import json
import csv


# =========================================================
# INPUT / OUTPUT
# =========================================================

INPUT_GEOJSON = r"D:\BaiduNetdiskDownload\PC\wsi_data_deprecated\experiment\geojson_1447f23e-1114-4b9a-bb00-98f10a7974b9.geojson"

OUTPUT_CSV = "nerve_vertices.csv"


# =========================================================
# LOAD GEOJSON
# =========================================================

with open(INPUT_GEOJSON, "r", encoding="utf-8") as f:
    geojson = json.load(f)


# =========================================================
# OUTPUT ROWS
# =========================================================

rows = []


# =========================================================
# PARSE FEATURES
# =========================================================

for feature_idx, feature in enumerate(geojson["features"]):

    geometry = feature["geometry"]

    geometry_type = geometry["type"]

    coordinates = geometry["coordinates"]


    # =====================================================
    # MULTIPOLYGON
    #
    # Structure:
    #
    # [
    #   polygon_1[
    #       ring_1[
    #           [x, y],
    #           [x, y]
    #       ]
    #   ]
    # ]
    # =====================================================

    if geometry_type == "MultiPolygon":

        for polygon_idx, polygon in enumerate(coordinates):

            for ring_idx, ring in enumerate(polygon):

                for vertex_idx, vertex in enumerate(ring):

                    x = vertex[0]
                    y = vertex[1]

                    rows.append([
                        feature_idx,
                        polygon_idx,
                        ring_idx,
                        vertex_idx,
                        x,
                        y
                    ])


    # =====================================================
    # POLYGON
    # =====================================================

    elif geometry_type == "Polygon":

        for ring_idx, ring in enumerate(coordinates):

            for vertex_idx, vertex in enumerate(ring):

                x = vertex[0]
                y = vertex[1]

                rows.append([
                    feature_idx,
                    0,
                    ring_idx,
                    vertex_idx,
                    x,
                    y
                ])


    else:

        print(f"Skip unsupported geometry type: {geometry_type}")


# =========================================================
# WRITE CSV
# =========================================================

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:

    writer = csv.writer(f)

    writer.writerow([
        "feature_idx",
        "polygon_idx",
        "ring_idx",
        "vertex_idx",
        "x",
        "y"
    ])

    writer.writerows(rows)


print(f"Exported {len(rows)} vertices -> {OUTPUT_CSV}")
