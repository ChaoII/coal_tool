import numpy as np
import pyvista as pv
import open3d as o3d
from scipy.spatial import cKDTree


def save_to_text(points: np.ndarray, file_name="result.txt"):
    np.savetxt(file_name, points, fmt="%5.2f", delimiter=' ')


def save_to_ply(points: np.ndarray, file_name="result.ply"):
    pc = pv.PolyData(points)
    mesh = pc.reconstruct_surface()
    mesh.save(file_name)


def down_sample(pcd: o3d.geometry.PointCloud, voxel_size: float) -> o3d.geometry.PointCloud:
    return pcd.voxel_down_sample(voxel_size)


def get_pc_bound(points: np.ndarray) -> np.ndarray:
    x_min = points[:, 0].min()
    x_max = points[:, 0].max()
    y_min = points[:, 1].min()
    y_max = points[:, 1].max()
    z_min = points[:, 2].min()
    z_max = points[:, 2].max()
    return np.array([[x_min, x_max], [y_min, y_max], [z_min, z_max]])


def reconstruct_surface(points: np.ndarray) -> pv.PolyData:
    pcd_ = pv.PolyData(points)
    return pcd_.reconstruct_surface()


def corrected_points(mesh: pv.PolyData,
                     bound=np.array([[-np.inf, np.inf],
                                     [-np.inf, np.inf],
                                     [-np.inf, np.inf]])) -> np.ndarray:
    point_ = np.array(mesh.points)
    if bound[0, 0] != -np.inf:
        point_[point_[:, 0] < bound[0, 0], 0] = bound[0, 0]
    if bound[0, 1] != np.inf:
        point_[point_[:, 0] > bound[0, 1], 0] = bound[0, 1]
    if bound[1, 0] != -np.inf:
        point_[point_[:, 1] < bound[1, 0], 1] = bound[1, 0]
    if bound[1, 1] != np.inf:
        point_[point_[:, 1] > bound[1, 1], 1] = bound[1, 1]
    if bound[2, 0] != -np.inf:
        point_[point_[:, 2] < bound[2, 0], 2] = bound[2, 0]
    if bound[2, 1] != np.inf:
        point_[point_[:, 2] > bound[2, 1], 2] = bound[2, 1]
    return point_


def get_hint_voxel_size(points: np.ndarray, k=3) -> float:
    tree = cKDTree(points)
    distances, _ = tree.query(points, k)
    return distances.max()


def point_cloud_smooth(src_filename: str, down_sample_size=None, k_size=3, bound=None,
                       save_to_text_filename=None,
                       save_to_ply_filename=None) -> np.ndarray:
    pcd = o3d.io.read_point_cloud(src_filename, format="xyz")
    if not down_sample_size:
        points = np.array(pcd.points)[:, :2]
        down_sample_size = get_hint_voxel_size(points, k_size)
    if not bound:
        bound = get_pc_bound(np.array(pcd.points))
    pcd_ = down_sample(pcd, voxel_size=down_sample_size)
    mesh = reconstruct_surface(np.array(pcd_.points))
    mesh_ = corrected_points(mesh, bound)
    if save_to_text_filename:
        save_to_text(mesh_, save_to_text_filename)
    if save_to_ply_filename:
        save_to_ply(mesh_, save_to_ply_filename)
    return mesh_


if __name__ == '__main__':
    points = point_cloud_smooth("test/n.txt", down_sample_size=0.1, save_to_text_filename="2.txt")

    pc_data = pv.PolyData(points)
    pc_data.plot()

    # pc = o3d.geometry.PointCloud()
    # pc.points = o3d.utility.Vector3dVector(points)
    # o3d.visualization.draw_geometries([pc])
