from utils import *
from accesspoint import *



class RadioAPs(AccessPoint):
    def __init__(self, id, x, y, z, coverage_radius, max_bandwidth,max_con):

        super().__init__(f'ra{id}', x, y, z, 'RAP', coverage_radius, max_bandwidth,max_con)
        

    


    

    
    