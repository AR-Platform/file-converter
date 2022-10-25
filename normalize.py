"""Normalization functions for the data dictionary"""

import numpy as np


def normalize_data(data: dict):
    """Normalizes the vertices and translation values of the given data dictionary.

    :param data: The data dictionary to normalize
    """
    data_np = np.array(data["vertices"])
    data_np = np.reshape(data_np, (-1, 3))

    # Prepare data
    min_x = np.amin(data_np[:, 0:1], axis=0)
    max_x = np.amax(data_np[:, 0:1], axis=0)
    min_y = np.amin(data_np[:, 1:2], axis=0)
    max_y = np.amax(data_np[:, 1:2], axis=0)
    min_z = np.amin(data_np[:, 2:3], axis=0)
    max_z = np.amax(data_np[:, 2:3], axis=0)
    scale_x = max_x - min_x
    scale_y = max_y - min_y
    scale_z = max_z - min_z

    # Position object at y = 0
    data_np[:, 1] -= min_y

    # Center object at x = z = 0
    data_np[:, 0] -= (min_x + max_x) / 2
    data_np[:, 2] -= (min_z + max_z) / 2

    # Normalize scale
    max_size = max(scale_x, scale_y, scale_z)
    data_np /= max_size

    # Normalize translate values
    if "blocks" in data.keys():
        for block in data["blocks"]:
            if block["name"] in ["TL1", "TL2", "TL3"]:
                block["values"] = [float(x / max_size) for x in block["values"]]

    data["vertices"] = data_np.flatten().tolist()
