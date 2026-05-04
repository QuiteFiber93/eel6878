'''
This code was created with the assistance of generative ai, as neither team member had any experience with claude api calls. 
'''

import csv
import json
import os
import re
import time
from pathlib import Path

import networkx as nx
import anthropic
from anthropic.types.messages.batch_create_params import Request
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming


# Config
edgelist   = "network_graph.edgelist"
true_results    = "route_benchmark.json"
prompt_template = "llm_prompt.txt"
output_file     = "llm_responses.json"

claude_model       = "claude-sonnet-4-5"
max_tokens  = 8192
POLL_SECS   = 45   # how often to check batch status

encodings   = ["edge_list", "adjacency_list", "incidence"]
query_types = ["connectivity", "fastest", "cheapest"]


# Build graph
G = nx.DiGraph()
with open(edgelist, "r", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        G.add_edge(
            row["source"], row["target"],
            time = int(row["time"]),
            cost = int(row["cost"]),
            weather = row["weather"],
        )


# Encodings (ported from the commented-out section of final_project_graph.py)
def edge_list_encoding(G: nx.DiGraph) -> str:
    lines = [
        "Directed Logistics Network — Edge List",
        "Format: SOURCE -> TARGET | time=Xd, cost=$Y, weather=W",
        "",
    ]
    for u, v, d in G.edges(data=True):
        lines.append(
            f"{u} -> {v} | time={d['time']}d, cost=${d['cost']}, "
            f"weather={d['weather']}"
        )
    return "\n".join(lines)


def adjacency_list_encoding(G: nx.DiGraph) -> str:
    lines = [
        "Directed Logistics Network — Adjacency List",
        "Each port lists its outgoing routes and attributes.",
        "",
    ]
    for node in G.nodes():
        successors = list(G.successors(node))
        if not successors:
            lines.append(f"{node}: (no outgoing routes — terminal port)")
        else:
            lines.append(f"{node}:")
            for nbr in successors:
                d = G[node][nbr]
                lines.append(
                    f"  -> {nbr} | time={d['time']}d, cost=${d['cost']}, "
                    f"weather={d['weather']}"
                )
        lines.append("")
    return "\n".join(lines).rstrip()


def incidence_encoding(G: nx.DiGraph) -> str:
    lines = [
        "Directed Logistics Network — Incidence Encoding",
        "Each port lists ALL incident routes (incoming + outgoing).",
        "",
    ]
    for node in G.nodes():
        in_edges  = list(G.in_edges(node, data=True))
        out_edges = list(G.out_edges(node, data=True))

        lines.append(f"{node}:")

        if in_edges:
            lines.append("  Incoming:")
            for u, _, d in in_edges:
                lines.append(
                    f"    {u} -> {node} | time={d['time']}d, cost=${d['cost']}, "
                    f"weather={d['weather']}"
                )
        else:
            lines.append("  Incoming: (none)")

        if out_edges:
            lines.append("  Outgoing:")
            for _, v, d in out_edges:
                lines.append(
                    f"    {node} -> {v} | time={d['time']}d, cost=${d['cost']}, "
                    f"weather={d['weather']}"
                )
        else:
            lines.append("  Outgoing: (none)")

        lines.append("")
    return "\n".join(lines).rstrip()


ENCODER_FUNCS = {
    "edge_list":      edge_list_encoding,
    "adjacency_list": adjacency_list_encoding,
    "incidence":      incidence_encoding,
}


# ---------------------------------------------------------------------------
# Per-query-type instructions
# ---------------------------------------------------------------------------
QUERY_INSTRUCTIONS = {
    "connectivity": (
        'Is there ANY directed path from {s} to {t}? '
        'Reply with ONLY a JSON object of the form '
        '{{"connected": true}} or {{"connected": false}}. '
        'No prose, no markdown, no code fences.'
    ),
    "fastest": (
        'What is the fastest (minimum total transit time in days) directed '
        'path from {s} to {t}? '
        'Reply with ONLY a JSON object of the form '
        '{{"path": ["{s}", "...", "{t}"]}} listing every node in order. '
        'No prose, no markdown, no code fences.'
    ),
    "cheapest": (
        'What is the cheapest (minimum total US-dollar cost) directed path '
        'from {s} to {t}? '
        'Reply with ONLY a JSON object of the form '
        '{{"path": ["{s}", "...", "{t}"]}} listing every node in order. '
        'No prose, no markdown, no code fences.'
    ),
}


def build_query(query_type: str, s: str, t: str) -> str:
    return QUERY_INSTRUCTIONS[query_type].format(s=s, t=t)


# ---------------------------------------------------------------------------
# Custom-id encoding
# ---------------------------------------------------------------------------
# custom_id format:  <pair_idx>__<query_type>__<encoding>__<source>_<target>
# (must be unique within the batch, and must round-trip cleanly)
def make_custom_id(pair_idx: int, query_type: str, encoding: str,
                   s: str, t: str) -> str:
    return f"{pair_idx:03d}__{query_type}__{encoding}__{s}_{t}"


def parse_custom_id(cid: str) -> dict:
    pair_idx, query_type, encoding, pair = cid.split("__")
    s, t = pair.split("_")
    return {
        "pair_idx":   int(pair_idx),
        "query_type": query_type,
        "encoding":   encoding,
        "source":     s,
        "target":     t,
    }


# ---------------------------------------------------------------------------
# Build all batch requests
# ---------------------------------------------------------------------------
def build_requests(G, ground_truth, prompt_template):
    encodings_text = {name: fn(G) for name, fn in ENCODER_FUNCS.items()}
    requests = []

    for pair_idx, gt in enumerate(ground_truth):
        s, t = gt["source"], gt["target"]

        for query_type in query_types:
            # Skip path queries for unconnected pairs — no well-defined answer.
            if query_type in ("fastest", "cheapest") and not gt["connected"]:
                continue

            query_text = build_query(query_type, s, t)

            for encoding in encodings:
                # Use str.replace rather than .format because the template
                # contains literal '{Low, Medium, High}' which would break
                # PEP-3101 formatting.
                prompt = (
                    prompt_template
                    .replace("{encoding}", encodings_text[encoding])
                    .replace("{query}",    query_text)
                )
                cid = make_custom_id(pair_idx, query_type, encoding, s, t)

                requests.append(Request(
                    custom_id=cid,
                    params=MessageCreateParamsNonStreaming(
                        model=claude_model,
                        max_tokens=max_tokens,
                        messages=[{"role": "user", "content": prompt}],
                    ),
                ))
    return requests


# ---------------------------------------------------------------------------
# Submit + poll + collect
# ---------------------------------------------------------------------------
def run_batch(requests):
    client = anthropic.Anthropic()

    print(f"Submitting batch of {len(requests)} requests...")
    batch = client.messages.batches.create(requests=requests)
    print(f"Batch ID: {batch.id}  status: {batch.processing_status}")

    while True:
        batch = client.messages.batches.retrieve(batch.id)
        if batch.processing_status == "ended":
            break
        counts = batch.request_counts
        print(f"  ...processing  "
              f"succeeded={counts.succeeded}  errored={counts.errored}  "
              f"processing={counts.processing}  expired={counts.expired}  "
              f"canceled={counts.canceled}")
        time.sleep(POLL_SECS)

    print("Batch ended. Streaming results...")
    out = {}
    for entry in client.messages.batches.results(batch.id):
        cid    = entry.custom_id
        result = entry.result

        record = {
            "custom_id":   cid,
            "meta":        parse_custom_id(cid),
            "result_type": result.type,
        }

        if result.type == "succeeded":
            # Concatenate any text blocks (usually one).
            text = "".join(
                block.text for block in result.message.content
                if block.type == "text"
            )
            record["raw_text"]  = text
            record["parsed"]    = try_parse_json(text)
            record["usage"]     = {
                "input_tokens":  result.message.usage.input_tokens,
                "output_tokens": result.message.usage.output_tokens,
            }
        else:
            # errored / expired / canceled
            record["raw_text"] = None
            record["parsed"]   = None
            record["error"]    = getattr(result, "error", None) and \
                                 result.error.model_dump()
        out[cid] = record

    return batch.id, out


# ---------------------------------------------------------------------------
# JSON parsing — the model is asked to emit pure JSON, but we defensively
# strip code fences and pull the first {...} block if it ignored that.
# ---------------------------------------------------------------------------
JSON_OBJ_RE = re.compile(r"\{.*\}", re.DOTALL)

def try_parse_json(text: str):
    if text is None:
        return None
    cleaned = text.strip()
    # Strip ```json ... ``` or ``` ... ``` fences if present.
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except Exception:
        m = JSON_OBJ_RE.search(cleaned)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                return None
        return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit(
            "ANTHROPIC_API_KEY not set. Run:\n  export ANTHROPIC_API_KEY=..."
        )

    ground_truth = json.loads(Path(true_results).read_text())
    prompt_template = Path(prompt_template).read_text()

    n_connected = sum(1 for r in ground_truth if r["connected"])
    expected = (
        len(ground_truth) * len(encodings)            # connectivity (all pairs)
        + n_connected     * len(encodings) * 2        # fastest + cheapest
    )
    print(
        f"Pairs: {len(ground_truth)} "
        f"(connected: {n_connected}, unconnected: {len(ground_truth) - n_connected})"
    )
    print(f"Expected total requests: {expected}")

    requests = build_requests(G, ground_truth, prompt_template)
    assert len(requests) == expected, (
        f"Built {len(requests)} requests, expected {expected}"
    )

    batch_id, results = run_batch(requests)

    # Persist with the ground truth alongside, so the analyzer is one file in.
    payload = {
        "batch_id":    batch_id,
        "model":       claude_model,
        "encodings":   encodings,
        "query_types": query_types,
        "ground_truth": ground_truth,
        "responses":   results,
    }
    Path(output_file).write_text(json.dumps(payload, indent=2))

    succeeded = sum(1 for r in results.values() if r["result_type"] == "succeeded")
    print(f"\nSaved {len(results)} responses to {output_file}")
    print(f"  succeeded: {succeeded}    other: {len(results) - succeeded}")


if __name__ == "__main__":
    main()