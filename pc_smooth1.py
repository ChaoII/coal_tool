import os
import uuid
import itertools
from datetime import datetime
from typing import Optional, Union

import numpy as np
from scipy.spatial import cKDTree

import config


async def _generate_filename(suffix: str) -> (str, str):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    dirname = ""
    if suffix == "txt":
        dirname = os.path.join("./files/pointcloud/text", timestamp[:8])
    if suffix in ['ply', 'vtp', 'stl', 'vtk']:
        dirname = os.path.join("./files/pointcloud/mesh", timestamp[:8])
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    filename = timestamp + str(uuid.uuid4()).replace("-", "")
    filepath = os.path.join(dirname, filename + "." + suffix)
    file_code = timestamp[:8] + "_" + filename
    return filepath, file_code


async def normalize_point_inner(src_point: np.ndarray,
                                xrange: list,
                                yrange: list,
                                density: float = 0.5,
                                nearest_k: int = 50,
                                down_sample_size: Optional[float] = None) -> np.ndarray:
    x = np.arange(xrange[0], xrange[1] + density, density)
    y = np.arange(yrange[0], yrange[1] + density, density)
    grid = np.array(list(itertools.product(x, y)))
    dst_point = np.zeros([grid.shape[0], 3])
    dst_point[:, :2] = grid
    kd_tree = cKDTree(src_point[:, :2])
    # 对第二个点集合中的每个点查找最近邻
    # k = 1 表示只查找最近的一个邻点
    distances, indices = kd_tree.query(grid, nearest_k)  #
    for i, (distance, idx) in enumerate(zip(distances, indices)):
        dst_point[i, 2] = np.average(src_point[idx, 2])
    if down_sample_size:
        import open3d as o3d
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(dst_point)
        down_pcd = pcd.voxel_down_sample(voxel_size=down_sample_size)
        dst_point = np.array(down_pcd.points)
    return dst_point


async def _generate_point_cloud_file(src_pc_filename: Union[np.ndarray, str],
                                     xrange: Union[np.ndarray, list],
                                     yrange: Union[np.ndarray, list],
                                     density: Optional[float] = 0.5,
                                     nearest_k: Optional[int] = 50,
                                     delimiter: str = " ",
                                     down_sample_size: Optional[float] = None):
    """
    重建点云，将点云文件标准化
    :param src_pc_filename: 输入的文件名
    :param xrange: x坐标范围
    :param yrange: y坐标范围
    :param delimiter: 分隔符默认为' '（空格）
    :param density: 点云密度默认为0.5m
    :param nearest_k: 最近邻点，值越大模型越平滑，值越小越精细，但是会出现奇异点，表面撕裂的问题
    :param down_sample_size: 体素大小，可选参数，默认不进行下采样，值越大模型越平滑，但精细度越差，值太小会显著增加计算耗时
    :return:
    """
    dst_points = await _generate_point_cloud_array(src_pc_filename,
                                                   xrange,
                                                   yrange,
                                                   density,
                                                   nearest_k,
                                                   delimiter,
                                                   down_sample_size)
    filepath, file_code = await _generate_filename("txt")
    np.savetxt(filepath, dst_points, fmt="%5.4f", delimiter=delimiter)
    if config.save_mesh_filename:
        import pyvista as pv
        pc_data = pv.PolyData(dst_points)
        mesh = pc_data.reconstruct_surface()
        filepath, _ = await _generate_filename("ply")
        mesh.save(filepath, binary=False)
        # mesh.plot(color='orange', show_edges=True)
    return file_code


if __name__ == '__main__':
    import asyncio

    asyncio.run(_generate_point_cloud_file("test/n.txt", [0, 270], [0, 50]))
