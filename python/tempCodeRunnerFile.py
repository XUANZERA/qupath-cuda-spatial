from engine import Engine

# import后自动注册
import primitives.nearest_neighbor
import primitives.distance_to_polygon

from io import read_point_set_csv

from python.data_structure.contract import NearestNeighborInput



engine = Engine()

source = read_point_set_csv("../data/src.csv")
target = read_point_set_csv("../data/tar.csv")

my_input = NearestNeighborInput(
    source=source,
    target=target,
)


result = engine.run(
    primitive="nearest_neighbor",
    backend="cuda",
    data=my_input,
)

print(result)