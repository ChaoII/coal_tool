import requests

url = "http://127.0.0.1:8000/api/pointcloud/download_file"

data = dict(
    file_marker="20240403",
    file_name="2024040316240357dc85bb96d6412095287264371b17ec"
)

response = requests.post(url=url, json=data)

print(response.status_code)
