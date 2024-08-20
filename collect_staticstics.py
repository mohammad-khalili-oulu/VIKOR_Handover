import os
import csv
import multiprocessing
import statistics
import math

# Create a Lock object for file access
file_lock = multiprocessing.Lock()

def ensure_directory_exists(directory='csvs'):
    if not os.path.exists(directory):
        os.makedirs(directory)

def write_stat_to_csv(csv_file_path, data):
    ensure_directory_exists()
    full_csv_path = os.path.join('csvs', csv_file_path)
    with file_lock, open(full_csv_path, mode='a', newline='') as csv_file:
        writer = csv.writer(csv_file, quoting=csv.QUOTE_MINIMAL)
        writer.writerows(data if isinstance(data[0], list) else [data])

def extract_numerical_part(value):
    if value[0]=='o':
        return int(value[2:])
    if value[0]=='r':
        return int(value[2:])
    return int(value[1:])


def time_to_int(time_str):
    return int(time_str[1:])


def durations(results):
    # Initialize dictionaries to store durations
    durations_oa = {}
    durations_ra = {}

    # Iterate over the results dictionary
    for category, nodes in results.items():
        for node, connections in nodes.items():
            for (obj, time), is_active in connections.items():
                if is_active == 1:
                    time_int = time_to_int(time)
                    if obj.startswith('oa'):
                        if obj not in durations_oa:
                            durations_oa[obj] = {'start': time_int, 'end': time_int}
                        else:
                            durations_oa[obj]['end'] = max(durations_oa[obj]['end'], time_int)
                    elif obj.startswith('ra'):
                        if obj not in durations_ra:
                            durations_ra[obj] = {'start': time_int, 'end': time_int}
                        else:
                            durations_ra[obj]['end'] = max(durations_ra[obj]['end'], time_int)

    # Calculate durations
    oa_durations = [durations_oa[obj]['end'] - durations_oa[obj]['start'] + 1 for obj in durations_oa]
    ra_durations = [durations_ra[obj]['end'] - durations_ra[obj]['start'] + 1 for obj in durations_ra]

    # Calculate average and standard deviation for 'oa' and 'ra' connections
    avg_oa_duration = statistics.mean(oa_durations) if oa_durations else 0
    std_dev_oa_duration = statistics.stdev(oa_durations) if len(oa_durations) > 1 else 0

    avg_ra_duration = statistics.mean(ra_durations) if ra_durations else 0
    std_dev_ra_duration = statistics.stdev(ra_durations) if len(ra_durations) > 1 else 0

    return avg_oa_duration, std_dev_oa_duration, avg_ra_duration, std_dev_ra_duration





def compute_distance(x1, y1, z1, x2, y2, z2):
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2)

def compute_distances(parameters):
    distances = {}
    nodes_positions = parameters['Nodes_Positions']
    aps_positions = parameters['aps_positions']
    for ap, ap_pos in aps_positions.items():
        posx, posy, posz = ap_pos
        for (node, time), node_pos in nodes_positions.items():
            posnx, posny, posnz = node_pos
            distance = compute_distance(posx, posy, posz, posnx, posny, posnz)
            distances[(ap, node, time)] = distance
    return distances

def distances(results, distances):
    # Initialize lists to store distances
    distances_oa = []
    distances_ra = []

    # Iterate over the results dictionary for the 'Es_Dis' category
    for node, connections in results['Es_Dis'].items():
        for (ap, time), is_active in connections.items():
            if is_active == 1:
                dist = distances.get((ap, node, time))
                if dist is not None:
                    if ap.startswith('oa'):
                        distances_oa.append(dist)
                    elif ap.startswith('ra'):
                        distances_ra.append(dist)

    # Calculate average and standard deviation for 'oa' and 'ra' connections
    avg_oa_distance = statistics.mean(distances_oa) if distances_oa else 0
    std_dev_oa_distance = statistics.stdev(distances_oa) if len(distances_oa) > 1 else 0

    avg_ra_distance = statistics.mean(distances_ra) if distances_ra else 0
    std_dev_ra_distance = statistics.stdev(distances_ra) if len(distances_ra) > 1 else 0

    return avg_oa_distance, std_dev_oa_distance, avg_ra_distance, std_dev_ra_distance

def handover_cost(results):
    # Initialize lists to store distances
    handover_oa = 0
    handover_ra = 0

    # Iterate over the results dictionary for the 'Es_Dis' category
    for node, connections in results['Es_Dis'].items():
        for (ap, time), is_active in connections.items():
            if is_active == 1:
                if ap.startswith('oa'):
                    handover_oa += 1
                elif ap.startswith('ra'):
                    handover_ra += 1

    

    return handover_oa, handover_ra

