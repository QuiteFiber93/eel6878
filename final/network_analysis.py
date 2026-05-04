import csv
import networkx as nx
import random
import json

# Building the graph from edge list file
G = nx.DiGraph()
with open("network_graph.edgelist", "r", newline="") as f:
    
    reader = csv.DictReader(f)
    
    for row in reader:
        G.add_edge(
            row["source"],
            row["target"],
            time = int(row["time"]),
            cost = int(row["cost"]),
            weather = row["weather"],
        )

# Sampling nodes randomly for shipments
rng = random.Random(42) # 42 is the answer to the ultimate question of life, the universe, and everything

nodes = list(G.nodes())

# Change this to change the number of samples
n_samples = 32
sampled_pairs = rng.sample(
    [(source, target) for source in nodes for target in nodes if source != target],
    n_samples
)


# Pathing for route queries
def route_costs(G, path):
    
    """Return total time, cost, and the path itself."""
    
    # Ignores if the path is a single hop
    if path is None or len(path) < 2:
        return None
    
    # Computing total path length and path cost for each route
    days = sum(G[path[i]][path[i+1]]["time"] for i in range(len(path)-1))
    cost = sum(G[path[i]][path[i+1]]["cost"] for i in range(len(path)-1))
    
    return {"path": path, "total_days": days, "total_cost": cost}

# Actually computing true values for queries
results = []
for s, t in sampled_pairs:
    
    # Connectivity check
    # Only proceed to further queries if a path exists
    if not nx.has_path(G, s, t):
        results.append({
            "source": s, 
            "target": t, 
            "connected": False, 
            "fastest": None, 
            "cheapest": None
            })

        continue
    
    # Choosing optimal paths for existing routes
    fastest_path  = nx.shortest_path(G, s, t, weight = "time")
    cheapest_path = nx.shortest_path(G, s, t, weight = "cost")
    
    results.append({
        "source": s, 
        "target": t, 
        "connected": True, 
        "fastest": route_costs(G, fastest_path), 
        "cheapest": route_costs(G, cheapest_path),
    })

# Printing results
def delimeter(text):
    print("=" * 70 + "\n" + text + "\n" + "=" * 70)

# Connectivity
delimeter(f"CONNECTIVITY")

# Table header
print(f"{'#':>3}  {'PAIR':18s}  {'GROUND TRUTH':12s}")
print("-" * 40)

for i, r in enumerate(results, 1):
    answer = "Yes" if r["connected"] else "No"
    print(f"{i:>3}  {r['source']:>4} -> {r['target']:<8s}  {answer}")

connected_pairs   = [r for r in results if r["connected"]]
unconnected_pairs = [r for r in results if not r["connected"]]
print(f"\n  Connected: {len(connected_pairs)}   Unconnected: {len(unconnected_pairs)}")

# Fastest route results
delimeter('Fastest Route')

print(f"{'#':>3}  {'PAIR':18s}  {'FASTEST PATH':45s}  {'DAYS':>5}")
print("-" * 80)

for i, r in enumerate(connected_pairs, 1):
    f = r["fastest"]
    print(f"{i:>3}  {r['source']:>4} -> {r['target']:<8s}  "
          f"{' -> '.join(f['path']):45s}  {f['total_days']:>5}")


# Cheapest route results
delimeter('CHEAPEST ROUTE')

print(f"{'#':>3}  {'PAIR':18s}  {'CHEAPEST PATH':45s}  {'COST':>7}")
print("-" * 82)

for i, r in enumerate(connected_pairs, 1):
    c = r["cheapest"]
    print(f"{i:>3}  {r['source']:>4} -> {r['target']:<8s}  "
          f"{' -> '.join(c['path']):45s}  ${c['total_cost']:>6}")


# Writing truth solutinos to file

with open("ground_truth.json", "w") as f:
    json.dump(results, f, indent=2)

delimeter('SUMMARY')
print(f"Total sampled pairs:\t\t{len(results)}")
print(f"  Connectivity tests:\t\t{len(results)}")
print(f"  Fastest-route tests:\t\t{len(connected_pairs)}")
print(f"  Cheapest-route tests:\t\t{len(connected_pairs)}")