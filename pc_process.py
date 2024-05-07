from typing import Union, Optional
import numpy as np
import asyncio
from pc_smooth1 import _generate_point_cloud_array, _generate_point_cloud_file, _generate_filename
from enum import Enum
from log import logger


class PointProcessType(Enum):
    Storing = 0
    Taking = 1


@logger.catch
async def _point_cloud_process(src_pc_filename: Union[str, np.ndarray],
                               coal_weight: float,
                               process_xrange: Union[np.ndarray, list],
                               process_yrange: Optional[Union[np.ndarray, list]] = None,
                               coal_density: float = 2.7,
                               process_type: PointProcessType = PointProcessType.Storing,
                               delimiter: str = " ",
                               new_index: Optional[int] = None,
                               xrange: Optional[list] = None,
                               yrange: Optional[list] = None,
                               density: float = 0.5,
                               nearest_k: int = 50,
                               down_sample_size: Optional[float] = None):
    if isinstance(src_pc_filename, str):
        src_points = np.loadtxt(src_pc_filename, delimiter=delimiter)
    elif isinstance(src_pc_filename, np.ndarray):
        src_points = src_pc_filename
    else:
        logger.error("文件必须是本地文件路径或者numpy数据类型")
        raise IOError("文件必须是本地文件路径或者numpy数据类型")
    if process_yrange is None:
        process_yrange = [np.min(src_points[:, 1]), np.max(src_points[:, 1])]
    stack_x = process_xrange[1] - process_xrange[0]
    stack_y = process_yrange[1] - process_yrange[0]
    stack_z = coal_weight / coal_density / (stack_x * stack_y)
    mask1 = (src_points[:, 0] >= process_xrange[0]) & (src_points[:, 0] < process_xrange[1]) & (
            src_points[:, 1] >= process_yrange[0]) & (src_points[:, 1] < process_yrange[1])
    if process_type == PointProcessType.Storing:
        src_points[mask1, 2] = src_points[mask1, 2] + stack_z
    else:
        src_points[mask1, 2] = src_points[mask1, 2] - stack_z
    if src_points.shape[1] == 3:
        src_points = np.c_[src_points, np.zeros(src_points.shape[0])]
    elif src_points.shape[1] < 3:
        logger.error("数据格式错误")
        raise ValueError("数据格式错误")
    if new_index is None:
        new_index = np.max(src_points[:, 3]) + 1

    dst_points = await _generate_point_cloud_array(src_points, xrange, yrange, density, nearest_k, delimiter,
                                                   down_sample_size)
    dst_points = np.c_[dst_points, src_points[:, 3]]
    if process_type == PointProcessType.Storing:
        mask2 = (dst_points[:, 0] >= process_xrange[0]) & (dst_points[:, 0] < process_xrange[1]) & (
                dst_points[:, 1] >= process_yrange[0]) & (dst_points[:, 1] < process_yrange[1])
        dst_points[mask2, 3] = new_index
    filepath, file_code = await _generate_filename("txt")
    np.savetxt(filepath, dst_points, fmt="%5.4f", delimiter=delimiter)
    return file_code


if __name__ == '__main__':
    asyncio.run(
        _point_cloud_process(
            r"C:\Users\AC\PycharmProjects\pointcloud\files\pointcloud\text\20240507\20240507171628231a04b13f794997ac20cd934ea079aa.txt",
            coal_weight=5000, process_xrange=[100, 116], process_yrange=None,
            process_type=PointProcessType.Storing, delimiter=" ", new_index=None, xrange=[0, 270],
            coal_density=2.7, yrange=[0, 50], density=0.5, nearest_k=50, down_sample_size=None))
