import numpy as np


ENV_SIZE  = (10, 10, 3) #env_size_x, env_size_y, env_size_z

MAX_OAP_RANGE  = 8
MAX_RAP_RANGE  = 200



#Bandwidth 
maxbandwidth_optical = 500
maxbandwidth_radio = 100
max_con_op = 10
max_con_r = 10
zeta = 1

Max_Con_optical =10
Max_Con_radio = 10
mu2 = 0
mu3 = 0
N_connected = 1




# Constants for radio 
FREQUENCY_GHZ = 2.4  # Example frequency in GHz
RADIO_NOISE_0 = 0.0001
RADIO_P_TX = 100
H0 = 2.5



# Constants for optical
PHI_HALF = 70
PSI_FIELD_OF_VIEW = 170
SENSOR_AREA = 1e-4  # detector physical area of a PD
G_OF = 1  # Gain associated with the optical filter employed at the receiver   # gain of an optical filter; ignore if no filter is used
ETA = 1.5  # refractive index of a lens at a PD; ignore if no lens is used
VECTOR_TO_LIGHT = np.array([0, 0, 1])
KAPPA = 1
OPTICAL_P_TX = 20  # transmitted optical power by individual LED
OPTICAL_NOISE_0 = 0.000001

FOV = 60 * np.pi / 180  # FOV of a receiver



Fized_cost =10
        
Var_cost = 5