from os import listdir

import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans

# Problem 2
print("\nProblem 2")
print("====================================================")
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

# Using analytic expression prodivded in lecture
analytic_predictions = np.array([2*(1 - np.cos(2*np.pi*k/N)) for k in range(N)])
# Numerically calculating laplacian eigenvalues
laplacian_eig = nx.laplacian_spectrum(G)

print(f"Analytic Predictions:   {np.array2string(np.sort(analytic_predictions), precision=5)}")
print(f"Numerical Calculations: {np.array2string(laplacian_eig, precision=5, suppress_small=True)}")


# Looping through N for Fielder eigenvalue
start = 5
stop = 50
step = 5
N = np.arange(start, stop+step, step)

fielder_values = [nx.algebraic_connectivity(nx.Graph(create_circular_edgelist(n, I))) for n in N]

fig = plt.figure()
plt.plot(N, fielder_values, '-o')
plt.title('Fielder Eigenvalues from 5 to 50')
plt.grid()
plt.show()

# N = 10
N = 10
G = nx.Graph(create_circular_edgelist(N, I))

fielder_eigenvalues = [None for n in range(1, N)]

for n in range(N-1):
    # Node to be connected
    u = n + 1
    # Checking to see if the edge already exists
    # If the edge exists, connectivity will not change, so fielder eigenvalue remains unchanged
    if G.has_edge(0, u):
        fielder_eigenvalues[n] = nx.algebraic_connectivity(G)
    
    # If the edge does not already exist, create it, analyze, and delete it
    else:
        G.add_edge(0, u)
        fielder_eigenvalues[n] = nx.algebraic_connectivity(G)
        G.remove_edge(0, u)
        
# Plotting results        
fig = plt.figure()
plt.plot(range(1, N), fielder_eigenvalues, '-o')
plt.title('Fielder Eigenvalues After Connecting Nodes 0 and k')
plt.xlabel('k')
plt.ylabel('Fielder Eigenvalue')
plt.grid()
plt.autoscale(False, axis = 'y')
plt.show()

# Problem 3
print("\nProblem 3")
print("====================================================")
karate_graph = nx.karate_club_graph()
pos = nx.circular_layout(karate_graph)

def spectral_clustering(G: nx.Graph, K: int, normalized = False):
    L = nx.normalized_laplacian_matrix(G).toarray() if normalized else nx.laplacian_matrix(G).toarray()
    
    # Using eigh because L is supposed to be symmetric
    eigvals, eigvecs = np.linalg.eigh(L)

    # We will be using K-means on rows of K_least_vectors
    K_least_vectors = eigvecs[:, :K]
    
    K_means = KMeans(n_clusters = K)
    K_means.fit(K_least_vectors)
    labels = K_means.predict(K_least_vectors)
    
    return labels

# part a) K = 2
K = 2    
labels = spectral_clustering(karate_graph, K)
fig = plt.figure()
nx.draw(karate_graph, pos, node_color = labels)
nx.draw_networkx_labels(karate_graph, pos)
plt.show()

# part b) K = 3
K = 3
labels = spectral_clustering(karate_graph, K)
fig = plt.figure()
nx.draw(karate_graph, pos, node_color = labels)
nx.draw_networkx_labels(karate_graph, pos)
plt.show()

# Problem 4 
print("\nProblem 4")
print("====================================================")

# Gets data for All Books and Books 1-7
graph_data = listdir('./data')
graph_data.remove('characters.csv')

# Names to be used in dict and plots
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
print("\nProblem 5")
print("====================================================")

degree_centrality = {}
weighted_degree_centrality = {}
closeness_centrality = {}
betweeness_centrality = {}
eigenvector_centrality = {}
pagerank = {}
for name,G in book_graphs.items():

    degree_centrality[name] = dict(G.degree())
    weighted_degree_centrality[name] = dict(G.degree(weight = "weight"))
    eigenvector_centrality[name] = dict(nx.eigenvector_centrality(G))
    closeness_centrality[name] = dict(nx.closeness_centrality(G))
    betweeness_centrality[name] = dict(nx.betweenness_centrality(G))
    pagerank[name] = dict(nx.pagerank(G, weight='weight'))

degree_centrality = pd.DataFrame(degree_centrality)
weighted_degree_centrality = pd.DataFrame(weighted_degree_centrality)
eigenvector_centrality = pd.DataFrame(eigenvector_centrality)
closeness_centrality = pd.DataFrame(closeness_centrality)
betweeness_centrality = pd.DataFrame(betweeness_centrality)
pagerank = pd.DataFrame(pagerank)

# Problem 6

G = book_graphs['All Books']

# Getting node positions
communities = nx.community.louvain_communities(G, weight='weight')


# TODO: Find a way to convert communities to labels

# Getting node sizes
node_size = 10000*pagerank.loc[list(G.nodes()), 'All Books']

# positions of nodes
pos = nx.spring_layout(G, weight = 'weight')

# Label sizes
label_size = betweeness_centrality.loc[list(G.nodes()), 'All Books']

fig = plt.figure()
nx.draw_networkx_nodes(G, pos)
nx.draw_networkx_labels(G, pos)
plt.axes()
# plt.show()


