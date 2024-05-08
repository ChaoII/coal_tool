import requests

url = "http://127.0.0.1:8000/api/pointcloud/download_file"

data = dict(
    file_marker="20240508",
    file_name="20240508102700ca0f19ed87d54d72b1d201c9b64e65aa"
)

response = requests.post(url=url, json=data)
with open("c_dst.txt", "w+",encoding="utf8") as code:
    code.write(response.content.decode())

print(response.status_code)

