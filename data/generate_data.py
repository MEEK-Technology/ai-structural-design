import random
import csv
from rules.beam_design import design_beam

def generate_dataset(num_samples=5000):
    dataset = []

    for _ in range(num_samples):
        span = round(random.uniform(3, 10), 2)   # meters
        load = round(random.uniform(10, 50), 2)  # kN/m
        fck = random.choice([20, 25, 30])        # concrete grade
        fy = 500                                 # steel grade

        result = design_beam(load, span, fy=fy)

        dataset.append([
            span,
            load,
            fck,
            fy,
            result["steel_area"]
        ])

    return dataset


def save_to_csv(data, filename="beam_dataset.csv"):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["span", "load", "fck", "fy", "steel_area"])
        writer.writerows(data)


if __name__ == "__main__":
    data = generate_dataset(5000)
    save_to_csv(data)
    print("Dataset generated successfully!")