import csv
import json
from pathlib import Path
from random import Random
from statistics import median

import networkx as nx
import matplotlib.pyplot as plt

# Config
edgelist  = "network_graph.edgelist"
responses = "llm_responses.json"
PLOTS_DIR      = "plots"

encodings       = ["edge_list", "adjacency_list", "incidence"]
encoding_labels = {"edge_list": "Edge List", "adjacency_list": "Adjacency List", "incidence": "Incidence"}
encoding_colors = {"edge_list": "tab:blue", "adjacency_list": "tab:orange", "incidence": "tab:green"}

# Making sure the plots look good in the IEEE double column size
plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight",
    "font.size": 8, "axes.titlesize": 9, "axes.labelsize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 7,
    "legend.fontsize": 7, "legend.frameon": True, "legend.framealpha": 0.9,
    "legend.borderpad": 0.3, "legend.handlelength": 1.4,
    "legend.handletextpad": 0.5,
    "lines.linewidth": 1.5, "lines.markersize": 5,
    "axes.linewidth": 0.8, "grid.linewidth": 0.5,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "xtick.major.size": 3, "ytick.major.size": 3,
})

query_labels = {
    "fastest":  ["time", "total_days",  "Days"],
    "cheapest": ["cost", "total_cost",  "Cost"],
}

# Building graph from edge list
G = nx.DiGraph()
with open(edgelist, newline="") as f:
    for row in csv.DictReader(f):
        G.add_edge(row["source"], row["target"], time = int(row["time"]), cost = int(row["cost"]), weather = row["weather"])

# Function to calculate total cost along path for a given attribute
def path_total(G, path, weight):
    
    return sum( G[path[i]][path[i + 1]][weight] for i in range(len(path) - 1) )

# Parse the LLM results, extract the model path, and validate
def extract_model_path(G, llm_response, true_sol):
    
    # Return none if query did not succeed 
    # or if the returned path is invalid
    if llm_response["result_type"] != "succeeded": 
        return None
    
    parsed_result = llm_response.get("parsed")
    if not isinstance(parsed_result, dict):      
        return None
    
    path = parsed_result.get("path")
    
    # Path is invalid if there are less than two nodes, not all nodes/edges are in G
    # Also checks against type, so that path is a list
    if (not isinstance(path, list)
        or len(path) < 2
        or any(node not in G for node in path)
        or not all( G.has_edge(path[i], path[i + 1]) for i in range(len(path) - 1)) ):
        
        return None
    
    # Ensures the source and target of path are correct.
    if path[0] != true_sol["source"] or path[-1] != true_sol["target"]: 
        return None
    
    return path

llm_responses = json.loads(Path(responses).read_text())
reference_sols = {i: r for i, r in enumerate(llm_responses['ground_truth'])}

# Scoring LLM responses
connectivity = {encoding: {'correct': 0, 'asked': 0} for encoding in encodings}
paths = {query_type: {encoding: {'total': 0, 'valid' : 0, 'exact' : 0, 'optimal' : 0} for encoding in encodings} for query_type in query_labels}

for llm_response in llm_responses['responses'].values():
    encoding = llm_response['meta']['encoding']
    query_type = llm_response['meta']['query_type']
    reference_sol = reference_sols[llm_response['meta']['pair_idx']]

    # We dont care about path values for connectivity
    if query_type == 'connectivity':
        connectivity[encoding]['asked'] += 1
        
        parsed_response = llm_response.get('parsed')
        if (isinstance(parsed_response, dict)
        and 'connected' in parsed_response
        and bool(parsed_response['connected']) == bool(reference_sol['connected'])):
            connectivity[encoding]['correct'] += 1
            
        continue
    
    # Scoring the actual paths found
    paths[query_type][encoding]['total'] += 1
    
    path = extract_model_path(G, llm_response, reference_sol)
    
    if path is None:
        continue
    
    paths[query_type][encoding]['valid'] += 1
    weight, key, metric_label = query_labels[query_type]
    
    if path == reference_sol[query_type]['path']:
        paths[query_type][encoding]['exact'] += 1
        
    if path_total(G, path, weight) == reference_sol[query_type][key]:
        paths[query_type][encoding]['optimal'] += 1
        
        
# Plotting Connectivity
fig, ax = plt.subplots(figsize = (3.5, 2.6))

accuracies = [connectivity[encoding]['correct']/connectivity[encoding]['asked'] 
              if connectivity[encoding]['asked'] else 0.0 for encoding in encodings]
