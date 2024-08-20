
class AccessPoint:
    def __init__(self, ap_id, x, y, z, ap_type, coverage_radius, max_bandwidth, max_connections):
        """
        Initializes an AccessPoint object with given parameters.
        """
        self.ap_id = ap_id
        self.x = x
        self.y = y
        self.z = z
        self.ap_type = ap_type
        self.coverage_radius = coverage_radius
        self.max_bandwidth = max_bandwidth
        self.free_bandwidth = max_bandwidth
        self.max_connections = max_connections
        self.N_connected = 0
        self.connected_nodes = []
        self.bandwidth_changes = {}
        self.used_bandwidth_changes = {}

    def store_bandwidth_changes(self, time_step):
        """
        Stores changes in bandwidth for a given time step.
        """
        self.bandwidth_changes[f't{time_step+1}'] = self.free_bandwidth
        self.used_bandwidth_changes[f't{time_step+1}'] = self.max_bandwidth - self.free_bandwidth

    def connect_node_to_ap(self, node_required_bandwidth, time_step, node_id):
        """
        Connects a node to the access point.
        """
        self.free_bandwidth -= node_required_bandwidth
        self.connected_nodes.append(node_id)
        if self.free_bandwidth < 0:
            self.free_bandwidth = 0
            self.store_bandwidth_changes(time_step)
            return False
        else:
            self.store_bandwidth_changes(time_step)
            return True

    def disconnect_node_from_ap(self, node_required_bandwidth, time_step, node_id):
        """
        Disconnects a node from the access point.
        """
        self.free_bandwidth += node_required_bandwidth
        self.store_bandwidth_changes(time_step)
        if node_id in self.connected_nodes:
            self.connected_nodes.remove(node_id)
        else:
            raise ValueError(f"AP: {self.ap_id} - The node with ID '{node_id}' is not connected but wants to release!{self.connected_nodes}")

    

    def get_location(self):
        """
        Returns the location of the access point.
        """
        return self.x, self.y, self.z

    
        