def collect_stat_and_store(results, used_bandwidth, available_bandwidth, execution_time,  parameters_values,  N_I, N_O, N_R, N_T, count,forecast_horizon, results_g, used_bandwidth_g, available_bandwidth_g ):
    # Sort AP and time values
    
    avg_oa_duration_vikor, std_dev_oa_duration_vikor, avg_ra_duration_vikor, std_dev_ra_duration_vikor = durations(results)
    avg_oa_duration_g, std_dev_oa_duration_g, avg_ra_duration_g, std_dev_ra_duration_g = durations(results_g)

    dis = compute_distances(parameters_values)
    avg_oa_distance_vikor, std_dev_oa_distance_vikor, avg_ra_distance_vikor, std_dev_ra_distance_vikor = distances(results, dis)
    avg_oa_distance_g, std_dev_oa_distance_g, avg_ra_distance_g, std_dev_ra_distance_g = distances(results_g, dis)

    hand_num_oa_vikor, hand_num_ra_vikor = handover_cost(results)
    hand_num_oa_greedy, hand_num_ra_greedy = handover_cost(results_g)
    
    # Prepare the data
    data_vikor = prepare_data_for_vikor(results, used_bandwidth, available_bandwidth)
    data_g = prepare_data_for_vikor(results_g, used_bandwidth_g, available_bandwidth_g)

    # Generate the CSV file name
    csv_file_name = f'stat_csv.csv'

    # Write execution time to the CSV file
    write_stat_to_csv(csv_file_name, ['Execution Time VIKOR:', round(execution_time/N_I,4)])
    write_stat_to_csv(csv_file_name, ['Count:', count])
    write_stat_to_csv(csv_file_name, ['Forecast Horizon:', forecast_horizon])
    write_stat_to_csv(csv_file_name, ['N_I:', N_I, 'N_O:', N_O,'N_R:', N_R, 'N_T:', N_T ])
    write_stat_to_csv(csv_file_name, ['Average duration of optical connections VIKOR:' , avg_oa_duration_vikor])
    write_stat_to_csv(csv_file_name, ['Standard deviation of Optical connections VIKOR:' ,std_dev_oa_duration_vikor])
    write_stat_to_csv(csv_file_name, ['Average duration of Radio connections VIKOR:' , avg_ra_duration_vikor])
    write_stat_to_csv(csv_file_name, ['Standard deviation of Radio connections VIKOR:' ,std_dev_ra_duration_vikor])

    write_stat_to_csv(csv_file_name, ['Average duration of optical connections GREEDY:' , avg_oa_duration_g])
    write_stat_to_csv(csv_file_name, ['Standard deviation of Optical connections GREEDY:' ,std_dev_oa_duration_g])
    write_stat_to_csv(csv_file_name, ['Average duration of Radio connections GREEDY:' , avg_ra_duration_g])
    write_stat_to_csv(csv_file_name, ['Standard deviation of Radio connections GREEDY:' ,std_dev_ra_duration_g])
    write_stat_to_csv(csv_file_name, ['VIKOR Distances', 'optical - Avg:', avg_oa_distance_vikor, 'Std Dev:', std_dev_oa_distance_vikor])
    write_stat_to_csv(csv_file_name, ['VIKOR Distances', 'Radio - Avg:', avg_ra_distance_vikor, 'Std Dev:', std_dev_ra_distance_vikor])

    write_stat_to_csv(csv_file_name, ['GREEDY Distances', 'optical - Avg:', avg_oa_distance_g, 'Std Dev:', std_dev_oa_distance_g])
    write_stat_to_csv(csv_file_name, ['GREEDY Distances', 'Radio - Avg:', avg_ra_distance_g, 'Std Dev:', std_dev_ra_distance_g])
    
    write_stat_to_csv(csv_file_name, ['VIKOR Handovers', 'optical:', hand_num_oa_vikor, 'Radio:', hand_num_ra_vikor])
    write_stat_to_csv(csv_file_name, ['GREEDY Handovers', 'optical:', hand_num_oa_greedy, 'Radio:', hand_num_ra_greedy])

    write_stat_to_csv(csv_file_name, ["Remain_Band VIKOR:",data_vikor])
    write_stat_to_csv(csv_file_name, ["Remain_Band GREEDY:",data_g])

    print(
    f"N_I: {N_I}, "
    f"N_O: {N_O}, "
    f"N_R: {N_R}, "
    f"N_T: {N_T}, "
    f"Count: {count}, "
    f"Forecast Horizon: {forecast_horizon}, "
    )
    print(
    f"Avg OA Duration (VIKOR): {avg_oa_duration_vikor:.2f}, "
    f"Std Dev OA Duration (VIKOR): {std_dev_oa_duration_vikor:.2f}, "
    f"Avg RA Duration (VIKOR): {avg_ra_duration_vikor:.2f}, "
    f"VIKOR Handovers, Optical {hand_num_oa_vikor:.2f},  Radio {hand_num_ra_vikor:.2f}, "
    f"Std Dev RA Duration (VIKOR): {std_dev_ra_duration_vikor:.2f}, "

    )
    print(
    f"Avg OA Duration (Greedy): {avg_oa_duration_g:.2f}, "
    f"Std Dev OA Duration (Greedy): {std_dev_oa_duration_g:.2f}, "
    f"Avg RA Duration (Greedy): {avg_ra_duration_g:.2f}, "
    f"Std Dev RA Duration (Greedy): {std_dev_ra_duration_g:.2f}"
    f"GREEDY Handovers, Optical {hand_num_oa_greedy:.2f},  Radio {hand_num_ra_greedy:.2f}, "
)



def prepare_data_for_vikor(results, used_bandwidth, available_bandwidth):
    #print(available_bandwidth)
    
    optical_bandwidths = []
    radio_bandwidths = []
    for key, value in available_bandwidth.items():
        if key.startswith('oa'):
            optical_bandwidths.extend(value.values())
        elif key.startswith('ra'):
            radio_bandwidths.extend(value.values())

    oa_std_dev = statistics.stdev(optical_bandwidths) if optical_bandwidths else None
    ra_std_dev = statistics.stdev(radio_bandwidths) if radio_bandwidths else None

    data = ['oa_std_dev', oa_std_dev]
    data += ['ra_std_dev', ra_std_dev]

    return data

    


