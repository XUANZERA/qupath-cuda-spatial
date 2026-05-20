from pathlib import Path
from typing import Any, Union

import json
import csv
import numpy as np
import numpy.typing as npt
import pandas as pd

from python.data_structure.schema import PointSet, PolygonSet, DistanceResult


def read_csv(path: Path, encoding: str = "utf-8") -> pd.DataFrame:
    return pd.read_csv(path, encoding=encoding)


def read_json(path: Path, encoding: str = "utf-8") -> dict[str, Any]:
    with open(path, "r", encoding=encoding) as f:
        return json.load(f)


def read_point_set_csv(path: Path, encoding: str = "utf-8") -> PointSet:

    df = read_csv(path, encoding)

    required = {"ids", "x", "y"}
    missing = required - set(df.columns)
    
    if missing:
        raise ValueError(f"Missing Columns: {missing}")
    
    point_set = PointSet(
        ids = df["ids"].to_numpy(dtype=np.int64),
        x = df["x"].to_numpy(dtype=np.float32),
        y = df["y"].to_numpy(dtype=np.float32),
    )

    point_set.validate()

    return point_set

##############################################################################################
# feature_idx,polygon_idx,ring_idx,vertex_idx, x, y
# 0          ,          0,       0,         0,10,10
# 0          ,          0,       0,         1,20,10
# 0          ,          0,       0,         2,20,20
# 0          ,          0,       0,         3,10,20
# feature: 一个语义annotation，例如Nerve1, Vessle2
# polygon: 同一个feature_ids的annotation的多个polygon (多个即为MultiPolygon)
# ring: 同一个polygon的多个环
# vertex: 同一个环的不同vertex
# x, y: 同一个环的(x, y)
##############################################################################################
# Geojson组成:
# for feature in featureCollection:
# featureCollection: 多个feature
# feature: 语义对象

# for geometry in feature:
# geometry: 多边形/多个多边形

# for ring: array in geometry:
# ring: 一个环

# for (x, y) in ring:
# (x, y) 一个节点的坐标

# FeatureCollection
#     └── Feature
#             └── Geometry
#                     └── Polygon / MultiPolygon
#                             └── Ring
#                                     └── Vertex(x,y)
##############################################################################################
def read_geojson(path: Path, encoding: str = "utf-8") -> PolygonSet:

    feature_idx_list = list()
    polygon_idx_list = list()
    ring_idx_list = list()
    vertex_idx_list = list()
    x_list = list()
    y_list = list()

    geojson = read_json(path, encoding)

    for feature_idx, feature in enumerate(geojson["features"]):
        geometry = feature["geometry"]
        geometry_type = geometry["type"]
        coordinates = geometry["coordinates"]


        if geometry_type == "MultiPolygon":

            for polygon_idx, polygon in enumerate(coordinates):
                for ring_idx, ring in enumerate(polygon):
                    for vertex_idx, vertex in enumerate(ring):

                        x = vertex[0]
                        y = vertex[1]

                        feature_idx_list.append(feature_idx)
                        polygon_idx_list.append(polygon_idx)
                        ring_idx_list.append(ring_idx)
                        vertex_idx_list.append(vertex_idx)
                        x_list.append(x)
                        y_list.append(y)

            
        elif geometry_type == "Polygon":

            POLYGON_IDX = 0

            for ring_idx, ring in enumerate(coordinates):
                for vertex_idx, vertex in enumerate(ring):

                    x = vertex[0]
                    y = vertex[1]

                    feature_idx_list.append(feature_idx)
                    polygon_idx_list.append(POLYGON_IDX)
                    ring_idx_list.append(ring_idx)
                    vertex_idx_list.append(vertex_idx)
                    x_list.append(x)
                    y_list.append(y)

        else:
            raise ValueError(f"Unsupported Geometry Type: {geometry_type}")
        
    result = PolygonSet(
        feature_idx=np.asarray(feature_idx_list, dtype=np.int64),
        polygon_idx=np.asarray(polygon_idx_list, dtype=np.int64),
        ring_idx=np.asarray(ring_idx_list, dtype=np.int64),
        vertex_idx=np.asarray(vertex_idx_list, dtype=np.int64),
        x=np.asarray(x_list, dtype=np.float32),
        y=np.asarray(y_list, dtype=np.float32)
    )

    return result

def geojson_write_csv(path: Path, polygon: PolygonSet, encoding: str = "utf-8") -> None:
    
    with open(path, "w", newline="", encoding=encoding) as f:

        writer = csv.writer(f)

        writer.writerow(
            [
                "feature_idx",
                "polygon_idx",
                "ring_idx",
                "vertex_idx",
                "x",
                "y"
            ]
        )

        rows = zip(
            polygon.feature_idx,
            polygon.polygon_idx,
            polygon.ring_idx,
            polygon.vertex_idx,
            polygon.x,
            polygon.y
        )

        writer.writerows(rows)

    print(f"Exported {len(rows)} vertices -> {path}")


def geojson_to_csv(input_path: Path, output_path: Path, encoding: str = "utf-8") -> None:

    r = read_geojson(path=input_path, encoding=encoding)
    geojson_write_csv(path=output_path, polygon=r, encoding=encoding)


def write_distance_result_csv(result: DistanceResult, path: Path) -> None:
    
    result.validate()
    
    df = pd.DataFrame(
        {
            "id": result.id,
            "distance": result.distance
        }
    )

    df.to_csv(path)