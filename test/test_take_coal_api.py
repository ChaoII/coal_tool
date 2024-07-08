import os

import requests
import numpy as np

from utils import get_split_points

url = "http://127.0.0.1:8000/api/pointcloud/take_coal"

src_point = np.loadtxt("initial_point_response_file/src_point.txt", delimiter=" ")
split_points = get_split_points("./initial_point_response_file")

json = dict(
    src_point=src_point.tolist(),
    split_points=split_points,
    coal_weight=30000,
    process_xrange=[30, 50],
    process_yrange=[0, 50],
    coal_density=1.25,
    x_edge_rate=0.4,
    x_sections=10,
)

response = requests.post(url=url, json=json).json()
src_point = response["data"]["src_point"]
split_points = response["data"]["split_points"]

np.savetxt("take_coal_response_file/src_point.txt", np.array(src_point), "%.4f", " ")

for index, split_point in enumerate(split_points):
    np.savetxt(f"take_coal_response_file/split_point_{index}.txt", np.array(split_point), "%.4f", " ")
