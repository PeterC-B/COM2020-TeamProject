from server.scripts.visualisation.visualisation_utils import plot_blank_graph

coords = (51.4545, -2.5879)  # Bristol
plot_blank_graph(coords, radius=500, travel_type="walk", saveToFile=True)