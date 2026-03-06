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
# new_arr = nx.laplacian_matrix(G).toarray()
# print(new_arr)
# for n in range(1, N):
#     if new_arr[0, n] == 0:
#         # print(f"Edge (0, {n}) does not exist")
#         new_arr[n, 0] = -1
#         new_arr[0, n] = -1
        
#         new_arr[0, 0] += 1
#         new_arr[n, n] += 1
#         print(np.array2string(np.sort(np.linalg.eigvals(new_arr)), precision=4, suppress_small=True))
#         new_arr[0, 0] -= 1
#         new_arr[n, n] -= 1
#         new_arr[n, 0] = 0
#         new_arr[0, n] = 0
# # new_arr[0, 2] = -1

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

chars = pd.read_csv("HW2_2026_Harry_Potter_Graphs/characters.csv")
edges = pd.read_csv("HW2_2026_Harry_Potter_Graphs/relations.csv")

G = nx.Graph()
for _, row in edges.iterrows():
    G.add_edge(row['source'], row['edge'], weight = 'weight', type = row['type'])

node_count = G.number_of_nodes()
edge_count = G.number_of_edges()
average_degree = 2 * edge_count / node_count
density = nx.density(G)
is_connected = nx.is_connected(G)
connected_components = nx.number_connected_components(G)
print(f"Node Count: {node_count}")
print(f"Edge Count: {edge_count}")
print(f"Average Degree: {average_degree}")
print(f"Density = {density}")
print(f"Is Graph Connected: {is_connected}")
print(f"Connected Components: {connected_components}")


print(f"Total Ally Edges: ")
print(f"Total Enemy Edges: ")

# Problem 5
print("\nProblem 5")
print("====================================================")