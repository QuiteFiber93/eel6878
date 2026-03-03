from os import listdir

import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

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