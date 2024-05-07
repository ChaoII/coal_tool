import os.path
from typing import Optional
import uuid
import aiofiles
from starlette.responses import FileResponse
from utils import register_offline_docs
from fastapi import FastAPI, applications, File, UploadFile, Form, Body
from starlette.staticfiles import StaticFiles
from pydantic import BaseModel
from pc_smooth1 import _generate_point_cloud_file
from pc_process import _point_cloud_process, PointProcessType
from log import logger

register_offline_docs(applications)
# 实例化app
app = FastAPI()
# 挂载静态路径将redoc和swagger-ui文件放置在静态路径下
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/files", StaticFiles(directory="files"), name="files")


class CoroRange(BaseModel):
    xmin: int
    xmax: int
    ymin: int
    ymax: int


class PointCloudInputModel(BaseModel):
    coro_range: CoroRange
    delimiter: str = " "
    density: float = 0.5
    nearest_k: int = 50
    down_sample_size: Optional[float] = None
    save_text_filename: str = "dst.txt"
    save_mesh_filename: Optional[str] = None


@app.post("/api/pointcloud/generate_point_cloud")
async def generate_point_cloud(src_pc_file: UploadFile = File(...),
                               x_min: int = Form(0),
                               x_max: int = Form(270),
                               y_min: int = Form(0),
                               y_max: int = Form(50),
                               delimiter: str = Form(" "),
                               density: float = Form(0.5),
                               nearest_k: int = Form(50),
                               down_sample_size: float = Form(None)):
    temp_filename = str(uuid.uuid4()).replace("-", "") + ".txt"
    async with aiofiles.open(temp_filename, 'w') as out_file:
        content = await src_pc_file.read()  # async read
        await out_file.write(content.decode())  # async write
    logger.info(f"创建了临时文件：【{temp_filename}】")
    try:
        file_code = await _generate_point_cloud_file(temp_filename,
                                                     [x_min, x_max],
                                                     [y_min, y_max],
                                                     density,
                                                     nearest_k,
                                                     delimiter,
                                                     down_sample_size)
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            logger.info(f"删除临时文件：【{temp_filename}】")
    except Exception as e:
        return {"code": -1, "data": {}, "err_msg": str(e)}
    return {
        "code": 0,
        "data": {
            "file_marker": file_code.split("_")[0],
            "file_name": file_code.split("_")[1]
        },
        "err_msg": ""
    }


@app.post("/api/pointcloud/store_coal")
async def store_coal(src_pc_file: UploadFile = File(...),
                     coal_weight: float = Form(0.0),
                     process_x_min: int = Form(0),
                     process_x_max: int = Form(0),
                     process_y_min: int = Form(0),
                     process_y_max: int = Form(0),
                     coal_density: float = Form(2.7),
                     new_index: int = Form(None),
                     x_min: int = Form(0),
                     x_max: int = Form(270),
                     y_min: int = Form(0),
                     y_max: int = Form(50),
                     delimiter: str = Form(" "),
                     density: float = Form(0.5),
                     nearest_k: int = Form(50),
                     down_sample_size: float = Form(None)):
    temp_filename = str(uuid.uuid4()).replace("-", "") + ".txt"
    async with aiofiles.open(temp_filename, 'w') as out_file:
        content = await src_pc_file.read()  # async read
        await out_file.write(content.decode())  # async write
    logger.info(f"创建了临时文件：【{temp_filename}】")
    try:
        file_code = await _point_cloud_process(temp_filename,
                                               coal_weight,
                                               [process_x_min, process_x_max],
                                               [process_y_min, process_y_max],
                                               coal_density,
                                               PointProcessType.Storing,
                                               delimiter,
                                               new_index,
                                               [x_min, x_max],
                                               [y_min, y_max],
                                               density,
                                               nearest_k,
                                               down_sample_size)
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            logger.info(f"删除临时文件：【{temp_filename}】")
    except Exception as e:
        return {"code": -1, "data": {}, "err_msg": str(e)}
    return {
        "code": 0,
        "data": {
            "file_marker": file_code.split("_")[0],
            "file_name": file_code.split("_")[1]
        },
        "err_msg": ""
    }


@app.post("/api/pointcloud/take_coal")
async def take_coal(src_pc_file: UploadFile = File(...),
                    coal_weight: float = Form(0.0),
                    process_x_min: int = Form(0),
                    process_x_max: int = Form(0),
                    process_y_min: int = Form(0),
                    process_y_max: int = Form(0),
                    coal_density: float = Form(2.7),
                    new_index: int = Form(None),
                    x_min: int = Form(0),
                    x_max: int = Form(270),
                    y_min: int = Form(0),
                    y_max: int = Form(50),
                    delimiter: str = Form(" "),
                    density: float = Form(0.5),
                    nearest_k: int = Form(50),
                    down_sample_size: float = Form(None)):
    temp_filename = str(uuid.uuid4()).replace("-", "") + ".txt"
    async with aiofiles.open(temp_filename, 'w') as out_file:
        content = await src_pc_file.read()  # async read
        await out_file.write(content.decode())  # async write
    try:
        file_code = await _point_cloud_process(temp_filename,
                                               coal_weight,
                                               [process_x_min, process_x_max],
                                               [process_y_min, process_y_max],
                                               coal_density,
                                               PointProcessType.Taking,
                                               delimiter,
                                               new_index,
                                               [x_min, x_max],
                                               [y_min, y_max],
                                               density,
                                               nearest_k,
                                               down_sample_size)
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            logger.info(f"删除临时文件：【{temp_filename}】")
    except Exception as e:
        return {"code": -1, "data": {}, "err_msg": str(e)}
    return {
        "code": 0,
        "data": {
            "file_marker": file_code.split("_")[0],
            "file_name": file_code.split("_")[1]
        },
        "err_msg": ""
    }


@app.post("/api/pointcloud/download_file")
async def get_file(file_marker: str = Body(...), file_name: str = Body(...)):
    file_url = os.path.join("files/pointcloud/text", file_marker, file_name + ".txt")
    return FileResponse(file_url, media_type="application/octet-stream", filename="dst.txt")


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app)
