from typing import Union, Optional
import numpy as np


async def _add_point_cloud(src_pc_filename: str,
                           xrange: Union[np.ndarray, list],
                           yrange=None,
                           density: float = 2.7,
                           delimiter: str = ",",
                           new_index: Optional[int] = None):
    if yrange is None:
        yrange = [-np.inf, np.inf]
    if new_index is None:
        src_points = np.loadtxt(src_pc_filename, delimiter=delimiter)
        if src_points.shape[1] <= 4:
            new_index = 0
        else:
            new_index = np.max(src_points[:, 4]) + 1

    src_points[:, 3]


if __name__ == '__main__':
    _add_point_cloud("files/pointcloud/text/20240403/2024040316240357dc85bb96d6412095287264371b17ec.txt", [30, 70],
                     None, 2)
