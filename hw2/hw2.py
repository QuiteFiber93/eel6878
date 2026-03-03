from os import listdir

import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Problem 2

# Function to create edgelist for graph with circular symmetry
def create_circular_edgelist(N, I):
    edge_list = []
    for u in range(N):
        for v in range(N):
            for i in I:
                if v == (u + i) % N: edge_list.append((u, v))
    return edge_list

# Actually creating graph for specified conditions
N = 5
I = [1]
G = nx.Graph(create_circular_edgelist(N, I))

fig = plt.figure()
plt.title(f'Circular Graph for N = {N}')
pos = nx.circular_layout(G)
nx.draw_circular(G)
nx.draw_networkx_labels(G, pos)
plt.show()

# Numerically calculating laplacian eigenvalues
laplacian_eig = nx.laplacian_spectrum(G)
print(f"Analytic Result: {None}")
print(f"Numerical Result: {laplacian_eig}")


# Looping through N for Fielder eigenvalue
start = 5
stop = 50
step = 5
N = np.arange(start, stop+step, step)

fielder_values = [nx.laplacian_spectrum(nx.Graph(create_circular_edgelist(n, I)))[1] for n in N]

fig = plt.figure()
plt.plot(N, fielder_values, '-o')
plt.title('Fielder Eigenvalues from 5 to 50')
plt.grid()
plt.show()

# N = 10
N = 10
G = nx.Graph(create_circular_edgelist(N, I))

fielder_eigenvalues = [None for n in range(1, N)]

for n in range(1, N):
    

# Problem 3
karate_graph = nx.karate_club_graph()


# Problem 4
# Gets data for All Books and Books 1-7
graph_data = listdir('./data')
graph_data.remove('characters.csv')

graph_names = ["All Books"] + [f"Book {n}" for n in range(1,8)]

# Creating dict to store graphs in
book_graphs = {name : None for name in graph_names}

# dataframe to hold all statistics
book_graph_stats = pd.DataFrame(columns = graph_names, index = ['Node Count', 'Edge Count', 'Average Degree', 'Density', 'Connected', 'Connected Components'])

for name,data in zip(graph_names,graph_data):
    # Will use nx function to convert from pandas DF to edgelist
    # First reading csv to pandas dataframe
    book_graph_data = pd.read_csv("./data/" + data)
    
    # Now converting pandas dataframe to graph through edgelist
    # Graph is stored in dict where keys are book number and values are graph
    book_graphs[name] = nx.from_pandas_edgelist(book_graph_data, 'source', 'target', 'weight')

    # Statistics of graph
    node_count = book_graphs[name].number_of_nodes()
    edge_count = book_graphs[name].number_of_edges()
    average_degree = 2 * edge_count / node_count
    density = nx.density(book_graphs[name])
    is_connected = nx.is_connected(book_graphs[name])
    connected_components = nx.number_connected_components(book_graphs[name])
    
    # Inserting statistics into dataframe
    book_graph_stats[name] = [node_count, edge_count, average_degree, density, is_connected, connected_components]
    

print(book_graph_stats)

# Problem 5

# Problem 6