"""Support for iris loaded data"""
import numpy as np
import iris
from functools import lru_cache
from forest_lite.server.util import get_file_names
from forest_lite.server.drivers import BaseDriver
from forest_lite.server.drivers.types import Description


driver = BaseDriver()


@driver.override("tilable")
def tilable(settings, data_var, query=None):
    file_names = get_file_names(settings["pattern"])
    cubes = get_cubes(file_names[0])
    cube = cubes[0]
    lats = cube.coord("grid_latitude")[:].points
    lons = cube.coord("grid_longitude")[:].points.copy()
    values = cube[0, 0].data.copy()
    print(lons, lats)
    # Roll input data into [-180, 180] range
    if np.any(lons > 180.0):
        shift_by = np.sum(lons > 180.0)
        lons[lons > 180.0] -= 360.
        lons = np.roll(lons, shift_by)
        values = np.roll(values, shift_by, axis=1)
    return {
        "latitude": lats,
        "longitude": lons,
        "values": values,
        "units": "%"
    }


@lru_cache
def get_cubes(path):
    return iris.load(path)


@driver.override("description")
def description(settings):
    file_names = get_file_names(settings["pattern"])
    data_vars = [{
        "name": "relative_humidity",
        "units": "%"
    }]
    return Description(**{
        "attrs": {},
        "data_vars": {
            data_var["name"]: {
                "dims": [],
                "attrs": {
                    "long_name": data_var["name"],
                    "units": data_var["units"],
                }
            } for data_var in data_vars
        }
    })
