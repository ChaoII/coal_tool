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
  <summary style="font-size: 28px;font-weight: bold">normalize_point</summary>

### 接口描述

对原始点云进行标准化，盘煤仪生成的点云可能由于种种原因存在缺点，破面等等问题，为满足需求，将点云进行标准化，重建一个点云模板，按照高度进行整理点云数据。

### 基本信息

- 接口名称：点云生成
- 接口URL：

```bash
http://127.0.0.1:8000/api/pointcloud/normalize_point
```

- 请求方式: POST
- Content-Type： application/json

| 参数名              | 参数值       | 是否必填 | 参数类型    | 描述说明                                                |
|------------------|-----------|------|---------|-----------------------------------------------------|
| src_point        | [[0,1..]] | 是    | List    | 必选参数-原始点云文件（由盘煤仪生成的点云），为一个二维数组                      |
| x_range          | [0,300]   | 是    | List    | 可选参数-重建点云煤场的x坐标的范围，默认[0,300]                        |
| y_range          | [0,50]    | 是    | Lst     | 可选参数-重建点云煤场的y坐标的范围，默认[0,50]                         |
| density          | 0.5       | 是    | 	Float  | 可选参数-煤场点云密度，默认0.5,每隔0.5米生成一个点                       |
| nearest_k        | 50        | 是	   | Integer | 可选参数-重构点云的精细程度，如果原始点云破面比较严重请增加该值，如果需要更精细，请降低该值，默认50 |
| down_sample_size | None      | 是    | 	Float  | 	可选参数-下采样尺寸，值越大点云密度越低，默认None，不进行下采样（请谨慎使用）          |

### 响应示例

- 成功200

```json
{
  "code": 0,
  "data": {
    "dst_point": []
  },
  "err_msg": ""
}
```

- 失败404

```json
{
  "code": -1,
  "data": {},
  "err_msg": "点云标准化失败,..."
}
```

</details>
<details open>
  <summary style="font-size: 28px;font-weight: bold">initial_point</summary>

### 接口描述

初始化点云，再煤场初次建立时，点云文件未进行分批，分块，分堆，该接口通过传入原始盘煤仪活标准化之后的点云，然后给出分堆的量进行点云拆分

### 基本信息

- 接口名称：初始化点云
- 接口URL：

```bash
 http://127.0.0.1:8000/api/pointcloud/initial_point
```

- 请求方式: POST
- Content-Type： application/json

| 参数名          | 参数值               | 是否必填 | 参数类型 | 描述说明                           |
|--------------|-------------------|------|------|--------------------------------|
| src_point    | [[0,1..]]         | 是    | List | 必选参数-原始点云文件（由盘煤仪生成的点云），为一个二维数组 |
| coal_weights | [50000,40000,...] | 是    | List | 必选参数-初始化时煤量，注意煤量数组的顺序一定是由下到上   |

### 响应示例

- 成功200

```json
{
  "code": 0,
  "data": {
    "src_point": [],
    "split_points": []
  },
  "err_msg": ""
}
```

- 失败404

```json
{
  "code": -1,
  "data": {},
  "err_msg": "点云初始化失败,..."
}
```

</details>
<details open>
  <summary style="font-size: 28px;font-weight: bold">store_coal</summary>

### 接口描述

根据输入的原始表面点云，点云初始化后的点云，煤场的堆煤起始位置和终止位置，和堆煤重量，更新表面点云和新增一个拆分后的点云

### 基本信息

- 接口名称：堆煤
- 接口URL：

```bash
 http://127.0.0.1:8000/api/pointcloud/store_coal
```

- 请求方式: POST
- Content-Type： application/json

