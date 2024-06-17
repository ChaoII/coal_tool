## 部署
### 1导入镜像
```bash
docker import pointcloud.tar pointcloud:v1.0
```
### 2运行容器
```bash
docker run -itd --name pc --restart always -w /app -v /etc/localtime:/etc/localtime -v /etc/timezone:/etc/timezone -p 9092:9092 pointcloud:v1.0 uvicorn main:app --host 0.0.0.0 --port 9092
```

## 接口文档

<details open>
  <summary style="font-size: 28px;font-weight: bold">generate_point_cloud</summary>

### 接口描述

对原始点云进行标准化，盘煤仪生成的点云可能由于种种原因存在缺点，破面等等问题，为满足需求，将点云进行标准化，重建一个点云模板，按照高度进行整理点云数据。

### 基本信息

- 接口名称：点云生成
- 接口URL：

```bash
http://127.0.0.1:8000/api/pointcloud/generate_point_cloud
```

- 请求方式: POST
- Content-Type： multipart/form-data

| 参数名              | 参数值  | 是否必填 | 参数类型    | 描述说明                                                |
|------------------|------|------|---------|-----------------------------------------------------|
| src_pc_file      | 文件路径 | 是    | 文件类型    | 必选参数-原始点云文件（由盘煤仪生成的点云）                              |
| x_min            | 0    | 是    | Integer | 可选参数-重建点云煤场的x最小值，默认0                                |
| x_max            | 270  | 是    | Integer | 可选参数-重建点云煤场的x最大值，默认270                              |
| y_min            | 0    | 是    | Integer | 可选参数-重建点云煤场的y最小值，默认0                                |
| y_max            | 50   | 是    | Integer | 可选参数-重建点云煤场的y最大值，默认50                               |
| delimiter        | 否    | 是	   | String  | 可选参数-点云数据分隔符，默认为" "(空格)                             |
| density          | 0.5  | 是    | 	Float  | 可选参数-煤场点云密度，默认0.5                                   |
| nearest_k        | 50   | 是	   | Integer | 可选参数-重构点云的精细程度，如果原始点云破面比较严重请增加该值，如果需要更精细，请降低该值，默认50 |
| down_sample_size | None | 是    | 	Float  | 	可选参数-下采样尺寸，值越大点云密度越低，默认None，不进行下采样（请谨慎使用）          |

### 响应示例

- 成功200

```json
{
  "code": 0,
  "data": {
    "file_marker": "20240508",
    "file_name": "2024050815225379e6e8d776194f6c80ba0fc246027b4c"
  },
  "err_msg": ""
}
```

- 失败404

```json
{
  "code": -1,
  "data": {},
  "err_msg": "点云重建失败"
}
```

</details>
<details open>
  <summary style="font-size: 28px;font-weight: bold">download_file</summary>

### 接口描述

在进行点云处理后，可以根据其他点云处理接口返回的文件参数，下载对应处理好的点云文件

### 基本信息

- 接口名称：下载点云文件
- 接口URL：

```bash
 http://127.0.0.1:8000/api/pointcloud/download_file
```

- 请求方式: POST
- Content-Type： application/json

### 请求参数

```json
{
  "file_marker": "20240508",
  "file_name": "20240508144137ab9de44ba44e4e01849ae71de19eb308"
}
```

</details>
<details open>
  <summary style="font-size: 28px;font-weight: bold">store_coal</summary>

### 接口描述

根据输入的参数，比如煤场的堆煤起始位置和终止位置，和堆煤重量，生成一个堆完煤的点云

### 基本信息

- 接口名称：点云生成
- 接口URL：

```bash
 http://127.0.0.1:8000/api/pointcloud/store_coal
```

- 请求方式: POST
- Content-Type： multipart/form-data

| 参数名                      | 参数值   | 是否必填 | 参数类型      | 描述说明                                                 |
|--------------------------|-------|------|-----------|------------------------------------------------------|
| src_pc_file              | 文件路径  | 是    | 文件类型      | 必选参数-原始点云文件（由盘煤仪生成的点云）                               |
| coal_weight	             | 50000 | 是    | 	Float    | 	必选参数-堆煤的重量                                          |
| process_x_min	           | 60    | 是	   | Integer   | 	必选参数-煤堆对方的x刻度最小值                                    |
| process_x_max            | 	 80  | 是    | 	Integer	 | 必选参数-煤堆对方的x刻度最大值                                     |
| process_y_min            | 2     | 否    | 	Integer  | 可选参数-煤堆对方的y刻度最小值，默认为点云y的最小值                          |
| process_y_max            | 48    | 否    | 	String   | 可选参数-煤堆对方的y刻度最大值，默认为点云y的最大值（注意，要么两参数同时不传，要么同时传）      |
| new_index                |       | 否    | 	Integer  | 可选参数-堆煤后新煤堆索引，默认为最大索引+1                              |
| coal_density             | 2.7   | 否	   | Float     | 可选参数-煤堆的密度，默认为2.7                                    |
| x_edge_rate              | 0.4   | 否    | 	Float    | 可选参数-边缘平滑率-默认0.4值越大边缘越平滑，越小越陡峭                       |
| x_sections               | 10    | 否    | 	Integer  | 可选参数-边缘分段-默认10，值越大边缘越平滑，越小越陡峭                        |
| rebuild_point_cloud true | true  | 否	   | Boolean   | 可选参数-是否重建点云，默认为true，如果为false后面的参数均可省略，重建点云会让点云更加合理正常 |
| x_min                    | 0     | 否    | 	Integer  | 可选参数-点云重建后的x最小值，必须与原始点云一致，默认0                        |
| x_max                    | 270   | 否    | 	Integer  | 可选参数-点云重建后的x最大值，必须与原始点云一致，默认270                      |
| y_min                    | 0     | 否    | 	Integer  | 可选参数-点云重建后的y最小值，默认0                                  |
| y_max                    | 50    | 否    | 	Integer  | 可选参数-点云重建后的y最大值，默认50                                 |
| delimiter                |       | 否    | 	String   | 可选参数-点云分隔符，默认" "(英文空格)                               |
| density                  | 0.5   | 否    | 	Float    | 可选参数点云重构的密度，默认0.5                                    |
| nearest_k                | 50    | 否    | 	Integer  | 可选参数-重构点云的精细程度，必须与原始点云的密度一致，不一致一定会报错                 |
| down_sample_size         |       | 否    | 	Float    | 可选参数-下采样尺寸，值越大点云密度越低，默认None，不进行下采样（请谨慎使用）            |

