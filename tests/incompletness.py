import random
import time

# Function to simulate and count occurrences of 1 (True)
def measure_true_values(iterations=1000):
    count_true = 0
    for _ in range(iterations):
        # Randomly generate a True (1) or False (0)
        value = random.choice([0, 1])  # 0 is False, 1 is True
        if value == 1:
            count_true += 1
        time.sleep(0.01)  # To simulate time passing in between checks

    return count_true

# Run the simulation with 1000 iterations
iterations = 1000
result = measure_true_values(iterations)
print(f"Number of True values (1) in {iterations} iterations: {result}")
