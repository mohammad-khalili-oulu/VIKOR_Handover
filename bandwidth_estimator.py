import math
import numpy as np
from constants import *



def calculate_radio_RSINR(distance, ap_max_bandwidth):
    """
    Calculates Radio RSINR (Equation 12).
    """
    large_scale_fading_loss = 20 * math.log10(distance) + 20 * math.log10(FREQUENCY_GHZ) + 32.4
    interference_sum = 0
    channel_gain = H0 * math.sqrt(10 ** (-large_scale_fading_loss / 10))
    RSINR = channel_gain * RADIO_P_TX / (ap_max_bandwidth * RADIO_NOISE_0 + interference_sum)
    return RSINR, channel_gain



def calculate_radio_LOS_channel_gain(distance, ap_coverage_radius, ap_max_bandwidth, N_connected):
    """
    Calculates Radio Line-of-Sight (LOS) channel gain.
    """
    
    if distance > ap_coverage_radius:
        return 0, 0, 0

    RSINR, channel_gain_r = calculate_radio_RSINR(distance, ap_max_bandwidth)
    if N_connected == 0:
        N_connected = 1
    Radio_Bandwidth = zeta * ap_max_bandwidth * math.log2(1 + RSINR) / N_connected
    return Radio_Bandwidth, channel_gain_r, RSINR






def calculate_optical_LOS_channel_gain(distance, node_pos, node_mu2, node_mu3, ap_coverage_radius, ap_pos, ap_max_bandwidth, N_connected):
    """
    Calculates Optical Line-of-Sight (LOS) channel gain.
    """
    
    if distance > ap_coverage_radius:
        return 0, 0, 0

    phi = compute_varphi(ap_pos, node_pos)
    Mu = calculate_mus(node_mu2, node_mu3)
    psi = compute_psi(node_pos, ap_pos, Mu)

    m_lambda =  -np.log10(2) / np.log10(np.cos(np.deg2rad(PHI_HALF)))  # Lambertian order of emission
    G_Con = (ETA ** 2) / np.sin(FOV)  # gain of an optical concentrator
    cosphi_A1 = ap_pos[2] - node_pos[2]  / distance  # angle vector

    channel_gain_OG = (m_lambda + 1) * SENSOR_AREA * cosphi_A1 ** (m_lambda + 1) / (2 * np.pi * distance ** 2)  # channel DC gain for source 1
    P_rec = OPTICAL_P_TX * channel_gain_OG * G_OF * G_Con  # received power from source 1
    
    
    interference_sum = 0
    OSINR = P_rec / (ap_max_bandwidth * OPTICAL_NOISE_0 + interference_sum)
    if N_connected == 0:
        N_connected = 1
    Optical_Bandwidth = zeta * ap_max_bandwidth * math.log2(1 + OSINR) / N_connected
    #print(Optical_Bandwidth)
    return Optical_Bandwidth, channel_gain_OG, OSINR



def compute_varphi(node_pos, ap_pos):
    """
    Computes the angle varphi.
    """
    node_pos = np.array(node_pos)
    ap_pos = np.array(ap_pos)
    numerator = np.dot(node_pos - ap_pos, VECTOR_TO_LIGHT)
    denominator = np.linalg.norm(node_pos - ap_pos)
    varphi = np.degrees(np.arccos(numerator / denominator))
    return varphi


def compute_psi(node_pos, ap_pos, Mu):
    """
    Computes the angle psi.
    """
    node_pos = np.array(node_pos)
    ap_pos = np.array(ap_pos)
    numerator = np.dot(node_pos - ap_pos, Mu)
    denominator = np.linalg.norm(node_pos - ap_pos)
    psi = np.degrees(np.arccos(numerator / denominator))
    return psi



def calculate_mus(mu2, mu3):
    """
    Computes the normal vector to the user device's surface.
    """
    return np.array([np.cos(mu3) * np.sin(mu2),
                     np.sin(mu3) * np.sin(mu2),
                     np.cos(mu2)])

