import numpy as np
import matplotlib.pyplot as plt

# the draw function of the utils.py provided 
# was changed so the drawing looked more like 
# the rest of my plots
from utils_altered import flow_layout, draw_flow

def draw_graph(graph, positions):
    # drawing nodes
    nx.draw_networkx_nodes(graph, positions, node_size = 800, node_color = 'royalblue', edgecolors = 'gray', linewidths=1.5)
    # drawing node labels
    nx.draw_networkx_labels(graph, positions, font_size = 12, font_color = 'white', font_weight = 'bold')
    # drawing edges
    nx.draw_networkx_edges(graph, positions, edge_color = 'gray', width = 1.2)
    
    plt.tight_layout()
    plt.axis('off')

import networkx as nx
if __name__ == "__main__":
    print('-----------------------------------------------------') 
    print('Problem 4')
    print("\n=====================================")
    print("     Part (a): Plotting IEEE30       ")
    print("=====================================")
    
    # Reading graph from edgelist
    graph30 = nx.read_edgelist("HW1_2026/ieee30.edgelist")
    # Creating graph positions so it looks ok when plotted
    positions30 = nx.spring_layout(graph30, k = 0.3, seed = 2026, iterations = 50)
    
    # creating figure
    fig = plt.figure(figsize=  (12, 10))
    
    # using preset graph stuff to make the graph look nice
    draw_graph(graph30, positions30)
    
    # saving graph to file
    plt.savefig("ieee30_graph.png")
    plt.close()
    
    # Finding degree and density of plot
    degree_sequence = [d for n,d in graph30.degree]
    max_degree = max(degree_sequence)
    print(f"Maximum degree: {max(degree_sequence)} at node(s): {[n+1 for n,d in enumerate(degree_sequence) if d == max_degree]}")
    print(f"The graph has a density of {nx.density(graph30):0.5f}")
    
    print("\n=====================================")
    print("     Part (b): Plotting IEEE123      ")
    print("=====================================")
    
    # Reading graph from edgelist
    graph123 = nx.read_weighted_edgelist("HW1_2026/ieee123.edgelist")
    # Creating graph positions so it looks ok when plotted
    positions123 = nx.nx_agraph.graphviz_layout(graph123, prog="dot")
    
    fig = plt.figure(figsize=(12, 10))
    
    draw_graph(graph123, positions123)
    
    plt.savefig('ieee123_graph.png')
    plt.close()
    
    degree_sequence = [d for n,d in graph123.degree]
    max_degree = max(degree_sequence)
    print(f"Maximum degree: {max(degree_sequence)} at node(s): {[n+1 for n,d in enumerate(degree_sequence) if d == max_degree]}")
    print(f"The graph has a density of {nx.density(graph123):0.5f}")
    
    print("\n=====================================")
    print("     Part (c): Graph Connectivity    ")
    print("=====================================")
    
    # Is the 30-node graph connected
    if nx.is_connected(graph30):
        print(f"Graph ieee30 is connected.")
    
    else:
        print(f"Graph ieee30 is not connected.")
        
    # Is the 123-node graph connected
    if nx.is_connected(graph123):
        print(f"Graph ieee123 is connected.")
    
    else:
        print(f"Graph ieee123 is not connected.")
        
    print("\n=====================================")
    print("     Part (d): Graph Cycles    ")
    print("=====================================")

    # Using networkX to find it a cycle exists for each plot
    # If a cycle does exist, the found cycle will be plotted
    # If a cycle does not exist, find_cycle raises and exception
    # So the code blocks are help in a try/except
    
    # For IEEE30
    try:
        cycle_path = nx.find_cycle(graph30)
        print(f'IEEE30 Cycle Example:\t{cycle_path}')
        
        fig = plt.figure(figsize=  (12, 10))
        draw_graph(graph30, positions30)
        
        # drawing nodes and edges in path
        nx.draw_networkx_nodes(graph30, positions30, nodelist=[u for u,v in cycle_path], edgecolors='green', node_size=800, linewidths=3)
        nx.draw_networkx_edges(graph30, positions30, edgelist=cycle_path, edge_color = 'green', width=5)
        plt.savefig('ieee30_cycle.png')
        plt.close()    
        
    except nx.exception.NetworkXNoCycle:
        print('No cycle for IEEE30')
    
    # For IEEE123
    try:
        cycle_path = nx.find_cycle(graph123)
        print(f'IEEE30 Cycle Example:\t{cycle_path}')
        
        fig = plt.figure(figsize=  (12, 10))
        draw_graph(graph123, positions123)
        
        # drawing nodes and edges in path
        nx.draw_networkx_nodes(graph123, positions123, nodelist=[u for u,v in cycle_path], edgecolors='green', node_size=800, linewidths=3)
        nx.draw_networkx_edges(graph123, positions123, edgelist=cycle_path, edge_color = 'green', width=5)
        plt.savefig('ieee30_cycle.png')
        plt.close()    
        
    except nx.exception.NetworkXNoCycle:
        print('No cycle for IEEE123')
        
    print("\n=====================================")
    print("     Part (e): Graph Bridges         ")
    print("=====================================")
    
    # Finding the minimum number of cuts for the graph30
    # These will infact be bridges
    # minimum_edge_cut will find the first instance of a bridge
    # bridges will find all instances
    cut_edges = nx.minimum_edge_cut(graph30)
    bridges = list(nx.bridges(graph30))
    
    fig = plt.figure(figsize = (12, 10))
    draw_graph(graph30, positions30)  
    nx.draw_networkx_edges(graph30, positions30, edgelist=bridges, edge_color = 'red', width=5)
    plt.savefig('ieee30_cuts.png')
    plt.close()
    
    print(f'IEEE30 Cut Example:\t{list(cut_edges)}')
    print(f'IEEE30 Bridge Example:\t{bridges}')

    print("\n=====================================")
    print("     Part (f): Handshaking Theorem   ")
    print("=====================================")
    
    # sum of degrees = 2|edges|
    # just need to confirm that total edges count half the sum of degrees
    
    print(f"Total Number of Edges for IEEE30:\t{graph30.number_of_edges()}")
    print(f"Sum of degrees for IEEE30:\t\t{sum(d for n,d in graph30.degree)}")
    print('\n')
    print(f"Total Number of Edges for IEEE123:\t{graph123.number_of_edges()}")
    print(f"Sum of degrees for IEEE123:\t\t{sum(d for n,d in graph123.degree)}")
    
    print("\n=====================================")
    print("     Part (g): Shortest Path         ")
    print("=====================================")
    
    # nodes to start and stop path
    initial_node = '1'
    terminal_node = '30'
    
    # uses networkX algorithms to find path
    shortest_path = nx.shortest_path(graph30, initial_node, terminal_node)
    
    # shortest_path returns a list of nodes
    # converting nodes to edges so they can be plotted
    shortest_path_edges =  [(shortest_path[i], shortest_path[i+1]) for i in range(len(shortest_path) - 1)]
    
    # printing and plotting
    print(f" The shortest path from {initial_node} to {terminal_node} is {shortest_path}")
    
    fig = plt.figure(figsize=  (12, 10))
    draw_graph(graph30, positions30)
    nx.draw_networkx_edges(graph30, positions30, edgelist =shortest_path_edges, edge_color='green', width = 5)
    plt.savefig('ieee30_shortest_path.png')
    
    plt.close()
    
    print('-----------------------------------------------------')
    print('Problem 5')

    # given values/commands for this
    N = 10
    T = 1000* N
    
    # setting seed for repeatability
    rng = np.random.default_rng(seed = 2026)
    amounts_spent = rng.multinomial(T, pvals = np.ones(N) / N)
    
    # Checking that the total money spent is equal to T
    assert sum(amounts_spent) == T, "Total of amounts spent must equal T"
    
    # Generating complete graph
    G = nx.complete_graph(N, nx.DiGraph())
    nx.set_edge_attributes(G, np.inf, 'Capacity')
    
    # Parsing amounts_spent into people who paid less than fair share
    underpaid = np.where(amounts_spent < T/N)[0]
    # and people who paid more than fair share
    overpaid = np.where(amounts_spent >= T/N)[0]

    # Setting up flow network 
    G.add_node('s')
    G.add_node('t')
    
    # connected people who underpaid to source node
    # and people who overpaid to target node
    for i in range(N):
        if i in underpaid:
            G.add_edge('s', i, capacity = abs(T/N - amounts_spent[i]))
        elif i in overpaid:
            G.add_edge(i, 't', capacity = abs(T/N - amounts_spent[i]))
        else:
            pass
        
    # daring using functions provided
    pos = flow_layout(G, 's', 't')
    fig = plt.figure(figsize = (12, 10))
    draw_graph(G, pos)
    plt.savefig('flow_network.png')
    plt.close()
    
    # using max flow algorithm  to solve flow network
    max_flow = nx.maximum_flow(G, 's', 't')
    draw_flow(G, max_flow[1], dict(figsize = (12, 10)), dict(font_size = 20))
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('flow_network_solution.png')