import json
from pathlib import Path
from networkx.readwrite import json_graph
import networkx as nx
from graphify.cluster import cluster, score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from graphify.export import to_html

# Load graph
data = json.loads(Path('graphify-out/graph.json').read_text())
G = json_graph.node_link_graph(data, edges='links')

# Load or recompute analysis
analysis_path = Path('graphify-out/.graphify_analysis.json')
if analysis_path.exists():
    analysis = json.loads(analysis_path.read_text())
    communities = {int(k): v for k, v in analysis['communities'].items()}
    cohesion = {int(k): v for k, v in analysis['cohesion'].items()}
    gods = analysis['gods']
    surprises = analysis['surprises']
else:
    communities = cluster(G)
    cohesion = score_all(G, communities)
    gods = god_nodes(G)
    surprises = surprising_connections(G, communities)
    analysis = {'communities': {str(k): v for k, v in communities.items()},
                'cohesion': {str(k): v for k, v in cohesion.items()},
                'gods': gods, 'surprises': surprises}
    analysis_path.write_text(json.dumps(analysis, indent=2))

# Generate community labels from top nodes
labels = {}
for cid, members in communities.items():
    nodes_in_c = [n for n, c in communities.items() if c == cid]
    top_labels = [G.nodes[n].get('label', n) for n in nodes_in_c[:3]]
    labels[cid] = ' / '.join(top_labels) if top_labels else f'Community {cid}'

detection = {'total_files': 11, 'total_words': 1872, 'warning': None}
tokens = {'input': 0, 'output': 0}

# Generate report
report = generate(G, communities, cohesion, labels, gods, surprises, detection, tokens, '.')
Path('graphify-out/GRAPH_REPORT.md').write_text(report)
print('GRAPH_REPORT.md written')

# Generate HTML
if G.number_of_nodes() <= 5000:
    to_html(G, communities, 'graphify-out/graph.html', community_labels=labels)
    print('graph.html written')

print(f'Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, {len(communities)} communities')
