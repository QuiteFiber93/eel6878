import numpy as np
import matplotlib.pyplot as plt

import networkx as nx
if __name__ == "__main__":
    print('-----------------------------------------------------')
    print('Problem 4')
    print("\n=====================================")
    print("     Part (a): Plotting IEEE30       ")
    print("=====================================")
    fig = plt.figure(figsize=  (12, 10))
    graph30 = nx.read_edgelist("HW1_2026/ieee30.edgelist")
    positions30 = nx.spring_layout(graph30, k = 0.3, seed = 2026, iterations = 50)
    nx.draw(graph30, positions30, with_labels=True)
    plt.savefig("ieee30_graph.png")

    degree_sequence = [d for n,d in graph30.degree]
    max_degree = max(degree_sequence)
    print(f"Maximum degree: {max(degree_sequence)} at node(s): {[n+1 for n,d in enumerate(degree_sequence) if d == max_degree]}")
    print(f"The graph has a density of {nx.density(graph30)}")
    
    print("\n=====================================")
    print("     Part (b): Plotting IEEE123      ")
    print("=====================================")
    fig = plt.figure(figsize=(12, 10))
    graph123 = nx.read_weighted_edgelist("HW1_2026/ieee123.edgelist")
    positions123 = nx.nx_agraph.graphviz_layout(graph123, prog="dot")
    nx.draw(graph123, positions123, with_labels=True, font_size=10, font_weight="bold")
    plt.savefig('ieee123_graph.png')

    degree_sequence = [d for n,d in graph123.degree]
    max_degree = max(degree_sequence)
    print(f"Maximum degree: {max(degree_sequence)} at node(s): {[n+1 for n,d in enumerate(degree_sequence) if d == max_degree]}")
    print(f"The graph has a density of {nx.density(graph123)}")
    
    print("\n=====================================")
    print("     Part (c): Graph Connectivity    ")
    print("=====================================")
    
    if nx.is_connected(graph30):
        print(f"Graph ieee30 is connected.")
    
    else:
        print(f"Graph ieee30 is not connected.")
        
    if nx.is_connected(graph123):
        print(f"Graph ieee123 is connected.")
    
    else:
        print(f"Graph ieee123 is not connected.")
        
    print("\n=====================================")
    print("     Part (d): Graph Cycles    ")
    print("=====================================")

    cycle_path = nx.find_cycle(graph30)
    print(f'IEEE30 Cycle Example:\t{cycle_path}')
    fig = plt.figure(figsize=  (12, 10))
    nx.draw(graph30, positions30, with_labels=True)
    nx.draw_networkx_edges(graph30, positions30, edgelist=cycle_path, edge_color = 'red')
    plt.savefig('ieee30_cycle.png')
        
        
    try:
        print(f'IEEE123 Cycle Example:\t{nx.find_cycle(graph123)}')
    except nx.exception.NetworkXNoCycle:
        print('No cycle for IEEE123')
        
    print("\n=====================================")
    print("     Part (e): Graph Bridges         ")
    print("=====================================")
    
    bridges = nx.bridges(graph30)
    cut_edges = nx.minimum_edge_cut(graph30)
    print(f'IEEE30 Cut Example:\t{list(cut_edges)}')
    print(f'IEEE30 Bridge Example:\t{list(bridges)}')

    print("\n=====================================")
    print("     Part (f): Handshaking Theorem   ")
    print("=====================================")
    
    print(f"Total Number of Edges for IEEE30:\t{graph30.number_of_edges()}")
    print(f"Sum of degrees for IEEE30:\t\t{sum(d for n,d in graph30.degree)}")
    print('\n')
    print(f"Total Number of Edges for IEEE123:\t{graph123.number_of_edges()}")
    print(f"Sum of degrees for IEEE123:\t\t{sum(d for n,d in graph123.degree)}")
    
    print("\n=====================================")
    print("     Part (g): Shortest Path         ")
    print("=====================================")
    initial_node = '1'
    terminal_node = '30'
    shortest_path = nx.shortest_path(graph30, initial_node, terminal_node)
    shortest_path_edges =  [(shortest_path[i], shortest_path[i+1]) for i in range(len(shortest_path) - 1)]
    
    print(f" The shortest path from {initial_node} to {terminal_node} is {shortest_path}")
    fig = plt.figure(figsize=  (12, 10))
    nx.draw(graph30, positions30, with_labels = True)
    nx.draw_networkx_edges(graph30, positions30, edgelist =shortest_path_edges, edge_color='red')
    plt.savefig('ieee30_shortest_path.png')