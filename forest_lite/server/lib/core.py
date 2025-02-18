"""Example Python I/O library"""
import glob
import xarray
import numpy as np
import datetime as dt
from forest_lite.server.lib import tiling
from functools import lru_cache


TILE_SIZE = 256 # 256 # 64  # 128


def get_data_tile(pattern, data_var, z, x, y, query=None):
    if query is not None:
        # Hashable query
        query = frozenset(query.items())
    path = get_path(pattern)
    return _data_tile(path, data_var, z, x, y, query)


@lru_cache
def _data_tile(path, data_var, z, x, y, query):
    zxy = (z, x, y)
    with xarray.open_dataset(path, engine="h5netcdf") as nc:

        # Find lons/lats related to data_var
        var = nc[data_var]
        for key in var.dims:
            if key.startswith("longitude"):
                lons = var[key].values
            if key.startswith("latitude"):
                lats = var[key].values

        # Find 2D values array
        if query is None:
            array = nc[data_var]
        else:
            idx = dict(query)

            # Map miliseconds to datetime
            idx = { key: convert_ms(key, value) for key, value in idx.items() }

            try:
                array = nc[data_var].sel(**idx, method="nearest")
            except ValueError:
                idx = { key: int(value) for key, value in idx.items() }
                array = nc[data_var].isel(**idx)

        units = nc[data_var].units

    assert array.ndim == 2, f"dims: {var.dims}"
    values = array.values

    # Mask moisture_content_of_soil_layer (TODO: Generalise)
    if "moisture_content" in data_var:
        fill_value = values.max()
        values = np.ma.masked_equal(values, fill_value)
    return _tile({
        "longitude": lons,
        "latitude": lats,
        "values": values,
        "units": units
    }, z, x, y)


def convert_ms(dim, value):
    if "time" in dim.lower():
        if isinstance(value, str):
            return value
        else:
            return dt.datetime.fromtimestamp(value / 1000)
    else:
        return value


def _tile(tilable, z, x, y):
    """Convenient interface for extension drivers"""
    zxy = (z, x, y)
    if "longitude" in tilable:
        lons = tilable["longitude"]
        lats = tilable["latitude"]
        web_mercator_x, web_mercator_y = tiling.web_mercator(lons, lats)
    else:
        web_mercator_x = tilable["web_mercator_x"]
        web_mercator_y = tilable["web_mercator_y"]
    values = tilable["values"]
    units = tilable["units"]
    data = tiling.data_tile(web_mercator_x, web_mercator_y,
                            values, zxy,
                            tile_size=TILE_SIZE)
    data.update({
        "units": [units],
        "tile_key": [[x, y, z]]
    })
    return data


def get_points(path, time):
    with xarray.open_dataset(path, engine="h5netcdf") as nc:
        pts = np.where(nc.time.values == time)
        if len(pts[0]) > 0:
            i = pts[0][0]
            data_array = nc["data"][i][::10, ::20]
    return data_array.to_dict()


def get_path(pattern):
    paths = sorted(glob.glob(pattern))
    if len(paths) > 0:
        return paths[-1]
    else:
        raise Exception(f"{pattern} path not found")


def xy_data(dataset, variable):
    """X-Y line/circle data related to a dataset"""
    # import time
    # time.sleep(5)  # Simulate expensive I/O or slow server
    if dataset == "takm4p4":
        return {
            "x": [0, 1e5, 2e5],
            "y": [0, 1e5, 2e5]
        }
    else:
        return {
            "x": [0, 1e5, 2e5],
            "y": [0, 3e5, 1e5]
        }
