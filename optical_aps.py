from utils import *
from accesspoint import *




class OpticalAPs(AccessPoint):
    def __init__(self, id, x, y, z, coverage_radius, max_bandwidth,max_con):
        super().__init__('oa' + str(id), x, y, z, 'OAP', coverage_radius, max_bandwidth,max_con)
        
    


