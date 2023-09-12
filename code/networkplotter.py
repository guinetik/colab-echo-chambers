import networkx as nx
import numpy as np
from bokeh.io import show
from bokeh.models import Circle, MultiLine
from bokeh.plotting import figure
from bokeh.palettes import Blues8
from bokeh.models.graphs import from_networkx
from bokeh.models.graphs import NodesAndLinkedEdges

class NetworkPlotter:
    def __init__(self, graph_network, network_communities, title, palette=Blues8):
        self.graph_network = graph_network
        self.network_communities = network_communities
        self.title = title
        self.palette = palette

    def normalize(self, values, bounds):
        return [bounds['desired']['lower'] + (x - bounds['actual']['lower']) * (bounds['desired']['upper'] - bounds['desired']['lower']) / (bounds['actual']['upper'] - bounds['actual']['lower']) for x in values]

    def get_adjusted_node_size(self):
        degrees = nx.degree(self.graph_network)
        nx.set_node_attributes(self.graph_network, name='degree', values=dict(degrees))

        centrality = nx.eigenvector_centrality_numpy(self.graph_network)
        nx.set_node_attributes(self.graph_network, name='centrality', values=centrality)

        centrality_values = []
        degree_values = []

        for node in centrality:
            centrality_values.append(centrality[node])

        max_centrality = max(centrality_values)
        min_centrality = min(centrality_values)
        i = 0

        for node, degree in degrees:
            degree_values.append(degree)
            i += 1

        max_degree = max(degree_values)

        centrality_values = self.normalize(centrality_values, {'actual': {'lower': min_centrality, 'upper': max_centrality * 2}, 'desired': {'lower': 5, 'upper': 100}})
        sizes = {}
        i = 0

        for node, degree in degrees:
            sizes[node] = centrality_values[i]
            i += 1

        adjusted_node_size = dict([(node, sizes[node]) for node, degree in degrees])
        nx.set_node_attributes(self.graph_network, name='adjusted_node_size', values=adjusted_node_size)

    def plot_bokeh_network(self):
        for component in list(nx.connected_components(self.graph_network)):
            if len(component) < 3:
                for node in component:
                    self.graph_network.remove_node(node)

        self.get_adjusted_node_size()

        modularity_class = {}
        modularity_color = {}

        for community_number, community in enumerate(self.network_communities):
            for name in community:
                modularity_class[name] = community_number
                modularity_color[name] = self.palette[community_number % len(self.palette)]

        nx.set_node_attributes(self.graph_network, modularity_class, 'modularity_class')
        nx.set_node_attributes(self.graph_network, modularity_color, 'modularity_color')

        size_by_this_attribute = 'adjusted_node_size'
        color_by_this_attribute = 'modularity_color'

        node_highlight_color = 'white'
        edge_highlight_color = 'black'

        HOVER_TOOLTIPS = [
            ("user_id", "@index"),
            ("Degree", "@degree"),
            ("Centrality", "@centrality"),
            ("Modularity Class", "@modularity_class"),
            ("Modularity Color", "$color[swatch]:modularity_color"),
        ]

        plot = figure(tooltips=HOVER_TOOLTIPS,
                      sizing_mode="stretch_width",
                      tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom', height=600, title=self.title)

        layout = nx.nx_pydot.graphviz_layout(self.graph_network, prog="neato")

        network_graph = from_networkx(self.graph_network, layout, scale=25,
                                      k=len(self.graph_network.nodes()) * 1 / np.sqrt(len(self.graph_network.nodes())),
                                      center=(0, 0))

        network_graph.node_renderer.glyph = Circle(size=size_by_this_attribute, fill_color=color_by_this_attribute)
        network_graph.node_renderer.hover_glyph = Circle(size=size_by_this_attribute, fill_color=node_highlight_color, line_width=2)
        network_graph.node_renderer.selection_glyph = Circle(size=size_by_this_attribute, fill_color=node_highlight_color, line_width=2)

        network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.3, line_width=0.5)
        network_graph.edge_renderer.selection_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)
        network_graph.edge_renderer.hover_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)

        network_graph.selection_policy = NodesAndLinkedEdges()
        network_graph.inspection_policy = NodesAndLinkedEdges()

        plot.renderers.append(network_graph)

        show(plot)