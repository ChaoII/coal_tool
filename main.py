import os.path
import uuid
import aiofiles
from starlette.responses import FileResponse
from utils import register_offline_docs
from fastapi import FastAPI, applications, File, UploadFile, Form, Body
from starlette.staticfiles import StaticFiles
from pc_smooth1 import _generate_point_cloud_file
from pc_process import _point_cloud_process, PointProcessType, delete_temp_file
from log import logger

register_offline_docs(applications)
# 实例化app
app = FastAPI()
# 挂载静态路径将redoc和swagger-ui文件放置在静态路径下
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/files", StaticFiles(directory="files"), name="files")


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
    temp_filename = "./temp/" + str(uuid.uuid4()).replace("-", "") + ".txt"
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

        await delete_temp_file(temp_filename)
    except Exception as e:
        logger.error("点云重建失败", str(e))
        await delete_temp_file(temp_filename)
        return {"code": -1, "data": {}, "err_msg": "点云重建失败"}
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
                     coal_weight: float = Form(...),
                     process_x_min: int = Form(...),
                     process_x_max: int = Form(...),
                     process_y_min: int = Form(None),
                     process_y_max: int = Form(None),
                     coal_density: float = Form(2.7),
                     new_index: int = Form(None),
                     x_edge_rate: float = Form(0.4),
                     x_sections: int = Form(10),
                     rebuild_point_cloud: bool = Form(False),
                     x_min: int = Form(0),
                     x_max: int = Form(270),
                     y_min: int = Form(0),
                     y_max: int = Form(50),
                     delimiter: str = Form(" "),
                     density: float = Form(0.5),
                     nearest_k: int = Form(50),
                     down_sample_size: float = Form(None)):
    temp_filename = "./temp/" + str(uuid.uuid4()).replace("-", "") + ".txt"
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
                                               x_edge_rate,
                                               x_sections,
                                               rebuild_point_cloud,
                                               [x_min, x_max],
                                               [y_min, y_max],
                                               density,
                                               nearest_k,
                                               down_sample_size)
        await delete_temp_file(temp_filename)
    except Exception as e:
        logger.error("新增堆煤失败", str(e))
        await delete_temp_file(temp_filename)
        return {"code": -1, "data": {}, "err_msg": "新增堆煤失败"}
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
                    coal_weight: float = Form(...),
                    process_x_min: int = Form(...),
                    process_x_max: int = Form(...),
                    process_y_min: int = Form(None),
                    process_y_max: int = Form(None),
                    coal_density: float = Form(2.7),
                    new_index: int = Form(None),
                    x_edge_rate: float = Form(0.4),
                    x_sections: int = Form(10),
                    rebuild_point_cloud: bool = Form(False),
                    x_min: int = Form(0),
                    x_max: int = Form(270),
                    y_min: int = Form(0),
                    y_max: int = Form(50),
                    delimiter: str = Form(" "),
                    density: float = Form(0.5),
                    nearest_k: int = Form(50),
                    down_sample_size: float = Form(None)):
    temp_filename = "./temp/" + str(uuid.uuid4()).replace("-", "") + ".txt"
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
                                               x_edge_rate,
                                               x_sections,
                                               rebuild_point_cloud,
                                               [x_min, x_max],
                                               [y_min, y_max],
                                               density,
                                               nearest_k,
                                               down_sample_size)
        await delete_temp_file(temp_filename)
    except Exception as e:
        logger.error("取煤失败", str(e))
        await delete_temp_file(temp_filename)
        return {"code": -1, "data": {}, "err_msg": "取煤失败"}
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
