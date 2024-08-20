
from generate_params import *
from utils import *
from write2csv import *
from decentral_fun import *
from collect_staticstics import *
from greedy_alg import *

forecast_horizon = 2


def run_approach(N_I, N_O, N_R, N_T):
    parameters_values, sets_count = generate_random_params(N_I, N_R, N_O, N_T)
    results, used_bandwidth, available_bandwidth = decentral_fun(sets_count, parameters_values,forecast_horizon)
    results_g, used_bandwidth_g, available_bandwidth_g = greedy_alg(sets_count, parameters_values,forecast_horizon)
    return parameters_values, results, used_bandwidth, available_bandwidth,results_g, used_bandwidth_g, available_bandwidth_g 




def main():
    N_I = 2
    N_O = 4
    N_R = 1
    N_T = 5
    

    

    
    parameters_values, results, used_bandwidth, available_bandwidth, results_g, used_bandwidth_g, available_bandwidth_g  = run_approach(N_I, N_O, N_R, N_T)
    

    collect_and_store_data_vikor(results, used_bandwidth, available_bandwidth, 0, N_I, N_O, N_R, N_T, 0)
    collect_stat_and_store(results, used_bandwidth, available_bandwidth, 0, parameters_values, N_I, N_O, N_R, N_T,0,forecast_horizon,results_g, used_bandwidth_g, available_bandwidth_g )
    


if __name__ == "__main__":
    main()

