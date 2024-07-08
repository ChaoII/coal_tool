import requests
import numpy as np

url = "http://127.0.0.1:8000/api/pointcloud/initial_point"
src_point = np.loadtxt("normalize.txt", delimiter=" ")
json = dict(
    src_point=src_point.tolist(),
    coal_weights=[3, 2, 1]
)
response = requests.post(url=url, json=json).json()
src_point = response["data"]["src_point"]
split_points = response["data"]["split_points"]

np.savetxt("initial_point_response_file/src_point.txt", np.array(src_point), "%.4f", " ")

for index, split_point in enumerate(split_points):
    np.savetxt(f"initial_point_response_file/split_point_{index}.txt", np.array(split_point), "%.4f", " ")
