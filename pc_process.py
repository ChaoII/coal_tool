import asyncio
import os
from enum import Enum
from typing import Union, Optional

import numpy as np

import config
from log import logger
from pc_smooth1 import _generate_filename, _generate_point_cloud_array


async def delete_temp_file(temp_filename: str):
    if os.path.exists(temp_filename):
        os.remove(temp_filename)
        logger.info(f"删除临时文件：【{temp_filename}】")


class PointProcessType(Enum):
    Storing = 0
    Taking = 1


async def calculate_height(xrange: list, height: float, x_edge_rate: float, x_sections: int) -> list:
    new_height = height / ((1 + 1 - 2 * x_edge_rate) / 2)
    x_diff = xrange[1] - xrange[0]
    tan_x = new_height / (x_diff * x_edge_rate)
    if x_sections == 0:
        per_section_x = x_diff * x_edge_rate
    else:
        per_section_x = x_diff * x_edge_rate / x_sections
    x_masks = []
    for i in range(x_sections):
        x_left_range = [xrange[0] + i * per_section_x, xrange[0] + (i + 1) * per_section_x]
        x_right_range = [xrange[1] - (i + 1) * per_section_x, xrange[1] - i * per_section_x]
        x_masks.append(
            [*x_left_range, (i + 1) * per_section_x * tan_x])
        x_masks.append(
            [*x_right_range, (i + 1) * per_section_x * tan_x])
    x_masks.append([xrange[0] + x_diff * x_edge_rate, xrange[1] - x_diff * x_edge_rate, new_height])
    return x_masks


async def _point_cloud_process(src_pc_filename: Union[str, np.ndarray],
                               coal_weight: float,
                               process_xrange: Union[np.ndarray, list],
                               process_yrange: Optional[Union[np.ndarray, list]] = None,
                               coal_density: float = 2.7,
                               process_type: PointProcessType = PointProcessType.Storing,
                               delimiter: str = " ",
                               new_index: Optional[int] = None,
                               x_edge_rate: float = 0.4,
                               x_sections: int = 10,
                               rebuild_point_cloud: bool = False,
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
    if process_yrange[0] is None and process_yrange[1] is not None:
        process_yrange = [np.min(src_points[:, 1]), process_yrange[1]]
    if process_yrange[0] is not None and process_yrange[1] is None:
        process_yrange = [process_yrange[0], np.max(src_points[:, 1])]
    if process_yrange[0] is None and process_yrange[1] is None:
        process_yrange = [np.min(src_points[:, 1]), np.max(src_points[:, 1])]
    stack_x = process_xrange[1] - process_xrange[0]
    stack_y = process_yrange[1] - process_yrange[0]
    stack_z = coal_weight / coal_density / (stack_x * stack_y)

    masks = await calculate_height(process_xrange, stack_z, x_edge_rate, x_sections)

    for mask in masks:
        mask_ = (src_points[:, 0] >= mask[0]) & (src_points[:, 0] < mask[1]) & (
                src_points[:, 1] >= process_yrange[0]) & (src_points[:, 1] <= process_yrange[1])
        if process_type == PointProcessType.Storing:
            src_points[mask_, 2] = src_points[mask_, 2] + mask[2]
        else:
            src_points[mask_, 2] = src_points[mask_, 2] - mask[2]
    if src_points.shape[1] == 3:
        src_points = np.c_[src_points, np.zeros(src_points.shape[0])]
    elif src_points.shape[1] < 3:
        logger.error("数据格式错误")
        raise ValueError("数据格式错误")
    if new_index is None:
        new_index = np.max(src_points[:, 3]) + 1

    if rebuild_point_cloud:
        dst_points = await _generate_point_cloud_array(src_points, xrange, yrange, density, nearest_k, delimiter,
                                                       down_sample_size)
        if dst_points.shape[0] != src_points.shape[0]:
            raise ValueError(
                "请确保在开启堆煤后点云重建时，确保输入的点云为已经标准化后的点云，并且点云重建的参数要和标准化时的一致")
        dst_points = np.c_[dst_points, src_points[:, 3]]
    else:
        dst_points = src_points
    if process_type == PointProcessType.Storing:
        mask2 = (dst_points[:, 0] >= process_xrange[0]) & (dst_points[:, 0] < process_xrange[1]) & (
                dst_points[:, 1] >= process_yrange[0]) & (dst_points[:, 1] < process_yrange[1])
        dst_points[mask2, 3] = new_index
    filepath, file_code = await _generate_filename("txt")
    np.savetxt(filepath, dst_points, fmt="%5.4f", delimiter=delimiter)

    if config.save_mesh_filename:
        import pyvista as pv
        pc_data = pv.PolyData(dst_points[:, :3])
        mesh = pc_data.reconstruct_surface()
        filepath, _ = await _generate_filename("ply")
        mesh.save(filepath, binary=False)
        mesh.plot(color='orange', show_edges=True)

    return file_code


if __name__ == '__main__':
    asyncio.run(
        _point_cloud_process(
            r"C:\Users\AC\PycharmProjects\pointcloud\files\pointcloud\text\20240507\20240507171628231a04b13f794997ac20cd934ea079aa.txt",
            coal_weight=5000, process_xrange=[100, 116], process_yrange=None,
            process_type=PointProcessType.Storing, delimiter=" ", new_index=None, xrange=[0, 270],
            coal_density=2.7, yrange=[0, 50], density=0.5, nearest_k=50, down_sample_size=None))
