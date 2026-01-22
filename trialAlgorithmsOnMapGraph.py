import mapping.functionSplitting as oxXl
import JamesExampleStructure.backend.algorithms.astar_algorithm as aStar
import JamesExampleStructure.backend.algorithms.dijkstra_algorithm as dijkstra
import JamesExampleStructure.backend.algorithms.yen_algorithm as yen

edgesDict = oxXl.csv_to_dict("edges_table.csv")
nodesDict = oxXl.node_csv_to_dict("nodes_table.csv")

heuristic = aStar.ehf(nodesDict, 13288882110)

distance, path = aStar.astar(edgesDict, 104804, 13288882110, heuristic, trace=False)

print(f"A* Distance: {distance}")
print(f"A* Path: {path}")

distance, path = dijkstra.dijkstra(edgesDict, 104804, 13288882110, trace=False)

print(f"\n\nDijkstra Distance: {distance}\nDijkstra Path: {path}")

paths = yen.yens(edgesDict, 104804, 13288882110, 3)


print(f"\n\nYen's Paths: {paths}\n\n")

for path in paths:
    print(f"Path {paths.index(path)+1}'s distance: {oxXl.calculate_distance_from_node_path(path, "edges_table.csv")}")