bars = ax.bar([encoding_labels[encoding] for encoding in encodings], accuracies, 
              color = [encoding_colors[encoding] for encoding in encodings],
              edgecolor = 'k', linewidth = 0.5)

ax.set_ylim([0.0, 1.1])
ax.set_ylabel('Accuracy')
ax.grid()
ax.set_axisbelow(True)

for bar, acc in zip(bars, accuracies):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{acc:.0%}", ha = "center", va = "bottom", fontsize = 7)
    
plt.tight_layout()
plt.savefig('plots/accuracy_connectivity.png')
plt.close(fig)

for query_type in query_labels:
    # Plotting bar chart for query type accuracy
    weight, key, metric_label = query_labels[query_type]
    
    bucket = paths[query_type]
    optimal = [bucket[encoding]['optimal'] / bucket[encoding]['total'] if bucket[encoding]['total'] else 0 for encoding in encodings]
    exact = [bucket[encoding]['exact'] / bucket[encoding]['total'] if bucket[encoding]['total'] else 0 for encoding in encodings]
    
    x = range(len(encodings))
    bar_width = 0.35
    
    fig, ax = plt.subplots(figsize = (3.5, 3))
    bar_opt = ax.bar([i - bar_width/2 for i in x], optimal, bar_width, label = 'Optimal', color = 'tab:blue', edgecolor = 'k', linewidth = 0.5)
    bar_ext = ax.bar([i + bar_width/2 for i in x], exact, bar_width, label = 'Exact', color = 'tab:orange', edgecolor = 'k', linewidth = 0.5)
    
    for bar, acc in zip(bar_opt, optimal):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                    f"{acc:.0%}", ha = "center", va = "bottom", fontsize = 7)
        
    for bar, acc in zip(bar_ext, exact):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                    f"{acc:.0%}", ha = "center", va = "bottom", fontsize = 7)
        
    ax.set_xticks(list(x))
    ax.set_xticklabels([encoding_labels[encoding] for encoding in encodings])
    ax.set_ylim([0, 1.1])
    ax.set_ylabel('Accuracy')
    ax.grid(axis = "y", linestyle = "--", alpha = 0.5)
    ax.set_axisbelow(True)
    ax.legend(loc = "lower right", ncol = 2)
    plt.tight_layout()
    plt.savefig(f'plots/accuracy_{query_type}.png')
    plt.close(fig)
    
    # Plotting scatter for query type ratios
    ratios = {encoding: [] for encoding in encodings}
    
    for llm_response in llm_responses['responses'].values():
        if llm_response['meta']['query_type'] != query_type:
            continue
        
        reference_sol = reference_sols[llm_response['meta']['pair_idx']]
        path = extract_model_path(G, llm_response, reference_sol)
        
        if path is None: 
            continue
        
        total = reference_sol[query_type][key]
        if total  == 0:
            continue
        
        ratios[llm_response['meta']['encoding']].append(path_total(G, path, weight) / total)
        
        
    fig, ax = plt.subplots(figsize = (3.5, 3.0))
    all_ratios = []
    
    rng = Random(0)
    
    for x_center, encoding in enumerate(encodings):
        ratio = ratios[encoding]
        all_ratios.extend(ratio)
        
        xs = [x_center + rng.uniform(-0.1, 0.1) for r in ratio]
        
        ax.scatter(xs, ratio, s = 22, alpha = 0.75, color = encoding_colors[encoding], edgecolor = 'k', linewidth = 0.5, zorder = 3)
        
        if ratio:
            ax.hlines(median(ratio), x_center - 0.22, x_center + 0.22,
                      colors = 'k', linewidth = 0.5, zorder = 4)
    
    ax.set_xticks(range(len(encodings)))
    ax.set_xticklabels([f"{encoding_labels[encoding]}" for encoding in encodings])
    ylabel = 'Time Ratio' if query_type == 'fastest' else 'Cost Ratio'
    ax.set_ylabel(ylabel)
    ax.grid(axis = 'y', linestyle = '--', alpha = 0.4)
    ax.set_axisbelow(True)
    
    y_top = max(all_ratios) * 1.08 if all_ratios else 1.5
    ax.set_ylim(0.95, max(y_top, 1.15))
    
    plt.tight_layout()
    plt.savefig(f'plots/ratio_{query_type}.png')
    plt.close(fig)