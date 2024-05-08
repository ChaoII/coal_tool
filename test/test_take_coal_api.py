import requests

url = "http://127.0.0.1:8000/api/pointcloud/take_coal"

data = dict(
    coal_weight=30000,
    process_x_min=50,
    process_x_max=80,
    process_y_min=0,
    process_y_max=50,
    coal_density=2.7,
    new_index=None,
    x_edge_rate=0.4,
    x_sections=10,
    rebuild_point_cloud=True,
    x_min=0,
    x_max=270,
    y_min=0,
    y_max=50,
    delimiter=" ",
    density=0.5,
    nearest_k=50,
    down_sample_size=None
)

f = open("dst2.txt", "r")

files = dict(
    src_pc_file=f
)
response = requests.post(url=url, data=data, files=files)
f.close()

print(response.json())
