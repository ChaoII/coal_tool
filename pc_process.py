import asyncio
from typing import Union, Optional

import numpy as np
import open3d as o3d


async def draw_point(point: np.ndarray):
    """
    绘制点云
    :param point:
    :return:
    """
    points = o3d.geometry.PointCloud()
    points.points = o3d.utility.Vector3dVector(point)  # 替换为点云数据
    o3d.visualization.draw_geometries([points])


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


async def store_coal_inner(src_point: np.ndarray, split_points: list[np.ndarray], coal_weight: float,
                           process_xrange: Union[np.ndarray, list],
                           process_yrange: Optional[Union[np.ndarray, list]] = None,
                           coal_density: float = 1.25,
                           x_edge_rate: float = 0.4,
                           x_sections: int = 10):
    stack_x = process_xrange[1] - process_xrange[0]
    stack_y = process_yrange[1] - process_yrange[0]
    stack_z = coal_weight / coal_density / (stack_x * stack_y)
    masks = await calculate_height(process_xrange, stack_z, x_edge_rate, x_sections)
    store_point = []
    for mask in masks:
        mask_ = (src_point[:, 0] >= mask[0]) & (src_point[:, 0] < mask[1]) & (
                src_point[:, 1] >= process_yrange[0]) & (src_point[:, 1] <= process_yrange[1])
        src_point[mask_, 2] = src_point[mask_, 2] + mask[2]
        store_point.extend(src_point[mask_, :])
    split_points.append(np.array(store_point))
    return split_points, src_point


async def take_coal_inner(src_point: np.ndarray,
                          split_points: list[np.ndarray],
                          coal_weight: float,
                          process_xrange: Union[np.ndarray, list],
                          process_yrange: Optional[Union[np.ndarray, list]] = None,
                          coal_density: float = 1.25,
                          x_edge_rate: float = 0.4,
                          x_sections: int = 10):
    if process_yrange[0] is None and process_yrange[1] is not None:
        process_yrange = [np.min(src_point[:, 1]), process_yrange[1]]
    if process_yrange[0] is not None and process_yrange[1] is None:
        process_yrange = [process_yrange[0], np.max(src_point[:, 1])]
    if process_yrange[0] is None and process_yrange[1] is None:
        process_yrange = [np.min(src_point[:, 1]), np.max(src_point[:, 1])]
    stack_x = process_xrange[1] - process_xrange[0]
    stack_y = process_yrange[1] - process_yrange[0]
    stack_z = coal_weight / coal_density / (stack_x * stack_y)
    masks = await calculate_height(process_xrange, stack_z, x_edge_rate, x_sections)
    for mask in masks:
        mask_ = (src_point[:, 0] >= mask[0]) & (src_point[:, 0] < mask[1]) & (
                src_point[:, 1] >= process_yrange[0]) & (src_point[:, 1] <= process_yrange[1])
        src_point[mask_, 2] = src_point[mask_, 2] - mask[2]
    dst_points = src_point
    return split_points, dst_points


async def initial_point_inner(src_point: np.ndarray, coal_weights: Union[np.ndarray, list]) -> (
        list[np.ndarray], np.ndarray):
    """
    初始化点云，将原始盘煤仪点云文件进行分层
    :param src_point: 原始盘煤仪点云文件
    :param coal_weights: 分层煤的量，注意量一定是按照最下层到最上层排列
    :return: 分层后的点云
    """
    coal_weights = coal_weights / np.sum(coal_weights)
    total_height = np.max(src_point[:, 2])
    start_height = end_height = 0
    split_points = []
    bake_src_point = src_point.copy()
    for coal_weight in coal_weights:
        height = total_height * coal_weight
        end_height = end_height + height
        mask = (src_point[:, 2] >= start_height) & (src_point[:, 2] < end_height)
        dst_point = src_point.copy()
        src_point = src_point[~mask]
        dst_point[~mask, 2] = end_height
        start_height = end_height
        await draw_point(dst_point)
        split_points.append(dst_point)
    return split_points, bake_src_point


async def inventory_coal_inner(new_point: np.ndarray, split_points: list[np.ndarray]):
    """
    盘点点云
    :param split_points: 拆分后的点云列表
    :param new_point: 盘煤后盘煤仪生成的新点云
    :return:
    """
    new_split_points = []
    for split_point in split_points:
        max_height = np.max(split_point[:, 2])
        mask_ = (split_point[:, 2] < max_height)
        ring = split_point[mask_]
        for i in range(len(ring)):
            x, y = ring[i, :2]
            mask_total = (new_point[:, 0] == x) & (new_point[:, 1] == y)
            mask_split = (split_point[:, 0] == x) & (split_point[:, 1] == y)
            new_z = new_point[mask_total, 2]
            split_point[mask_split, 2] = new_z
        split_point[~mask_, 2] = np.max(split_point[:, 2])
        new_split_points.append(split_point)
    return new_point, new_split_points


if __name__ == '__main__':
    asyncio.run(
        store_coal_inner(
            np.loadtxt("test/dst2.txt", delimiter=" ")[:, :3], split_points=[],
            coal_weight=5000, process_xrange=[100, 116], process_yrange=[0, 50]))

    # asyncio.run(
    #     initial_point(src_point=np.loadtxt("test/dst2.txt", delimiter=" ")[:, :3],
    #                   coal_weights=np.array([100000, 200000, 300000])))
