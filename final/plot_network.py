import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D
import csv

# Building the graph from edge list file
edgelist = "network_graph.edgelist"

G = nx.DiGraph()
with open(edgelist, "r", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        G.add_edge(
            row["source"],
            row["target"],
            time=int(row["time"]),
            cost=int(row["cost"]),
            weather=row["weather"],
        )

locations = list(G.nodes())

# Approximate positions of cities on real map
positions = {
    "ANC": (-1.5,  5.0),
    "SEA": ( 0.0,  3.5),
    "POR": (-0.2,  3.0),
    "OAK": (-0.5,  1.8),
    "LAX": (-0.2,  1.0),
    "PHX": ( 0.8,  1.0),
    "SLC": ( 1.2,  2.8),
    "DEN": ( 2.2,  2.5),
    "MSP": ( 3.5,  3.5),
    "KC":  ( 3.5,  2.0),
    "DAL": ( 3.5,  0.8),
    "HOU": ( 3.8,  0.0),
    "MEM": ( 4.2,  1.5),
    "CHI": ( 4.5,  3.2),
    "DTW": ( 5.5,  3.3),
    "YYZ": ( 5.8,  4.0),   
    "ATL": ( 5.5,  1.2),
    "CLT": ( 6.2,  1.6),
    "JAX": ( 6.0,  0.4),
    "TPA": ( 5.8, -0.2),
    "MIA": ( 6.5, -0.5),
    "PHL": ( 7.0,  2.6),
    "NYC": ( 7.2,  3.0),
    "BOS": ( 7.6,  3.4),
    "HNL": (-3.0,  0.5), 
}


fig, ax = plt.subplots(figsize = (10, 5))

# Drawing nodes
nx.draw_networkx_nodes(G, positions, ax =ax, node_size = 900, edgecolors = 'black', linewidths = 1.2)

nx.draw_networkx_labels(G, positions, ax = ax, font_size = 12, font_weight = 'bold', font_color = 'white')


# Drawing edges and edge labels
weather = {"Low": "#2ca02c", "Medium": "#ff8c00", "High": "#d62728"}

for level, color in weather.items():
    edges = [(u, v) for u, v, d in G.edges(data = True) if d['weather'] == level]
    
    nx.draw_networkx_edges(G, positions, ax = ax, edgelist = edges, edge_color = color, 
                           width = 1.5, alpha = 0.6, arrows = True, arrowsize = 14)
    
edge_labels = { (u, v): f"{d['time']}d / ${d['cost']}" for u, v, d in G.edges(data = True)}

nx.draw_networkx_edge_labels(G, positions, ax = ax, edge_labels = edge_labels, font_size = 6, label_pos = 0.5,
                             bbox = dict(boxstyle = 'round,pad=0.15', fc = 'white', ec = 'none', alpha = 0.7))

legend = [
    Line2D([0], [0], color = weather['Low'], lw = 3, label = 'Weather: Low'),
    Line2D([0], [0], color = weather['Medium'], lw = 3, label = 'Weather: Medium'),
    Line2D([0], [0], color = weather['High'], lw = 3, label = 'Weather: High')
]

ax.legend(handles = legend, loc = 'lower left', fontsize = 9, framealpha = 0.9)

ax.set_title('Logistics Network', fontsize = 14, fontweight = 'bold')

ax.set_axis_off()

plt.tight_layout()

plt.savefig('network_graph.png', dpi = 300, bbox_inches = 'tight')

plt.show()