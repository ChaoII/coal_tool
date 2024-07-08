from typing import List, Optional

import numpy as np
from fastapi import FastAPI, applications
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.staticfiles import StaticFiles

from log import logger
from pc_process import store_coal_inner, initial_point_inner, \
    inventory_coal_inner, take_coal_inner
from pc_smooth1 import normalize_point_inner
from utils import register_offline_docs

register_offline_docs(applications)
# 实例化app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

PointCloud = List[List[float]]


class InitialPoint(BaseModel):
    src_point: PointCloud
    coal_weights: List[float]


class StoreCoalModel(BaseModel):
    src_point: PointCloud
    split_points: List[PointCloud]
    coal_weight: float
    process_xrange: List[int]
    process_yrange: List[int]
    coal_density: float = 1.25
    x_edge_rate: float = 0.4
    x_sections: int = 10


class TakeColaModel(BaseModel):
    src_point: PointCloud
    split_points: list[PointCloud]
    coal_weight: float
    process_xrange: List[int]
    process_yrange: List[int]
    coal_density: float
    x_edge_rate: float = 0.4
    x_sections: int = 10


class PointNormalizeModel(BaseModel):
    src_point: PointCloud
    x_range: list[int]
    y_range: list[int]
    density: float = 0.5
    nearest_k: int = 50
    down_sample_size: Optional[float] = None


class InventoryModel(BaseModel):
    new_point: PointCloud
    split_points: list[PointCloud]


# 挂载静态路径将redoc和swagger-ui文件放置在静态路径下
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/files", StaticFiles(directory="files"), name="files")


@app.post("/api/pointcloud/normalize_point")
async def normalize_point(parameter: PointNormalizeModel):
    src_point = np.array(parameter.src_point)
    if src_point.shape != 2 and src_point.shape[1] != 3:
        err_msg = f"原始点云文件错误格式错误，点云必须包含x,y,z 三列数据，但是点云数据列数为{src_point.shape[1]}"
        logger.error(err_msg)
        return {"code": -1, "data": {}, "err_msg": err_msg}
    try:
        dst_point = await normalize_point_inner(src_point,
                                                parameter.x_range,
                                                parameter.y_range,
                                                parameter.density,
                                                parameter.nearest_k,
                                                parameter.down_sample_size)

    except Exception as e:
        err_msg = f"点云重建失败,失败原因{e}"
        logger.error(err_msg)
        return {"code": -1, "data": {}, "err_msg": err_msg}
    return {
        "code": 0,
        "data": {
            "dst_point": dst_point.tolist(),
        },
        "err_msg": ""
    }


@app.post("/api/pointcloud/initial_point")
async def initial_point(parameter: InitialPoint):
    src_point = np.array(parameter.src_point)
    if src_point.shape != 2 and src_point.shape[1] != 3:
        err_msg = f"原始点云文件错误格式错误，点云必须包含x,y,z 三列数据，但是点云数据列数为{src_point.shape[1]}"
        logger.error(err_msg)
        return {"code": -1, "data": {}, "err_msg": err_msg}
    try:
        split_points, src_point = await initial_point_inner(src_point, parameter.coal_weights)
        split_points = list(map(lambda x: x.tolist(), split_points))
    except Exception as e:
        err_msg = f"初始化堆煤失败, {e}"
        logger.error(err_msg)
        return {"code": -1, "data": {}, "err_msg": err_msg}
    return {
        "code": 0,
        "data": {
            "src_point": src_point.tolist(),
            "split_points": split_points
        },
        "err_msg": ""
    }


@app.post("/api/pointcloud/store_coal")
async def store_coal(parameter: StoreCoalModel):
    src_point = np.array(parameter.src_point)
    if src_point.shape != 2 and src_point.shape[1] != 3:
        err_msg = f"原始点云文件错误格式错误，点云必须包含x,y,z 三列数据，但是点云数据列数为{src_point.shape[1]}"
        logger.error(err_msg)
        return {"code": -1, "data": {}, "err_msg": err_msg}
    try:
        split_points = list(map(lambda x: np.array(x), parameter.split_points))
        split_points, src_point = await store_coal_inner(src_point, split_points, parameter.coal_weight,
                                                         parameter.process_xrange, parameter.process_yrange,
                                                         parameter.coal_density, parameter.x_edge_rate,
                                                         parameter.x_sections)
        split_points = list(map(lambda x: x.tolist(), split_points))
    except Exception as e:
        err_msg = f"新增堆煤失败, {e}"
        logger.error(err_msg)
        return {"code": -1, "data": {}, "err_msg": err_msg}
    return {
        "code": 0,
        "data": {
            "src_point": src_point.tolist(),
            "split_points": split_points
        },
        "err_msg": ""
    }


@app.post("/api/pointcloud/take_coal")
async def take_coal(parameter: TakeColaModel):
    src_point = np.array(parameter.src_point)
    if src_point.shape != 2 and src_point.shape[1] != 3:
        err_msg = f"原始点云文件错误格式错误，点云必须包含x,y,z 三列数据，但是点云数据列数为{src_point.shape[1]}"
        logger.error(err_msg)
        return {"code": -1, "data": {}, "err_msg": err_msg}
    try:
        split_points = list(map(lambda x: np.array(x), parameter.split_points))
        split_points, dst_points = await take_coal_inner(src_point,
                                                         split_points,
                                                         parameter.coal_weight,
                                                         parameter.process_xrange,
                                                         parameter.process_yrange,
                                                         parameter.coal_density,
                                                         parameter.x_edge_rate,
                                                         parameter.x_sections,
                                                         )
        split_points = list(map(lambda x: x.tolist(), split_points))
    except Exception as e:
        err_msg = f"取煤失败, {e}"
        logger.error(err_msg)
        return {"code": -1, "data": {}, "err_msg": err_msg}
    return {
        "code": 0,
        "data": {
            "src_point": dst_points.tolist(),
            "split_points": split_points
        },
        "err_msg": ""
    }


@app.post("/api/pointcloud/inventory_coal")
async def inventory_coal(parameter: InventoryModel):
    new_point = np.array(parameter.new_point)
    if new_point.shape != 2 and new_point.shape[1] != 3:
        err_msg = f"原始点云文件错误格式错误，点云必须包含x,y,z 三列数据，但是点云数据列数为{new_point.shape[1]}"
        logger.error(err_msg)
        return {"code": -1, "data": {}, "err_msg": err_msg}
    try:
        split_points = list(map(lambda x: np.array(x), parameter.split_points))
        dst_points, split_points = await inventory_coal_inner(new_point, split_points)
        split_points = list(map(lambda x: x.tolist(), split_points))
    except Exception as e:
        err_msg = f"盘点失败, {e}"
        logger.error(err_msg)
        return {"code": -1, "data": {}, "err_msg": err_msg}
    return {
        "code": 0,
        "data": {
            "src_point": dst_points.tolist(),
            "split_points": split_points
        },
        "err_msg": ""
    }


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app)
