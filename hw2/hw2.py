from os import listdir

import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

# Problem 4
# Gets data for All Books and Books 1-7
graph_data = listdir('./data')
graph_data.remove('characters.csv')

graph_names = ["All Books"] + [f"Book {n}" for n in range(1,8)]

# Creating dict to store graphs in
book_graphs = {name : None for name in graph_names}
for name,data in zip(graph_names,graph_data):
    # Will use nx function to convert from pandas DF to edgelist
    # First reading csv to pandas dataframe
    book_graph_data = pd.read_csv("./data/" + data)
    
    # Now converting pandas dataframe to graph through edgelist
    book_graphs[name] = nx.from_pandas_edgelist(book_graph_data, 'source', 'target', 'weight')
    
    # Showing graph statistics
    print(book_graphs[name].number_of_nodes())
    
    # Plots graph
    fig = plt.figure()
    nx.draw_networkx(book_graphs[name])
    plt.title(name)
    plt.axes()
    plt.show()
    