import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


if __name__ == "__main__":
    print('-----------------------------------------------------')
    print('Problem 4')
    print("=====================================")
    print("     Part (a): Plotting IEEE30       ")
    print("=====================================")
    ax1 = plt.subplot(111)
    graph30 = nx.read_edgelist("HW1_2026/ieee30.edgelist")
    nx.draw(graph30, with_labels=True)
    plt.show()

    degree_sequence = [d for n,d in graph30.degree]
    max_degree = max(degree_sequence)
    print(f"Maximum dgree: {max(degree_sequence)} at node(s): {[n+1 for n,d in enumerate(degree_sequence) if d == max_degree]}")
    
    print("=====================================")
    print("     Part (b): Plotting IEEE123      ")
    print("=====================================")
    ax1 = plt.subplot(111)
    graph123 = nx.read_weighted_edgelist("HW1_2026/ieee123.edgelist")
    nx.draw(graph123, with_labels=True)
    plt.show()

    degree_sequence = [d for n,d in graph123.degree]
    max_degree = max(degree_sequence)
    print(f"Maximum dgree: {max(degree_sequence)} at node(s): {[n+1 for n,d in enumerate(degree_sequence) if d == max_degree]}")
    
    print("=====================================")
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
        
    print("=====================================")
    print("     Part (d): Graph Cycles    ")
    print("=====================================")
    
    print(f'IEEE30 Cycle Example:\t{nx.find_cycle(graph30)}')
    print(f'IEEE123 Cycle Example:\t{nx.find_cycle(graph123)}')
    
    print("=====================================")
    print("     Part (e): Graph Bridges         ")
    print("=====================================")
    
    print(f'IEEE30 Bridge Example:\t{nx.find_cycle(graph30)}')
    