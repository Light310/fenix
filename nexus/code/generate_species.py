import random
import numpy as np

basic_position = [0, 0, 0, 0,
                  0, 0, 0, 0,
                  0, 0, 0, 0,
                  0, 0, 0, 0]


def generate_species():
    mutation = [0 for i in range(16)]

    for i in range(16):
        rnd = random.randint(1, 100)
        if rnd > 85:
            mutation[i] = -1
        elif rnd > 70:
            mutation[i] = 1

    #print(mutation)

    mutated_position = np.array(basic_position) + 30*np.array(mutation)
    print(mutated_position)
    return mutated_position

for i in range(5):
    generate_species()