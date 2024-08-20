
descriptions = {
    'z': 'Main objective function',
    'z1': 'Objective function 1: Minimizing handover costs',
    'z11': 'First summation value of Objective function 1 value',
    'z12': 'Second summation value of Objective function 1 value',
    'z13': 'Third summation value of Objective function 1 value',
    'z14': 'Fourth summation value of Objective function 1 value',
    'z2': 'Objective function 2: Minimizing the distance between nodes and their corresponding APs',
    'z3': 'Objective function 3: Minimizing the count of active APs',
    'z4': 'Objective function 4: Maximizing load balancing',
    'z5': 'Objective function 5: Minimizing Disconnected Nodes',
    'Re_B': 'Remaining bandwidth of access points over time',
    'Es_Con': 'Establishment of connection between access points at specific times',
    'Es_Dis': 'Establishment of disconnection between access points at specific times',
    'Ha_Fr_To': 'Handover from one access point to another for a node at a given time',
    'Co': 'Connections between access points and nodes over time',
    'Onoff': 'Status of access points over time (1: active, 0: inactive)'
}
def print_optimal_values(optimal_values):
    for key, value in reversed(list(optimal_values.items())):
        print(f"{descriptions.get(key, key)}:")
        if isinstance(value, dict):
            
            for subkey, subvalue in value.items():
                print(f"  {subkey}: {subvalue}")
        else:
            print(f"{key}: {value}")


def is_empty_matrix(matrix):
    if not isinstance(matrix, list):
        return False
    for item in matrix:
        if isinstance(item, list):
            if not is_empty_matrix(item):
                return False
        else:
            return False
    return True

def remove_zero_rows(matrix, ap_id):
    
    indices_to_remove = [i for i, row in enumerate(matrix) if isinstance(row, (list, tuple)) and all(x == 0 for x in row)]

    # Remove corresponding items from matrix and ap
    for index in sorted(indices_to_remove, reverse=True):
        del matrix[index]
        del ap_id[index]
    return matrix, ap_id