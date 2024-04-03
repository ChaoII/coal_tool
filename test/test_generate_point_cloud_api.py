import requests

url = "http://127.0.0.1:8000/api/pointcloud/generate_point_cloud"

data = dict(
    x_min=0,
    x_max=270,
    y_min=0,
    y_max=50,
    delimiter=" ",
    density=0.5,
    nearest_k=50
)

f = open("n.txt", "r")

files = dict(
    src_pc_file=f
)

response = requests.post(url=url, data=data, files=files)

f.close()

print(response.json())
