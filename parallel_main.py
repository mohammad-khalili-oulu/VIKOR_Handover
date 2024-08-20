
import time
import multiprocessing
import logging
from write2csv import *

from generate_params import *
from utils import *
from decentral_fun import *
from collect_staticstics import *
from greedy_alg import *


# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')



# Example usage


num_process = 2


def run_iteration(args):
    N_I, N_O, N_R, N_T, count, forecast_horizon = args
    
    parameters_values, sets_count = generate_random_params(N_I, N_R, N_O, N_T)
    
    
    
    start_time2 = time.time()
    results, used_bandwidth, available_bandwidth = decentral_fun(sets_count, parameters_values,forecast_horizon)
    end_time2 = time.time()
    execution_time2 = end_time2 - start_time2
    logging.info(f"N_I={N_I}, N_O={N_O}, N_R={N_R}, N_T={N_T}, count={count}, VIKOR, Execution time: {execution_time2:.6f} seconds")

    results_g, used_bandwidth_g, available_bandwidth_g = greedy_alg(sets_count, parameters_values,forecast_horizon)
    
    collect_stat_and_store(results, used_bandwidth, available_bandwidth, execution_time2, parameters_values, N_I, N_O, N_R, N_T, count,forecast_horizon,results_g, used_bandwidth_g, available_bandwidth_g)
    
    


def main():
    N_Is = list(range(1, 2))
    N_Os = [4,9]
    N_Rs = [2,4]
    N_Ts = list(range(5, 6))
    forecast_horizons  = list(range(2, 3))
    n_repeat = 5

    
    

    # Create a multiprocessing pool before the loop
    pool = multiprocessing.Pool(processes = num_process)

    # Define a list of arguments for run_iteration
    args_list = [(N_I, N_O, N_R, N_T,count,forecast_horizon)
                 for N_I in N_Is
                 for N_O in N_Os
                 for N_R in N_Rs
                 for N_T in N_Ts
                 for count in range(n_repeat)
                 for forecast_horizon in forecast_horizons]

    # Use pool.map to execute run_iteration in parallel
    pool.map(run_iteration, args_list)

    # Close the pool and wait for all processes to finish
    pool.close()
    pool.join()
    
    
if __name__ == "__main__":
    main()
    
