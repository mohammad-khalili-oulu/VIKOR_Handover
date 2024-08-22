import numpy as np
import math
import logging
from vikor import vikor
from accesspoint import *
from radio_aps import *
from optical_aps import *
from bandwidth_estimator import *
from constants import *



class Node:
    def __init__(self, node_id, req_bandwidth,  start_position, stop_position, N_T, forecast_horizon, mu2, mu3):
        self.node_id = f'i{node_id}'
        self.req_bandwidth = req_bandwidth
        self.start_x, self.start_y,self.start_z = start_position
        self.stop_x, self.stop_y, self.stop_z = stop_position
        self.current_loc_x = start_position[0]
        self.current_loc_y = start_position[1]
        self.current_loc_z = start_position[2]
        self.prev_loc_x = None
        self.prev_loc_y = None
        self.prev_loc_z = None
        self.N_T = N_T
        self.mu2 = mu2
        self.mu3 = mu3
        self.forecast_horizon = forecast_horizon
        self.current_ap = None
        self.previous_handover_time = 0
        self.Co, self.Es_Con, self.Es_Dis, self.Ha_Fr_To = {}, {}, {}, {}
        self.not_connected_log = [] 
    
    def initilize_vars(self,APs):
        
        for t in range(self.N_T):
            for ap in APs:
                key = (ap.ap_id,  f"t{t+1}")
                self.Co[key] = self.Es_Con[key] = self.Es_Dis[key] = 0
                for apto in APs:
                    self.Ha_Fr_To[(ap, apto, f"t{t}")] = 0
            

        return 
    
    def node_process_greedy(self, APs, parameters_values):

        self.initilize_vars(APs)
        for t in range(self.N_T-1):
            new_loc = parameters_values['Nodes_Positions'][self.node_id, f't{t+1}']
            self.move_node(new_loc)
            node_loc = (self.current_loc_x, self.current_loc_y, self.current_loc_z)
            
            
            if self.current_ap is not None:
                dist = self.distance_to_AP(self.current_ap, node_loc)
                ap_pos = np.array([self.current_ap.x, self.current_ap.y, self.current_ap.z])
                bandwidth = self.comp_achievable_band(dist,new_loc,self.current_ap.coverage_radius,ap_pos,self.current_ap.max_bandwidth,self.current_ap.N_connected, self.current_ap.ap_type)
                if bandwidth >= self.req_bandwidth[t]:
                    self.stay_connected_with_current_APs(t)
                    continue
            best_ap = None
            dist = 100
            for ap in APs:
                d = self.distance_to_AP(ap, new_loc)
                if d <= ap.coverage_radius:
                    if d<dist:
                        dist =d
                        best_ap = ap
                    

            if best_ap is None:
                self.not_connected(t)
                
            else:
                self.handover(best_ap, t)
            #print('node:',self.node_id, 'time:',t, 'best AP',best_AP.ap_id)
            
            
        if self.current_ap is not None:    
            self.disconnect_from_current_AP(self.N_T)
        return self.Co,self.Es_Con,self.Es_Dis

    def node_process(self, APs, parameters_values):

        self.initilize_vars(APs)
        for t in range(self.N_T-1):
            new_loc = parameters_values['Nodes_Positions'][self.node_id, f't{t+1}']
            self.move_node(new_loc)

            next_positions = self.get_next_positions_Simple(t)
            
            available_APs = self.accessible_APs(APs)
            alternatives = []
            decision_matrix = []
            if not available_APs:
                self.not_connected(t)
                continue
            for ap in available_APs:
                alternatives.append(ap)
                #1) Handover costs (fixed, and type-dependent)
                f1_handover_cost = self.f1_handover_costs(ap,t,parameters_values)

                ban_dem_2_available = self.f2_ban_dem_2_available(ap,t,parameters_values)
                

                #2) Required bandwidth to achievable bandwidth Ratio for next $m$ position
                bandwidths_ratios = self.f3__achievable_bandwidth(ap,next_positions,t)
                
                




                row = f1_handover_cost + ban_dem_2_available + bandwidths_ratios 
                decision_matrix.append(row )
            num_alternatives = len(alternatives)
            
            num_attrs = len(row)
            weights =[1 for _ in range(num_attrs)]
            
            impact = [-1] * (len(f1_handover_cost) )  # Initialize with -1 for the length of f1_fuzzy_distances
            impact.extend([1] * ( len(ban_dem_2_available)+ len(bandwidths_ratios)))  # Append 1 for the length of f2_all_ban_ratio

            if len(impact) != len(row):
                print(len(impact) , len(row))
                print('ERROR')
            
            closeness = vikor(decision_matrix, num_alternatives, num_attrs, weights,impact)
            max_cc_index = np.argmax(closeness)
            best_AP = alternatives[max_cc_index]
            
            self.handover(best_AP, t)
            #print('node:',self.node_id, 'time:',t, 'best AP',best_AP.ap_id)
            
            
        if self.current_ap is not None:    
            self.disconnect_from_current_AP(self.N_T)
        return self.Co,self.Es_Con,self.Es_Dis

    def f3__achievable_bandwidth(self,ap,next_positions,t):
        bandwidths = []
        for next_position in next_positions:
            dist = self.distance_to_AP(ap, next_position)
            ap_pos = np.array([ap.x, ap.y, ap.z])
            bandwidth = self.comp_achievable_band(dist,next_position,ap.coverage_radius,ap_pos,ap.max_bandwidth,ap.N_connected, ap.ap_type)

            if bandwidth > 0:
                
                bandwidths.append(round(self.req_bandwidth[t-1]/bandwidth,2))
            else:
                bandwidths.append(0)
        return bandwidths
    
    def comp_achievable_band(self, dist,position,coverage_radius,ap_pos,max_bandwidth,N_connected, ap_type):
        if ap_type == "RAP":
            bandwidth, _, _ = calculate_radio_LOS_channel_gain(dist,coverage_radius,max_bandwidth,N_connected)
        else:
            
            bandwidth, _, _ = calculate_optical_LOS_channel_gain(dist,position,mu2, mu3, coverage_radius,ap_pos,max_bandwidth,N_connected)
        
        return bandwidth

        
    def f1_handover_costs(self,ap,t,parameters_values):
        cost = [0 for _ in range(min(self.forecast_horizon, self.N_T - t))]
        if self.current_ap is None:
            return cost
        if self.current_ap == ap:
            return cost
        
        
        for tau in range(min(self.forecast_horizon, self.N_T - t)):
            if t - self.previous_handover_time + tau >0:
                cost[tau] = Fized_cost + Var_cost/(t - self.previous_handover_time + tau)
            else:
                cost[tau] = Fized_cost + Var_cost
        
        return cost
        
    def f2_ban_dem_2_available(self,ap,t,parameters_values):
        ro =  [0 for _ in range(min(self.forecast_horizon, self.N_T - t))]
        for tau in range(min(self.forecast_horizon, self.N_T - t)):
            if t+tau < self.N_T:
                ro[tau] =  ap.free_bandwidth /ap.max_bandwidth
        return ro

    
    def get_next_positions_Simple(self,current_t):
    
        # Calculate node velocity based on current and next positions
        if current_t+1 == self.N_T:
            return (self.current_loc_x, self.current_loc_y)
        if self.prev_loc_x == None:
            return (0,0,0)
        x_velocity = self.current_loc_x - self.prev_loc_x
        y_velocity = self.current_loc_y - self.prev_loc_y
        next_positions = []
        # Predict next positions based on constant speed and direction
        for i in range(min(self.forecast_horizon+1, self.N_T - current_t)):
            new_pos = (self.current_loc_x + i * x_velocity, self.current_loc_y + i * y_velocity,self.current_loc_z)
            next_positions.append(new_pos)
        
        return next_positions

    def move_node(self,new_loc):
        if new_loc[0] ==  self.stop_x and new_loc[1] ==  self.stop_y :
            return
        self.prev_loc_x = self.current_loc_x
        self.prev_loc_y = self.current_loc_y
        self.current_loc_x = new_loc[0]
        self.current_loc_y = new_loc[1]

    def accessible_APs(self, APs):
        avaialanle_APs = []
        node_loc = (self.current_loc_x, self.current_loc_y, self.current_loc_z)
        for AP in APs:
            d = self.distance_to_AP(AP, node_loc)
            if d <= AP.coverage_radius:
                avaialanle_APs.append(AP)
        return avaialanle_APs
    
    
    
    def stay_connected_with_current_APs(self,time_step):
        self.Co[(self.current_ap.ap_id,  f"t{time_step}") ] = 1
        #logging.info(f'Node {self.node_id} stay connected with the AP {self.current_ap.ap_id} at time_step: {time_step}!')
        
    
    def distance_to_AP(self, AP, node_loc):
        AP_loc_x, AP_loc_y, AP_loc_z = AP.get_location()
        x = AP_loc_x - node_loc[0]
        y = AP_loc_y - node_loc[1]
        z = AP_loc_z - node_loc[2]
        dis = math.sqrt(x*x + y*y + z*z)
        dis = round(dis, 3)
        return dis
    
    def handover(self, next_ap, time_step):
        if self.current_ap is None:
            self.connect_to_AP(next_ap, time_step)
            return
        if self.current_ap.ap_id == next_ap.ap_id:
            self.stay_connected_with_current_APs(time_step)
            return
        
        self.disconnect_from_current_AP(time_step)
        self.connect_to_AP(next_ap, time_step)
        
    def connect_to_AP(self, next_ap, time_step):
        self.previous_handover_time = time_step
        self.current_ap = next_ap
        self.Co[(self.current_ap.ap_id,  f"t{time_step}") ] = 1
        self.Es_Con[(self.current_ap.ap_id,  f"t{time_step}") ] = 1
        #logging.info(f'Node {self.node_id}: The AP {self.current_ap.ap_id} at time_step: {time_step} is connected!')
        stat = self.current_ap.connect_node_to_ap(self.req_bandwidth[time_step-1],time_step,self.node_id)
        if not stat:
            raise ValueError(f"AP: {self.current_ap.ap_id} does not have sufficient bandwidth for the node with ID {self.node_id}")
            
    def disconnect_from_current_AP(self, time_step):
        self.Es_Dis[(self.current_ap.ap_id,  f"t{time_step}") ] = 1
        #logging.info(f'Node {self.node_id}: The AP {self.current_ap.ap_id} at time_step: {time_step} was released')
        self.current_ap.disconnect_node_from_ap(self.req_bandwidth[time_step-1],time_step,self.node_id)

            
    
    def not_connected(self, time_step):
        self.not_connected_log.append(time_step)
        self.current_ap = None
        logging.warning(f'Node {self.node_id} could not connect to any AP in time step {time_step}.!')

    
    