| 参数名             | 参数值          | 是否必填 | 参数类型      | 描述说明                      |
|-----------------|--------------|------|-----------|---------------------------|
| src_point       | [[0,1..]]    | 是    | List      | 原始点云文件（由盘煤仪生成的点云），为一个二维数组 |
| split_points    | [[[0,1,..]]] | 是    | List      | 拆分后的点云，为一个三维数组            |
| coal_weight	    | 10000        | 是    | 	Float    | 	堆煤的重量单位吨(t)              |
| process_xrange	 | [30,50]      | 是	   | Integer   | 	煤堆堆放的x刻度范围               |
| process_yrange  | 	 [0,50]     | 是    | 	Integer	 | 煤堆堆放的y刻度范围                |
| coal_density    | 1.25         | 否	   | Float     | 煤堆的密度，默认为1.25             |
| x_edge_rate     | 0.4          | 否    | 	Float    | 边缘平滑率-默认0.4值越大边缘越平滑，越小越陡峭 |
| x_sections      | 10           | 否    | 	Integer  | 边缘分段-默认10，值越大边缘越平滑，越小越陡峭  |

### 响应示例

- 成功200

```json
{
  "code": 0,
  "data": {
    "src_point": [],
    "split_points": []
  },
  "err_msg": ""
}
```

- 失败404

```json
{
  "code": -1,
  "data": {},
  "err_msg": "堆煤失败，..."
}
```

</details>
<details open>
  <summary style="font-size: 28px;font-weight: bold">take_coal</summary>

### 接口描述

根据输入的原始表面点云，点云初始化后的点云，煤场的堆煤起始位置和终止位置，和取煤重量，更新表面点云和新增一个拆分后的点云

### 基本信息

- 接口名称：取煤
- 接口URL：

```bash
 http://127.0.0.1:8000/api/pointcloud/take_coal
```

- 请求方式: POST
- Content-Type： application/json

| 参数名             | 参数值          | 是否必填 | 参数类型      | 描述说明                      |
|-----------------|--------------|------|-----------|---------------------------|
| src_point       | [[0,1..]]    | 是    | List      | 原始点云文件（由盘煤仪生成的点云），为一个二维数组 |
| split_points    | [[[0,1,..]]] | 是    | List      | 拆分后的点云，为一个三维数组            |
| coal_weight	    | 10000        | 是    | 	Float    | 	取煤的重量单位吨(t)              |
| process_xrange	 | [30,50]      | 是	   | Integer   | 	煤堆挖取的x刻度的范围              |
| process_yrange  | 	 [0,50]     | 是    | 	Integer	 | 煤堆挖取的y刻度的范围               |
| coal_density    | 1.25         | 否	   | Float     | 煤堆的密度，默认为1.25             |
| x_edge_rate     | 0.4          | 否    | 	Float    | 边缘平滑率-默认0.4值越大边缘越平滑，越小越陡峭 |
| x_sections      | 10           | 否    | 	Integer  | 边缘分段-默认10，值越大边缘越平滑，越小越陡峭  |

### 响应示例

- 成功200

```json
{
  "code": 0,
  "data": {
    "src_point": [],
    "split_points": []
  },
  "err_msg": ""
}
```

- 失败404

```json
{
  "code": -1,
  "data": {},
  "err_msg": "取煤失败，..."
}
```

</details>

<details open>
  <summary style="font-size: 28px;font-weight: bold">inventory_coal</summary>

### 接口描述

煤堆再进行多次堆取后，会存在通过怕堆取接口生成的点云与盘煤仪生成的点云存在差异，本接口通过新的盘煤仪点云和生成的点云进行点云修正

### 基本信息

- 接口名称：煤场盘点
- 接口URL：

```bash
 http://127.0.0.1:8000/api/pointcloud/inventory_coal
```

- 请求方式: POST
- Content-Type： application/json

| 参数名          | 参数值          | 是否必填 | 参数类型 | 描述说明                          |
|--------------|--------------|------|------|-------------------------------|
| new_point    | [[0,1..]]    | 是    | List | 盘煤仪盘点后的新点云（由盘煤仪生成的点云），为一个二维数组 |
| split_points | [[[0,1,..]]] | 是    | List | 拆分后的点云，为一个三维数组                |

### 响应示例

- 成功200

```json
{
  "code": 0,
  "data": {
    "src_point": [],
    "split_points": []
  },
  "err_msg": ""
}
```

- 失败404

```json
{
  "code": -1,
  "data": {},
  "err_msg": "盘点失败，..."
}
```

</details>

