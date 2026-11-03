"""Step 1: generate and draw a balanced random splitter.

Parallel wires are allowed. Expansion has not yet been tested.
"""
# Counter counts repeated connections, such as two wires from I0 to U1.
from collections import Counter
# Path helps us save the picture beside this Python file.
from pathlib import Path
# random provides the shuffle operation used to choose the wiring.
import random

#plt for plotting, nx for graphs.
import matplotlib.pyplot as plt
import networkx as nx


def build_splitter(m=8, d=2, seed=42):
    """Each input has d wires per direction; each output receives 2*d."""
    if not isinstance(m, int) or m < 2 or m % 2:
        raise ValueError("m must be a positive even integer of at least 2.")
    if not isinstance(d, int) or d < 1:
        raise ValueError("d must be a positive integer.")

   # Use a local random generator so this function has its own random state.
    # A seed controls the choices; it does not guarantee good expansion.
    rng = random.Random(seed)

     # Multi = parallel wires are allowed between the same pair of switches.
    # Di = directed: every wire points from an input to an output.
    # Store m, d and seed as metadata so the drawing can read them later.
    graph = nx.MultiDiGraph(m=m, d=d, seed=seed)
     # Make switch names using list comprehensions.
     # // is integer division: 8 // 2 gives 4 outputs in each direction.
    inputs = [f"I{i}" for i in range(m)]
    up = [f"U{i}" for i in range(m // 2)]
    down = [f"D{i}" for i in range(m // 2)]

     # Add the switches before adding any wires.
    # group is a category attached to each switch, not a connection.
    graph.add_nodes_from(inputs, group="input")
    graph.add_nodes_from(up, group="up")
    graph.add_nodes_from(down, group="down")

    for direction, outputs in [("up", up), ("down", down)]:
        for _ in range(d):
            # Two slots per output give one slot per input in each round.
            slots = [output for output in outputs for _ in range(2)]
            rng.shuffle(slots)
            for source, target in zip(inputs, slots):
                graph.add_edge(source, target, direction=direction)

    return graph, inputs, up, down


def draw_splitter(graph, inputs, up, down):
    m = graph.graph["m"]
    d = graph.graph["d"]
    positions = {node: (0, m - 1 - i) for i, node in enumerate(inputs)}
    positions.update({node: (1, m - 1 - i) for i, node in enumerate(up)})
    positions.update({node: (1, m // 2 - 1 - i) for i, node in enumerate(down)})

    # Aggregate parallel wires for the picture, keeping all wires in graph.
    counts = Counter((source, target) for source, target in graph.edges())
    drawing = nx.DiGraph()
    drawing.add_nodes_from(graph.nodes())
    drawing.add_edges_from(counts)

    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor("#f7f8fa")
    ax.set_facecolor("#f7f8fa")
    for nodes, color in [(inputs, "#167d8d"), (up, "#3769a8"), (down, "#bd7b24")]:
        nx.draw_networkx_nodes(drawing, positions, nodelist=nodes,
                               node_color=color, node_size=650, ax=ax)
    nx.draw_networkx_edges(drawing, positions, ax=ax, node_size=650,
                           arrowsize=14, edge_color="#637888", alpha=0.45,
                           width=[0.7 + 0.45 * counts[edge] for edge in drawing.edges()])
    nx.draw_networkx_labels(drawing, positions, ax=ax,
                            font_color="white", font_size=10)
    nx.draw_networkx_edge_labels(
        drawing, positions, ax=ax,
        edge_labels={edge: f"{count} wires" for edge, count in counts.items() if count > 1},
        font_size=8, rotate=False,
    )

    ax.text(0, m - 0.15, "INPUTS", ha="center", weight="bold", color="#163047")
    ax.text(1.23, 3 * m / 4 - 0.5, "UP\nOUTPUTS", ha="center", color="#3769a8")
    ax.text(1.23, m / 4 - 0.5, "DOWN\nOUTPUTS", ha="center", color="#bd7b24")
    ax.set_title(f"Candidate splitter: {m} inputs | d = {d} | seed = {graph.graph['seed']}",
                 pad=28, color="#163047", fontsize=15, weight="bold")
    fig.text(0.5, 0.025,
             "Each input has d wires per direction. Labels show parallel wires. Expansion not tested.",
             ha="center", fontsize=9, color="#435567")
    ax.set_xlim(-0.25, 1.5)
    ax.set_ylim(-0.65, m + 0.1)
    ax.axis("off")
    fig.tight_layout(rect=(0, 0.05, 1, 0.98))
    output = Path(__file__).resolve().with_name("splitter.png")
    fig.savefig(output, dpi=200, facecolor=fig.get_facecolor())
    print(f"Diagram saved to: {output}")
    plt.show()


if __name__ == "__main__":
    graph, inputs, up, down = build_splitter()
    print(f"Inputs: {len(inputs)}")
    print(f"Up outputs: {len(up)} | Down outputs: {len(down)}")
    print(f"Wires (including parallel wires): {graph.number_of_edges()}")
    print("Expansion: not tested yet")
    draw_splitter(graph, inputs, up, down)
