import math
from typing import List, Tuple

def normalize(matrix: List[List[float]], n: int, m: int) -> List[List[float]]:
    """
    Normalizes the decision matrix.
    """
    normalized_matrix = [[0] * m for _ in range(n)]
    for j in range(m):
        column_sum = math.sqrt(sum(matrix[i][j] ** 2 for i in range(n)))
        for i in range(n):
            normalized_matrix[i][j] = matrix[i][j] / column_sum if column_sum else 0
    return normalized_matrix

def weighted_normalize(matrix: List[List[float]], n: int, m: int, weights: List[float]) -> List[List[float]]:
    """
    Performs weighted normalization of the decision matrix.
    """
    weighted_matrix = [[0] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            weighted_matrix[i][j] = matrix[i][j] * weights[j]
    return weighted_matrix

def calculate_ideal_solutions(matrix: List[List[float]], n: int, m: int, impact: List[int]) -> Tuple[List[float], List[float]]:
    """
    Calculates the ideal best (f*) and ideal worst (f-) solutions.
    """
    ideal_best = [0] * m
    ideal_worst = [0] * m
    for j in range(m):
        if impact[j] == 1:
            ideal_best[j] = max(matrix[i][j] for i in range(n))
            ideal_worst[j] = min(matrix[i][j] for i in range(n))
        else:
            ideal_best[j] = min(matrix[i][j] for i in range(n))
            ideal_worst[j] = max(matrix[i][j] for i in range(n))
    return ideal_best, ideal_worst

def calculate_si_ri(matrix: List[List[float]], n: int, m: int, ideal_best: List[float], ideal_worst: List[float]) -> Tuple[List[float], List[float]]:
    """
    Calculates the Si (utility measure) and Ri (regret measure) for each alternative.
    """
    Si = [0] * n
    Ri = [0] * n
    for i in range(n):
        for j in range(m):
            # Check for division by zero
            if ideal_best[j] == ideal_worst[j]:
                continue  # Skip this criterion as it doesn't differentiate alternatives
            
            # Calculate the normalized difference
            normalized_diff = (ideal_best[j] - matrix[i][j]) / (ideal_best[j] - ideal_worst[j])
            Si[i] += normalized_diff
            Ri[i] = max(Ri[i], normalized_diff)
    return Si, Ri


def calculate_qi(Si: List[float], Ri: List[float], n: int, v: float) -> List[float]:
    """
    Calculates the Qi (VIKOR index) for each alternative.
    v is the weight of the strategy of 'the majority of criteria' (typically v = 0.5).
    """
    S_min, S_max = min(Si), max(Si)
    R_min, R_max = min(Ri), max(Ri)
    
    Qi = [0] * n
    for i in range(n):
        if S_max == S_min:
            S_term = 0  # Assign 0 if all Si values are equal to avoid division by zero
        else:
            S_term = (Si[i] - S_min) / (S_max - S_min)
        
        if R_max == R_min:
            R_term = 0  # Assign 0 if all Ri values are equal to avoid division by zero
        else:
            R_term = (Ri[i] - R_min) / (R_max - R_min)
        
        Qi[i] = v * S_term + (1 - v) * R_term
    
    return Qi


def vikor(all_ratings: List[List[float]], n: int, m: int, weights: List[float], impact: List[int], v: float = 0.5) -> List[float]:
    """
    Performs VIKOR analysis on the decision matrix.
    n is the number of alternatives.
    m is the number of attributes.
    impact specifies the positive or negative effect of attributes (1 for benefit, 0 for cost).
    weight defines the weight of attributes.
    v is the weight of the strategy of 'the majority of criteria'.
    """
    normalized_matrix = normalize(all_ratings, n, m)
    weighted_normalized_matrix = weighted_normalize(normalized_matrix, n, m, weights)
    ideal_best, ideal_worst = calculate_ideal_solutions(weighted_normalized_matrix, n, m, impact)
    Si, Ri = calculate_si_ri(weighted_normalized_matrix, n, m, ideal_best, ideal_worst)
    Qi = calculate_qi(Si, Ri, n, v)
    
    return Qi

# Example usage:
# all_ratings = [[...], [...], ...]
# weights = [...]
# impact = [...]
# vikor_scores = vikor(all_ratings, len(all_ratings), len(all_ratings[0]), weights, impact)
