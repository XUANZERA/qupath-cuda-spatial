@echo off
@REM .\target\release\qupath_gpu_tool.exe ^
@REM   --mode nearest_neighbor ^
@REM   --source examples/nearest_neighbor/input_x.csv ^
@REM   --target examples/nearest_neighbor/input_y.csv ^
@REM   --output examples/nearest_neighbor/result.csv

.\target\release\qupath_gpu_tool.exe ^
  --mode distance_to_polygon ^
  --source examples/distance_to_polygon/boundary_input.csv ^
  --target examples/distance_to_polygon/cells_input.csv ^
  --output examples/distance_to_polygon/result.csv 