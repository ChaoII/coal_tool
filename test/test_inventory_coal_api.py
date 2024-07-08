import requests
import numpy as np

from utils import get_split_points

url = "http://127.0.0.1:8000/api/pointcloud/inventory_coal"
new_point = np.loadtxt("normalize.txt", delimiter=" ")

split_points = get_split_points("./initial_point_response_file")

json = dict(
    new_point=new_point.tolist(),
    split_points=split_points
)

response = requests.post(url=url, json=json).json()
src_point = response["data"]["src_point"]
split_points = response["data"]["split_points"]

np.savetxt("inventory_coal_response_file/src_point.txt", np.array(src_point), "%.4f", " ")

for index, split_point in enumerate(split_points):
    np.savetxt(f"inventory_coal_response_file/split_point_{index}.txt", np.array(split_point), "%.4f", " ")
