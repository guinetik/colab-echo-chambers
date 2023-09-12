from abc import ABC, abstractmethod

class EchoChamberVisualizer:
  def __init__(self, graph_network, centrality_strategy, layout_strategy):
      self.graph_network = graph_network
      self.centrality_strategy = centrality_strategy
      self.layout_strategy = layout_strategy
      
  def plot_bokeh_echo_chamber(self, network_communities, title):
      self.adjust_node_size_for_echo_chambers()
      modularity_class = {}
      modularity_color = {}
      palette = Category20[10]

      for community_number, community in enumerate(network_communities):
          for name in community:
              modularity_class[name] = community_number
              modularity_color[name] = palette[community_number % len(palette)]

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
          ("In Echo Chamber", "@is_echo_chamber_node"),
          ("Modularity Class", "@modularity_class"),
          ("Modularity Color", "$color[swatch]:modularity_color"),
      ]

      plot = figure(tooltips=HOVER_TOOLTIPS, sizing_mode="stretch_width", tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom', height=600, title=title)

      layout = self.layout_strategy.configure_layout(self.graph_network)

      network_graph = from_networkx(self.graph_network, layout, scale=10)

      network_graph.node_renderer.glyph = Circle(size=size_by_this_attribute, fill_color={'field': color_by_this_attribute})
      network_graph.node_renderer.hover_glyph = Circle(size=size_by_this_attribute, fill_color=node_highlight_color, line_width=2)
      network_graph.node_renderer.selection_glyph = Circle(size=size_by_this_attribute, fill_color=node_highlight_color, line_width=2)

      network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=0.5)
      network_graph.edge_renderer.selection_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)
      network_graph.edge_renderer.hover_glyph = MultiLine(line_color=edge_highlight_color, line_width=2)

      network_graph.selection_policy = NodesAndLinkedEdges()
      network_graph.inspection_policy = NodesAndLinkedEdges()

      main_hub_color = "white"

      network_graph.node_renderer.data_source.data['modularity_color'] = [modularity_color.get(node, main_hub_color) for node in self.graph_network.nodes()]
      network_graph.node_renderer.data_source.data['modularity_color'] = [color if self.graph_network.nodes[node].get('is_echo_chamber_node', False) else main_hub_color for node, color in zip(self.graph_network.nodes(), network_graph.node_renderer.data_source.data['modularity_color'])]

      plot.renderers.append(network_graph)

      show(plot)
  
  def plot(self, network_communities, title, plot_type=PlotType.BOKEH, options=None):
        self.adjust_node_size_for_echo_chambers()
        modularity_class = {}
        modularity_color = {}
        palette = Category20[10]

        for community_number, community in enumerate(network_communities):
            for name in community:
                modularity_class[name] = community_number
                modularity_color[name] = palette[community_number % len(palette)]

        nx.set_node_attributes(self.graph_network, modularity_class, 'modularity_class')
        nx.set_node_attributes(self.graph_network, modularity_color, 'modularity_color')

        if options is None:
            options = {}

        layout = self.layout_strategy.configure_layout(self.graph_network)
        options['layout'] = layout

        plot = GraphPlotFactory.create_plot(plot_type, options)
        plot.plot(self.graph_network)

    class PlotType(Enum):
        BOKEH = "bokeh"
        MATPLOTLIB = "matplotlib"

    class BokehPlot:
        def __init__(self, options):
            self.options = options

        def plot(self, graph_network):
            tooltips = self.options.get('tooltips', [])
            if 'tools' not in self.options:
                self.options['tools'] = []
            hover_tool = HoverTool(tooltips=tooltips)
            self.options['tools'].append(hover_tool)
            plot = figure(**self.options)
            layout = self.options.get('layout')
            network_graph = from_networkx(graph_network, layout, scale=10)
            network_graph.node_renderer.glyph = Circle(size=5, fill_color='orange')
            network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=0.5)
            network_graph.selection_policy = NodesAndLinkedEdges()
            network_graph.inspection_policy = NodesAndLinkedEdges()
            plot.renderers.append(network_graph)
            show(plot)

    class MatPlot:
        def __init__(self, options):
            self.options = options

        def plot(self, graph_network):
            plt.figure()
            pos = nx.spring_layout(graph_network)
            nx.draw_networkx(graph_network, pos, arrows=True, **self.options)
            plt.show()

    class GraphPlotFactory:
        @staticmethod
        def create_plot(plot_type, options):
            if plot_type == PlotType.BOKEH:
                return EchoChamberVisualizer.BokehPlot(options)
            elif plot_type == PlotType.MATPLOTLIB:
                return EchoChamberVisualizer.MatPlot(options)
            else:
                raise ValueError("Invalid plot type")

  class CentralityStrategy(ABC):
      def __init__(self, min_size, max_size):
          self.min_size = min_size
          self.max_size = max_size

      @abstractmethod
      def compute(self, graph_network):
          pass

      def _normalize_centrality(self, centrality):
          min_centrality = min(centrality.values())
          max_centrality = max(centrality.values())
          sizes = {}
          for node, centrality in centrality.items():
              normalized_centrality = (centrality - min_centrality) / (max_centrality - min_centrality)
              size = self.min_size + normalized_centrality * (self.max_size - self.min_size)
              sizes[node] = size
          return sizes

  class DegreeCentralityStrategy(CentralityStrategy):
      def compute(self, graph_network):
          centrality = nx.degree_centrality(graph_network)
          return self._normalize_centrality(centrality)

  class ClosenessCentralityStrategy(CentralityStrategy):
      def compute(self, graph_network):
          centrality = nx.closeness_centrality(graph_network)
          return self._normalize_centrality(centrality)

  class BetweennessCentralityStrategy(CentralityStrategy):
      def compute(self, graph_network):
          centrality = nx.betweenness_centrality(graph_network)
          return self._normalize_centrality(centrality)

  class EigenvectorCentralityStrategy(CentralityStrategy):
      def compute(self, graph_network):
          centrality = nx.eigenvector_centrality(graph_network, max_iter=500)
          return self._normalize_centrality(centrality)

  def adjust_node_size_for_echo_chambers(self):
      sizes = self.centrality_strategy.compute(self.graph_network)
      nx.set_node_attributes(self.graph_network, name='adjusted_node_size', values=sizes)

  class LayoutStrategy(ABC):
      @abstractmethod
      def configure_layout(self, graph_network):
          pass

  class SpringLayoutStrategy(LayoutStrategy):
    def configure_layout(self, graph_network):
        return nx.spring_layout(graph_network, seed=42)

  class KamadaKawaiLayoutStrategy(LayoutStrategy):
      def configure_layout(self, graph_network):
          return nx.kamada_kawai_layout(graph_network)

  class CircularLayoutStrategy(LayoutStrategy):
      def configure_layout(self, graph_network):
          return nx.circular_layout(graph_network)

  class NeatoLayoutStrategy(LayoutStrategy):
      def configure_layout(self, graph_network):
          return nx.nx_pydot.graphviz_layout(graph_network, prog="neato")

  class SpectralLayoutStrategy(LayoutStrategy):
      def configure_layout(self, graph_network):
          return nx.spectral_layout(graph_network)

  class DotLayoutStrategy(LayoutStrategy):
      def configure_layout(self, graph_network):
          return nx.nx_pydot.graphviz_layout(graph_network, prog="dot")

  class SFDPLayoutStrategy(LayoutStrategy):
      def configure_layout(self, graph_network):
          return nx.nx_pydot.graphviz_layout(graph_network, prog="sfdp")


  # Adicione outras estratégias de layout conforme necessário 
############################################################################################
network_communities = list(nx.algorithms.community.greedy_modularity_communities(G))
layout_strategy = EchoChamberVisualizer.KamadaKawaiLayoutStrategy()
centrality_strategy = EchoChamberVisualizer.EigenvectorCentralityStrategy(10, 20)
visualizer = EchoChamberVisualizer(G, centrality_strategy, layout_strategy)
options = {
    'tooltips': [
        ("user_id", "@index"),
        ("Degree", "@degree"),
        ("Centrality", "@centrality"),
        ("In Echo Chamber", "@is_echo_chamber_node"),
        ("Modularity Class", "@modularity_class"),
        ("Modularity Color", "$color[swatch]:modularity_color"),
    ],
    'sizing_mode': "stretch_width",
    'tools': ["pan", "wheel_zoom", "save", "reset"],
    'active_scroll': 'wheel_zoom',
    'height': 600,
    'title': 'Network'
}
visualizer.plot(network_communities, 'Network', plot_type=EchoChamberVisualizer.PlotType.BOKEH, options=options)