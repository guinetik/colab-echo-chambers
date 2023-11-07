class NetworkPlotter3D:
    def __init__(self, G, palette, communities, layout_function, pos=None):
        self.G = G
        self.palette = palette
        self.communities = communities
        self.layout_function = layout_function
        self.pos = pos
        # print(self.palette)
        self.edge_x = []
        self.edge_y = []
        self.edge_z = []
        self.node_x = []
        self.node_y = []
        self.node_z = []
        self.node_colors = []
        self.node_sizes = []
        self.hover_texts = []
        self._prepare_data()

    def _prepare_data(self):
        # Convert node names in the G to integers if they aren't
        # if not all(isinstance(node, int) for node in self.G.nodes()):
        #    mapping = {node: int(node) for node in self.G.nodes()}
        #    self.G = nx.relabel_nodes(self.G, mapping)

        # Compute persona colors
        self._compute_modularity_colors()

        # Compute node metrics
        self._compute_node_metrics()

        # Compute node sizes based on eigenvector centrality
        self.node_sizes = self._compute_node_sizes()

        # Compute 3D positions
        if self.pos is None:
            self.pos = self.layout_function(
                self.G, dim=3, communities=self.communities)

        # Extract edge positions
        self._extract_edge_positions()

        # Extract node positions and hover texts
        self._extract_node_positions_and_hover_texts()

    def _compute_persona_colors(self):
        persona_color = nx.get_node_attributes(self.G, 'persona')
        # print(persona_color)
        default_color = 'orange'  # Cor padrão para nós sem persona
        for node in self.G.nodes():
            if node in persona_color:
                self.G.nodes[node]['color'] = self.palette[persona_color[node]]
            else:
                self.G.nodes[node]['color'] = default_color
        self.node_colors = [self.G.nodes[node]['color']
                            for node in self.G.nodes()]
        # print(self.node_colors)

    def _compute_modularity_colors(self):
        modularity_color = {}
        # print(self.palette)
        for community_number, community in enumerate(self.communities):
            # print(community_number, community)
            for name in community:
                modularity_color[name] = self.palette[community_number % len(
                    self.palette)]
        # Ensure all nodes have a color
        default_color = "black"  # Default color for nodes not in any community
        for node in self.G.nodes():
            if node not in modularity_color:
                modularity_color[node] = default_color
        nx.set_node_attributes(self.G, modularity_color, 'color')
        self.node_colors = [modularity_color[node] for node in self.G.nodes()]

    def _compute_node_metrics(self):
        # Compute degree for each node
        degrees = dict(self.G.degree())
        nx.set_node_attributes(self.G, degrees, 'degree')

        # Compute eigenvector centrality for each node
        eigenvector_centrality = nx.eigenvector_centrality(self.G)
        nx.set_node_attributes(
            self.G, eigenvector_centrality, 'eigenvector_centrality')

        # Compute followers (in-degree) and following (out-degree) for each node
        followers = dict(self.G.in_degree())
        following = dict(self.G.out_degree())
        nx.set_node_attributes(self.G, followers, 'followers')
        nx.set_node_attributes(self.G, following, 'following')

    def _compute_node_sizes(self):
        centrality_values = [
            self.G.nodes[node]['eigenvector_centrality'] for node in self.G.nodes()]
        max_centrality = max(centrality_values)
        min_centrality = min(centrality_values)
        size_bounds = {'desired': {'lower': 5, 'upper': 50}, 'actual': {
            'lower': min_centrality, 'upper': max_centrality}}
        sizes = [size_bounds['desired']['lower'] + (x - size_bounds['actual']['lower']) * (size_bounds['desired']['upper'] - size_bounds['desired']['lower']) / (
            size_bounds['actual']['upper'] - size_bounds['actual']['lower']) for x in centrality_values]
        return sizes

    def _extract_edge_positions(self):
        for edge in self.G.edges():
            x0, y0, z0 = self.pos[edge[0]]
            x1, y1, z1 = self.pos[edge[1]]
            self.edge_x.extend([x0, x1, None])
            self.edge_y.extend([y0, y1, None])
            self.edge_z.extend([z0, z1, None])

    def _extract_node_positions_and_hover_texts(self):
        for node in self.G.nodes():
            self.node_x.append(self.pos[node][0])
            self.node_y.append(self.pos[node][1])
            self.node_z.append(self.pos[node][2])

            node_id_text = f"Node ID: {node}"
            community_text = f"Community: {self.G.nodes[node].get('modularity_class', 'N/A')}"
            degree_text = f"Degree: {self.G.nodes[node].get('degree', 'N/A')}"
            # Rounded to 4 decimal places
            eigenvector_text = f"Eigenvector Centrality: {self.G.nodes[node].get('eigenvector_centrality', 'N/A'):.4f}"
            followers_text = f"Followers: {self.G.nodes[node].get('followers', 'N/A')}"
            following_text = f"Following: {self.G.nodes[node].get('following', 'N/A')}"

            hover_info = f"{node_id_text}<br>{community_text}<br>{degree_text}<br>{eigenvector_text}<br>{followers_text}<br>{following_text}"
            self.hover_texts.append(hover_info)

    def plot(self, title="Network Plot", filename=None):
        # print(self.node_colors)
        # 0.5 is the opacity, adjust as needed
        edge_color_with_opacity = 'rgba(128, 128, 128, 0.8)'
        edge_trace = go.Scatter3d(
            x=self.edge_x,
            y=self.edge_y,
            z=self.edge_z,
            mode='lines',
            line=dict(width=0.5, color=edge_color_with_opacity),
            showlegend=False,
            hoverinfo='none'
        )
        node_trace = go.Scatter3d(x=self.node_x, y=self.node_y, z=self.node_z, mode='markers', marker=dict(
            size=self.node_sizes, color=self.node_colors, opacity=0.8), showlegend=False, text=self.hover_texts, hoverinfo='text')
        fig = go.Figure(data=[edge_trace, node_trace])
        print(self.communities)
        for community_number, members in enumerate(self.communities):
            # print(community_number)
            fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], mode='markers', marker=dict(
                size=10, color=self.palette[community_number]), name=f"Community {community_number + 1}"))
        # for persona, color in self.palette.items():
            # fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], mode='markers', marker=dict(size=10, color=color), name=persona.capitalize()))
        fig.update_layout(title={
            'text': title,
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {
                'size': 20,
                'color': 'black'
            }
        },
            scene=dict(aspectmode='data',
                       xaxis=dict(nticks=10, showspikes=False, showbackground=False,
                                  showline=False, zeroline=False, showgrid=False, showticklabels=False),
                       yaxis=dict(nticks=10, showspikes=False, showbackground=False,
                                  showline=False, zeroline=False, showgrid=False, showticklabels=False),
                       zaxis=dict(nticks=10, showspikes=False, showbackground=False, showline=False, zeroline=False, showgrid=False, showticklabels=False)),
            margin=dict(t=20, b=20, r=20, l=20),
            height=800)
        if filename:
            # Save the figure as an HTML file
            pyo.plot(fig, filename=filename, auto_open=False)
        fig.show()
