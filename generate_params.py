
import random
import math
from bandwidth_estimator import calculate_radio_LOS_channel_gain, calculate_optical_LOS_channel_gain
from constants import *


def generate_random_params(N_I,N_R,N_O,N_T):
    N_A = N_O + N_R
    
    parameters_values = {
        
        'mu2': mu2,
        'mu3': mu3,
        'Maxconnections': {},
        'ENV_SIZE': ENV_SIZE,
        'MAX_OAP_RANGE': MAX_OAP_RANGE,
        'MAX_RAP_RANGE': MAX_RAP_RANGE,
        'maxbandwidth_init': {},
        'Rb_init': {},
        'achievable_bandwidth': {},
        'Max_Con_init': {},
        'Dist':{},
        'Start_Positions': {},
        'Stop_Positions': {},
        'Nodes_Positions': {},
        'aps_positions': {},
        'Coverage':{}
    }
    
    sets_count = {
        'N_T': N_T,
        'N_I': N_I,
        'N_O': N_O,
        'N_R': N_R,
        'N_A': N_A,
    }
    
    
    
    Min_RQ_B_Nodes = 9
    Max_RQ_B_Nodes = 10

    for i in range(N_I):
        for t in range(N_T):        
            parameters_values['Rb_init'][f'i{i+1}', f't{t+1}'] = random.randint(Min_RQ_B_Nodes, Max_RQ_B_Nodes) 

    Distances,  nodes_positions, aps_positions, nodes = generate_random_positions(N_I, N_O, N_R, N_T)
    #print(aps_positions)
    #print( N_O, N_R)

    for ap in range(N_O):
        parameters_values['maxbandwidth_init'][f'oa{ap+1}'] = maxbandwidth_optical
        parameters_values['Max_Con_init'][f'oa{ap+1}'] = Max_Con_optical
        parameters_values['aps_positions'][f'oa{ap+1}'] = aps_positions[ap]
        parameters_values['Maxconnections'][f'oa{ap+1}'] = max_con_op

    for ap in range(N_O,N_A):
        parameters_values['maxbandwidth_init'][f'ra{ap+1}'] = maxbandwidth_radio
        parameters_values['Max_Con_init'][f'ra{ap+1}'] = Max_Con_radio
        parameters_values['aps_positions'][f'ra{ap+1}'] = aps_positions[ap]
        parameters_values['Maxconnections'][f'ra{ap+1}'] = max_con_r
    
    

    
    #achievable_bandwidth = calculate_achievable_bandwidth(Distances,Coverage, zeta)
    
    for i in range(N_I):
        parameters_values['Start_Positions'][f'i{i+1}'] = nodes[i][0]
        parameters_values['Stop_Positions'][f'i{i+1}'] = nodes[i][1]
        for t in range(N_T):
            parameters_values['Nodes_Positions'][f'i{i+1}', f't{t+1}'] = nodes_positions[i][t]
            #print(f'i{i+1}', f't{t+1}',nodes_positions[i][t])
            for ap in range(N_O):
                parameters_values['Dist'][f'oa{ap+1}', f'i{i+1}', f't{t+1}'] = Distances[t][i][ap]
                #print(f'oa{ap+1}', f'i{i+1}', f't{t+1}',Distances[t][i][ap])
                #parameters_values['achievable_bandwidth'][f'oa{ap+1}', f'i{i+1}', f't{t+1}'] = achievable_bandwidth[t][i][ap]

                bandwidth,_,_ = calculate_optical_LOS_channel_gain(Distances[t][i][ap],nodes_positions[i][t],mu2, mu3,MAX_OAP_RANGE,aps_positions[ap],maxbandwidth_optical,N_connected)
                parameters_values['achievable_bandwidth'][f'oa{ap+1}', f'i{i+1}', f't{t+1}'] = bandwidth
                
                if bandwidth == 0:
                    parameters_values['Coverage'][f'oa{ap+1}', f'i{i+1}', f't{t+1}'] = 0
                else:
                    parameters_values['Coverage'][f'oa{ap+1}', f'i{i+1}', f't{t+1}'] = 1
                
            for ap in range(N_O,N_A):
                parameters_values['Dist'][f'ra{ap+1}', f'i{i+1}', f't{t+1}'] = Distances[t][i][ap]
                #parameters_values['achievable_bandwidth'][f'ra{ap+1}', f'i{i+1}', f't{t+1}'] = achievable_bandwidth[t][i][ap]
                bandwidth,_,_ = calculate_radio_LOS_channel_gain(Distances[t][i][ap],MAX_RAP_RANGE,maxbandwidth_radio,N_connected)
                parameters_values['achievable_bandwidth'][f'ra{ap+1}', f'i{i+1}', f't{t+1}']= bandwidth

                if bandwidth == 0:
                    parameters_values['Coverage'][f'ra{ap+1}', f'i{i+1}', f't{t+1}'] = 0
                else:
                    parameters_values['Coverage'][f'ra{ap+1}', f'i{i+1}', f't{t+1}'] = 1

    return parameters_values, sets_count






def generate_random_positions(num_nodes,  N_O, N_R, T):
    nodes = [((round(random.uniform(0, ENV_SIZE[0]), 2), round(random.uniform(0, ENV_SIZE[1]), 2),0),
              (round(random.uniform(0, ENV_SIZE[0]), 2), round(random.uniform(0, ENV_SIZE[1]), 2),0)) for _ in range(num_nodes)]

    opticalAPs = generate_grid_positions(N_O)
    radioAPs =  generate_grid_positions(N_R)
    #print(opticalAPs)
    #print(radioAPs)
    #APs = [(round(random.uniform(0, ENV_SIZE[0]), 2), round(random.uniform(0, ENV_SIZE[1]), 2),ENV_SIZE[2]) for _ in range(N_O+N_R)]
    #print(APs)
    #APs = []
    APs = opticalAPs + radioAPs
    #print(APs)
    nodes_positions = [[((node[0][0] + (node[1][0] - node[0][0]) * t / (T - 1)),
                         (node[0][1] + (node[1][1] - node[0][1]) * t / (T - 1)),0)
                        for t in range(T)] for node in nodes]

    distances_over_time = [[[round(math.sqrt((nodes_positions[i][t][0] - AP[0]) ** 2 + (nodes_positions[i][t][1] - AP[1]) ** 2+ (nodes_positions[i][t][2] - AP[2]) ** 2), 2)
                             for AP in APs]
                            for i in range(num_nodes)]
                           for t in range(T)]

    

    return distances_over_time,  nodes_positions, APs, nodes





def generate_grid_positions( num_positions):
    MAX_X, MAX_Y,z = ENV_SIZE[0], ENV_SIZE[1], ENV_SIZE[2]
    
    positions = []
    
    num_row = round(math.sqrt(num_positions))
    step_x = MAX_X / num_row
    num_col = num_positions // num_row
    step_y = MAX_Y / num_col
    
    for i in range(num_row):
        x = step_x / 2
        y = step_y / 2
        for j in range(num_col):
            positions.append((x, y, z))
            y += step_y
        x += step_x
    
    return positions