### 响应示例

- 成功200

```json
{
  "code": 0,
  "data": {
    "file_marker": "20240508",
    "file_name": "2024050815225379e6e8d776194f6c80ba0fc246027b4c"
  },
  "err_msg": ""
}
```

- 失败404

```json
{
  "code": -1,
  "data": {},
  "err_msg": "点云重建失败"
}
```

</details>
<details open>
  <summary style="font-size: 28px;font-weight: bold">take_coal</summary>

### 接口描述

根据输入的参数，比如煤场的堆煤起始位置和终止位置，和取煤重量，生成一个取完煤的点云

### 基本信息

- 接口名称：点云生成
- 接口URL：

```bash
 http://127.0.0.1:8000/api/pointcloud/take_coal
```

- 请求方式: POST
- Content-Type： multipart/form-data

| 参数名                      | 参数值   | 是否必填 | 参数类型      | 描述说明                                                 |
|--------------------------|-------|------|-----------|------------------------------------------------------|
| src_pc_file              | 文件路径  | 是    | 文件类型      | 必选参数-原始点云文件（由盘煤仪生成的点云）                               |
| coal_weight	             | 50000 | 是    | 	Float    | 	必选参数-堆煤的重量                                          |
| process_x_min	           | 60    | 是	   | Integer   | 	必选参数-煤堆对方的x刻度最小值                                    |
| process_x_max            | 	 80  | 是    | 	Integer	 | 必选参数-煤堆对方的x刻度最大值                                     |
| process_y_min            | 2     | 否    | 	Integer  | 可选参数-煤堆对方的y刻度最小值，默认为点云y的最小值                          |
| process_y_max            | 48    | 否    | 	String   | 可选参数-煤堆对方的y刻度最大值，默认为点云y的最大值（注意，要么两参数同时不传，要么同时传）      |
| new_index                |       | 否    | 	Integer  | 可选参数-堆煤后新煤堆索引，默认为最大索引+1                              |
| coal_density             | 2.7   | 否	   | Float     | 可选参数-煤堆的密度，默认为2.7                                    |
| x_edge_rate              | 0.4   | 否    | 	Float    | 可选参数-边缘平滑率-默认0.4值越大边缘越平滑，越小越陡峭                       |
| x_sections               | 10    | 否    | 	Integer  | 可选参数-边缘分段-默认10，值越大边缘越平滑，越小越陡峭                        |
| rebuild_point_cloud true | true  | 否	   | Boolean   | 可选参数-是否重建点云，默认为true，如果为false后面的参数均可省略，重建点云会让点云更加合理正常 |
| x_min                    | 0     | 否    | 	Integer  | 可选参数-点云重建后的x最小值，必须与原始点云一致，默认0                        |
| x_max                    | 270   | 否    | 	Integer  | 可选参数-点云重建后的x最大值，必须与原始点云一致，默认270                      |
| y_min                    | 0     | 否    | 	Integer  | 可选参数-点云重建后的y最小值，默认0                                  |
| y_max                    | 50    | 否    | 	Integer  | 可选参数-点云重建后的y最大值，默认50                                 |
| delimiter                |       | 否    | 	String   | 可选参数-点云分隔符，默认" "(英文空格)                               |
| density                  | 0.5   | 否    | 	Float    | 可选参数点云重构的密度，默认0.5                                    |
| nearest_k                | 50    | 否    | 	Integer  | 可选参数-重构点云的精细程度，必须与原始点云的密度一致，不一致一定会报错                 |
| down_sample_size         |       | 否    | 	Float    | 可选参数-下采样尺寸，值越大点云密度越低，默认None，不进行下采样（请谨慎使用）            |

### 响应示例

- 成功200

```json
{
  "code": 0,
  "data": {
    "file_marker": "20240508",
    "file_name": "2024050815225379e6e8d776194f6c80ba0fc246027b4c"
  },
  "err_msg": ""
}
```

- 失败404

```json
{
  "code": -1,
  "data": {},
  "err_msg": "点云重建失败"
}
```

</details>
