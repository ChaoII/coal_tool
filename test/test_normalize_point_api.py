import requests
import numpy as np

url = "http://127.0.0.1:8000/api/pointcloud/normalize_point"

src_point = np.loadtxt("n.txt", delimiter=" ")

json = dict(
    src_point=src_point.tolist(),
    x_range=[0, 300],
    y_range=[0, 50],
    density=0.5,
    nearest_k=50,
    down_sample_size=0
)

response = requests.post(url=url, json=json)
dst_point = response.json()["data"]["dst_point"]
np.savetxt("normalize.txt", np.array(dst_point), "%.4f", " ")
