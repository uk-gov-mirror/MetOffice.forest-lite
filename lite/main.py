import argparse
import glob
import os
import cartopy
import numpy as np
import uvicorn
import fastapi
from fastapi import Response, Request
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.responses import FileResponse
import bokeh.palettes
from bokeh.core.json_encoder import serialize_json
import yaml
import lib.core
import lib.config
import lib.palette
import lib.atlas


app = fastapi.FastAPI()
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)


CONFIG = None  # TODO: Remove global variable


@app.on_event("startup")
async def startup_event():
    global CONFIG

    # Configure application
    args = parse_args()
    with open(args.config_file) as stream:
        data = yaml.safe_load(stream)
        CONFIG = lib.config.Config(**data)


@app.get("/")
async def root(request: Request):
    context = {"request": request,
               "title": "FOREST lite"}
    return templates.TemplateResponse("index.html", context)


@app.get("/datasets")
async def datasets(response: Response):
    response.headers["Cache-Control"] = "max-age=31536000"
    return {"names": sorted(dataset.label for dataset in CONFIG.datasets)}


@app.get("/datasets/{dataset_name}/times/{time}")
async def datasets_images(dataset_name: str, time: int):
    for dataset in CONFIG.datasets:
        if dataset.label == dataset_name:
            pattern = dataset.driver.settings["pattern"]
            paths = sorted(glob.glob(pattern))
            if len(paths) > 0:
                obj = lib.core.image_data(dataset_name,
                                          paths[-1],
                                          time)
                content = serialize_json(obj)
                response = Response(content=content,
                                    media_type="application/json")
                #  response.headers["Cache-Control"] = "max-age=31536000"
                return response


@app.get("/palettes")
async def palettes():
    return list(lib.palette.all_palettes())


@app.get("/datasets/{dataset_name}/times")
async def dataset_times(dataset_name, limit: int = 10):
    for dataset in CONFIG.datasets:
        if dataset.label == dataset_name:
            pattern = dataset.driver.settings["pattern"]
            paths = sorted(glob.glob(pattern))
            if len(paths) > 0:
                obj = lib.core.get_times(dataset_name, paths[-1])[-limit:]
                content = serialize_json(obj)
                response = Response(content=content,
                                    media_type="application/json")
                #  response.headers["Cache-Control"] = "max-age=31536000"
                return response


@app.get("/tiles/{dataset}/{time}/{Z}/{X}/{Y}")
async def tiles(dataset: str, time: int, Z: int, X: int, Y: int):
    print(dataset, time, Z, X, Y)
    obj = lib.core.get_data_tile(CONFIG, dataset, time, Z, X, Y)
    content = serialize_json(obj)
    response = Response(content=content,
                        media_type="application/json")
    #  response.headers["Cache-Control"] = "max-age=31536000"
    return response


@app.get("/points/{dataset}/{timestamp_ms}")
async def points(dataset: str, timestamp_ms: int):
    time = np.datetime64(timestamp_ms, 'ms')
    path = lib.core.get_path(CONFIG, dataset)
    obj = lib.core.get_points(path, time)
    content = serialize_json(obj)
    response = Response(content=content,
                        media_type="application/json")
    #  response.headers["Cache-Control"] = "max-age=31536000"
    return response


@app.get("/google_limits")
async def google_limits():
    return {
        "x": cartopy.crs.Mercator.GOOGLE.x_limits,
        "y": cartopy.crs.Mercator.GOOGLE.y_limits,
    }


@app.get("/atlas/{feature}")
async def atlas_feature(feature: str):
    obj = lib.atlas.load_feature(feature)
    content = serialize_json(obj)
    response = Response(content=content,
                        media_type="application/json")
    #  response.headers["Cache-Control"] = "max-age=31536000"
    return response


def parse_args():
    """Command line interface"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8888)
    parser.add_argument("config_file")
    return parser.parse_args()


def main():
    # Parse command line arguments
    args = parse_args()

    # Start server
    uvicorn.run("main:app", port=args.port)


if __name__ == '__main__':
    main()
