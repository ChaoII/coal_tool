import os
import numpy as np


def get_split_points(point_path: str):
    split_points = []
    for root, dir_name, files in os.walk(point_path):
        for file in files:
            if file.startswith("split_point"):
                file_path = os.path.join(root, file)
                split_point = np.loadtxt(file_path, delimiter=" ")
                split_points.append(split_point.tolist())
    return split_points
