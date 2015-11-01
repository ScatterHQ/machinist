if __name__ == '__main__':
    from spike import main
    raise SystemExit(main())

from sys import argv
from networkx import (
    DiGraph, to_agraph,
    draw_networkx_edges, draw_networkx_nodes, draw_networkx_labels,
    draw_networkx_edge_labels,
)
from twisted.python.reflect import namedAny


def add_states(graph, table):
    for (state, transition) in table.table.items():
        graph.add_node(state.name)
    return graph


def add_edges(graph, table):
    for (from_state, transitions) in table.table.items():
        for (input_symbol, transition) in transitions.items():
            graph.add_edge(
                from_state.name, transition.nextState.name,
                label=input_symbol.name,
            )
    return graph


def render_graphviz(graph_name, graph):
    graph = graph.copy()
    # XXX Set colors on nodes and labels so you can tell them apart in the visualization
    a = to_agraph(graph)
    a.layout("dot")
    a.draw(graph_name + ".machinist.ps")


def render_matplotlib(graph_name, graph):
    from matplotlib import pyplot as plt
    from networkx import spring_layout, graphviz_layout, draw_networkx, draw_spring, get_edge_attributes
    plt.rcParams['text.usetex'] = False
    plt.figure(figsize=(16, 16))
    pos = spring_layout(graph)

    # Yea, just a giant heap of global mutable state.  Why not, anyway?
    draw_networkx_edges(
        graph,
        pos,
        alpha=0.3,
        # width=edgewidth,
        edge_color='m',
    )
    draw_networkx_nodes(
        graph,
        pos,
        # node_size=nodesize,
        node_color='w',
        alpha=0.4,
    )
    draw_networkx_labels(
        graph,
        pos,
    )
    draw_networkx_edge_labels(
        graph,
        pos,
        # This is where things screw up.  get_edge_attributes returns a
        # different data structure for MultiDiGraphs than for DiGraphs.
        # draw_networkx_edge_labels can't deal with the difference.
        edge_labels=get_edge_attributes(graph, "label"),
    )
    # draw_spring(graph)
    font = {
        'fontname'   : 'Helvetica',
        'color'      : 'k',
        'fontweight' : 'bold',
        'fontsize'   : 14,
    }
    plt.title(graph_name, font)
    plt.savefig(graph_name + ".machinist.png", dpi=75)


renderers = {
    "graphviz": render_graphviz,
    "matplotlib": render_matplotlib,
}


def main():
    table = namedAny(argv[1])

    # matplotlib renderer has problems with MultiDiGraph.  State machine may
    # well have multiple transitions between a particular state pair, though
    # ... Use a DiGraph so something gets rendered, even if it's wrong (!!!)
    g = add_states(DiGraph(), table)
    g = add_edges(g, table)

    renderers[argv[2]](argv[1], g)
