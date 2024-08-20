import os
import csv
import multiprocessing

# Create a Lock object for file access
file_lock = multiprocessing.Lock()

def ensure_directory_exists(directory='csvs'):
    if not os.path.exists(directory):
        os.makedirs(directory)

def write_to_csv(csv_file_path, data):
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




def prepare_data_for_vikor(results, used_bandwidth, available_bandwidth):
    headers1 = ['Access Point', 'Time', 'Used Bandwidth', 'Remaining Bandwidth']
    headers2 = ['Access Point', 'Node', 'Time', 'Connections', 'Establish Connections', 'Disconnection']

    data = [headers1]
    for ap in used_bandwidth:
        for time in  used_bandwidth[ap].keys():
            data.append([ap,time,used_bandwidth[ap][time], available_bandwidth[ap][time]])
        
    
    # Initialize the main data list with appropriate headers
    data.append(headers2)
    zero_data = []
    Co_dict = results['Co']
    Es_Con_dict = results['Es_Con']
    Es_Dis_dict = results['Es_Dis']
    for node in Co_dict.keys():
        node_Co_dict = Co_dict[node]
        node_Es_Con_dict = Es_Con_dict[node]
        node_Es_Dis_dict = Es_Dis_dict[node]

        for (ap,time) in node_Co_dict.keys():
            key = (ap,time)
            co_value = node_Co_dict.get(key, 0)
            es_con_value = node_Es_Con_dict.get(key, 0)
            es_dis_value = node_Es_Dis_dict.get(key, 0)

            # Check if not all values are zero before appending to data
            if co_value != 0 or es_con_value != 0 or es_dis_value != 0:
                data.append([ap, node, time, co_value, es_con_value, es_dis_value])
            else:
                zero_data.append([ap, node, time, co_value, es_con_value, es_dis_value])
    
    #sorted_data = sorted(data[1:], key=lambda x: (x[0], int(x[1][1:]), x[2]))
    #sorted_data.insert(0, headers2)  # Reinsert headers at the beginning
    data.append([])
    return data,zero_data

    



def collect_and_store_data_vikor(results, used_bandwidth, available_bandwidth, execution_time2, N_I, N_O, N_R, N_T, count):
    """Collect data from results and store it in a CSV file."""
    csv_data,zero_data = prepare_data_for_vikor(results, used_bandwidth, available_bandwidth)
    csv_file_name = f'vikor_csv_N_I={N_I}_N_O={N_O}_N_R={N_R}_N_T={N_T}.csv'
    # Write execution time to the CSV file
    write_to_csv(csv_file_name, ['Execution Time:', round(execution_time2,4)])
    write_to_csv(csv_file_name, ['Count:', count])
    # Write all prepared data to the CSV file
    write_to_csv(csv_file_name, csv_data)
    write_to_csv(csv_file_name, ['Zero data:'])
    write_to_csv(csv_file_name, zero_data)