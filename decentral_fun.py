
from accesspoint import *
from radio_aps import *
from node import *
from optical_aps import *
from threading import Thread, Lock


def node_process_collaborative(node, shared_state, lock):
    # Node processes using the shared state
    Co, Es_Con, Es_Dis = node.node_process(shared_state['APs'], shared_state['parameters_values'])
    
    with lock:
        # Update shared state with the results
        shared_state['results'].append((node.node_id, Co, Es_Con, Es_Dis))

def decentral_fun(sets_count, parameters_values, forecast_horizon):
    """
    Perform decentralized processing.
    """
    # Initialize APs and Nodes
    N_I = sets_count['N_I']
    N_T = sets_count['N_T']
    N_O = sets_count['N_O']
    N_R = sets_count['N_R']
    N_A = sets_count['N_A']

    APs = create_APs(N_A, N_O, parameters_values)
    Nodes = create_nodes(N_I, N_T, parameters_values, forecast_horizon)

    # Shared state
    shared_state = {
        'APs': APs,
        'parameters_values': parameters_values,
        'results': []
    }
    lock = Lock()

    # Start threads for each node
    threads = []
    for node in Nodes:
        t = Thread(target=node_process_collaborative, args=(node, shared_state, lock))
        t.start()
        threads.append(t)

    # Join threads
    for t in threads:
        t.join()

    # Process results
    results = {'Co': {}, 'Es_Con': {}, 'Es_Dis': {}}
    for node_id, Co, Es_Con, Es_Dis in shared_state['results']:
        results['Co'][node_id] = Co
        results['Es_Con'][node_id] = Es_Con
        results['Es_Dis'][node_id] = Es_Dis

    # Prepare bandwidth data
    used_bandwidth = {ap.ap_id: ap.used_bandwidth_changes for ap in APs}
    available_bandwidth = {ap.ap_id: ap.bandwidth_changes for ap in APs}

    return results, used_bandwidth, available_bandwidth



def create_APs(N_A, N_O, parameters_values):
    """
    Create access points based on provided parameters.
    """
    APs = []
    for oap in range(N_O):
        x_pos, y_pos, z = parameters_values['aps_positions'][f'oa{oap+1}']
        cr = parameters_values['MAX_OAP_RANGE']
        mb = parameters_values['maxbandwidth_init'][f'oa{oap+1}']
        AP = OpticalAPs(id=oap+1, x=x_pos, y=y_pos, z=z, coverage_radius=cr, max_bandwidth=mb, max_con=parameters_values['Maxconnections'][f'oa{oap+1}'])
        APs.append(AP)

    for rap in range(N_O, N_A):
        x_pos, y_pos, z_pos = parameters_values['aps_positions'][f'ra{rap+1}']
        cr = parameters_values['MAX_OAP_RANGE']
        mb = parameters_values['maxbandwidth_init'][f'ra{rap+1}']
        AP = RadioAPs(id=rap+1, x=x_pos, y=y_pos, z=z_pos, coverage_radius=cr, max_bandwidth=mb, max_con=parameters_values['Maxconnections'][f'ra{rap+1}'])
        APs.append(AP)

    return APs



def create_nodes(N_I, N_T, parameters_values, forecast_horizon):
    """
    Create nodes based on provided parameters.
    """
    nodes = []
    for i in range(N_I):
        start_positions = parameters_values['Start_Positions'][f'i{i+1}']
        stop_positions = parameters_values['Stop_Positions'][f'i{i+1}']
        node = Node(
            node_id=i+1,
            req_bandwidth=[parameters_values['Rb_init'][f'i{i+1}', f't{t+1}'] for t in range(N_T)],
            start_position=start_positions,
            stop_position=stop_positions,
            N_T=N_T,
            forecast_horizon=forecast_horizon,
            mu2=parameters_values['mu2'],
            mu3=parameters_values['mu3']
        )
        nodes.append(node)
    return nodes





