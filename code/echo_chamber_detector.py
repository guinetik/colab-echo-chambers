class EchoChamberDetector:
    def __init__(self, nodes_df, edges_df, events_df, colab_comments_df, colab_likes_df, colab_updown_df, strategy,
                 min_community_density=0.5, min_community_size=3, communities=None):
        self.nodes = nodes_df
        self.edges = edges_df
        self.events = events_df
        self.colab_comments = colab_comments_df
        self.colab_likes = colab_likes_df
        self.colab_updown = colab_updown_df
        self.G = nx.from_pandas_edgelist(self.edges, 'source', 'target', create_using=nx.DiGraph())
        self.strategy = strategy
        self.communities = communities
        self.min_community_density = min_community_density
        self.min_community_size = min_community_size
        self.echo_chambers = []

    def get_unique_event_types_for_user_from_df(self, user_id, dataframe):
        return dataframe[dataframe['colab_user_id_from'] == user_id]['event_type_id'].unique()

    def get_all_unique_event_types_for_user(self, user_id):
        event_types_from_events = self.events[self.events['colab_user_id']
                                              == user_id]['event_type_id'].unique()
        event_types_from_comments = self.get_unique_event_types_for_user_from_df(
            user_id, self.colab_comments)
        event_types_from_likes = self.get_unique_event_types_for_user_from_df(
            user_id, self.colab_likes)
        event_types_from_updown = self.get_unique_event_types_for_user_from_df(
            user_id, self.colab_updown)
        all_event_types = np.concatenate([event_types_from_events, event_types_from_comments,
                                          event_types_from_likes, event_types_from_updown])
        # Convert all elements to strings
        all_event_types_str = [str(event_type) for event_type in all_event_types]

        return np.unique(all_event_types_str)

    def get_all_scores_for_user(self, user_id):
        scores_from_events = self.events[self.events['colab_user_id']
                                         == user_id]['score'].values
        updown_votes = self.colab_updown[self.colab_updown['colab_user_id_from'] == user_id]
        scores_from_updown = np.where(updown_votes['vote'] == 'down', -1, 1)
        all_scores = np.concatenate([scores_from_events, scores_from_updown])
        return all_scores

    def get_persona_for_user(self, user_id):
        user_events = self.events[self.events['colab_user_id'] == user_id]
        if not user_events.empty:
            return user_events['persona'].iloc[0]
        else:
            return None

    def calculate_community_density(self, community):
        edges = [(n1, n2) for n1 in community for n2 in community if n1 !=
                 n2 and self.G.has_edge(n1, n2)]
        density = len(edges) / (len(community) * (len(community) - 1))
        return density

    def calculate_modularity(self, G):
        """
        Calcula a modularidade do grafo.
        :param G: O grafo.
        :return: O valor da modularidade.
        """
        ug = G.to_undirected()
        # Detecção de comunidades usando o algoritmo de Louvain
        partition = community_louvain.best_partition(ug)

        # Calculando a modularidade
        modularity = community_louvain.modularity(partition, ug)
        print(f"modularity {modularity}")
        return modularity

    def calculate_global_gec(self):
        total_gec = 0
        total_weight = 0

        for community in self.communities:
            community_size = len(community)
            community_gec = self.calculate_community_gec(community)

            # Weighted sum of GEC, weighted by the size of each community
            total_gec += community_gec * community_size
            total_weight += community_size

        # Calculate the weighted average GEC
        global_gec = total_gec / total_weight if total_weight > 0 else 0
        print(f"global_gec {global_gec}")
        return global_gec

    def calculate_external_connections(self, community):
        external_connections = 0
        possible_connections = 0
        for node in community:
            for neighbor in self.G.neighbors(node):
                if neighbor not in community:
                    external_connections += 1
                possible_connections += 1
        if possible_connections > 0:
            factor = external_connections / possible_connections
        else:
            factor = 0.0
        return factor

    def calculate_homogeneity_of_opinions(self, community):
        # Obter todas as pontuações de opinião dos membros da comunidade
        all_scores = [score for user in community for score in self.get_all_scores_for_user(user)]

        # Filtrar out NaN values
        all_scores = [score for score in all_scores if not np.isnan(score)]

        # Se não houver pontuações suficientes, retorne 1 (máxima homogeneidade por padrão)
        if len(all_scores) <= 1:
            return 1

        # Calcular o desvio padrão das pontuações
        homogeneity = np.std(all_scores)
        #print(f"calculate_homogeneity_of_opinions {homogeneity}")
        return homogeneity


    def calculate_echo_chamber_metrics(self, community):
        # Calculate individual metrics
        density = self.calculate_community_density(community)
        homogeneity = self.calculate_homogeneity_of_opinions(community)
        external_connections = self.calculate_external_connections(community)
        ecc = self.calculate_community_ecc(community)
        gec = self.global_gec  # Global Echo Chamber factor
        average_exposure = self.calculate_community_exposure(community)

        # Echo chamber strength calculation
        strength = np.exp(
            self.beta1 * density +
            self.beta2 * homogeneity +
            self.beta3 * external_connections +
            self.beta4 * ecc +
            self.beta5 * gec +
            self.beta6 * average_exposure +
            self.beta7  
        )

        # Create a dictionary to store all metrics including strength
        echo_chamber_metrics = {
            'echo_chamber_strength': round(strength,4),
            'density': round(density,4),
            'homogeneity': round(homogeneity,4),
            'external_connections': round(external_connections,4),
            'ecc': round(ecc,4),
            'gec': round(gec,4),
            'average_exposure': round(average_exposure,4),
            'factor': round(strength,4)
        }

        return echo_chamber_metrics


    def calculate_graph_echo_chamber_strength(self):
        # Extract the largest connected component as a subgraph
        largest_cc = max(nx.connected_components(self.G.to_undirected() ), key=len)
        subgraph = G.subgraph(largest_cc)

        # Filter nodes with a degree (in + out in a directed graph) of 3 or more
        filtered_nodes = [node for node, degree in subgraph.degree() if degree >= 3]

        # Create a subgraph with only those filtered nodes
        filtered_subgraph = subgraph.subgraph(filtered_nodes)
        community = list(filtered_subgraph.nodes)
        ##
        density = nx.density(self.G)
        #print(f"graph density: {density}")
        homogeneity = self.calculate_homogeneity_of_opinions(community)
        #print(f"graph homogeneity: {homogeneity}")
        eig_centralities = nx.eigenvector_centrality_numpy(G)
        external_connections = median(eig_centralities.values())
        #print(f"graph external_connections: {external_connections}")
        ecc = self.calculate_community_ecc(community)
        #print(f"graph ecc: {ecc}")
        self.global_gec = self.calculate_global_gec()
        #print(f"graph gec: {gec}")
        average_exposure = self.calculate_community_exposure(community)
        #print(f"graph average_exposure: {average_exposure}")
        strength = np.exp(
            self.beta1 * density +
            self.beta2 * homogeneity +
            self.beta3 * external_connections +
            self.beta4 * ecc +
            self.beta5 * self.global_gec +
            self.beta6 * average_exposure +
            beta7
        )
        print(f"calculate_graph_echo_chamber_strength {strength}")
        return strength

    def is_echo_chamber(self, community):
        if not hasattr(self, 'graph_strength'):
          self.graph_strength = self.calculate_graph_echo_chamber_strength()
        community_strength = self.calculate_echo_chamber_strength(community)
        return community_strength >= self.graph_strength

    def derive_betas(self, G):
        # Beta1 - Coeficiente de Agrupamento Médio
        avg_clustering_coeff = nx.average_clustering(G)
        beta1 = avg_clustering_coeff  # Ou um valor inicial de 0.171, conforme o contexto

        # Beta2 - Homogeneidade das Opiniões
        num_communities = len(list(nx.community.greedy_modularity_communities(G)))
        beta2 = 1 / num_communities  # Ou um valor inicial de 1/352

        # Beta3 - Conexões Externas
        num_weakly_connected_components = nx.number_weakly_connected_components(G)
        beta3 = 1 / num_weakly_connected_components  # Ou um valor inicial de 1/329

        # Bfeta4 - Efeito dos Influenciadores
        eig_centralities = nx.eigenvector_centrality_numpy(G)
        median_centrality = median(eig_centralities.values())
        beta4 = median_centrality
        # Beta5 - Exposição Média
        if nx.is_connected(G.to_undirected()):
            avg_path_length = nx.average_shortest_path_length(G)
        else:
            avg_path_length = 1  # Ou algum outro valor de fallback
        beta5 = avg_path_length  # Ou um valor inicial de 5.6236

        # Beta6 - GEC (Modularidade)
        # Nota: Modularidade pode ser calculada usando algoritmos de detecção de comunidades
        modularity = self.calculate_modularity(G)
        beta6 = modularity  # Ou um valor inicial de 0.683
        beta7 = 1 / len(self.G.nodes)

        return beta1, beta2, beta3, beta4, beta5, beta6, beta7

    def calculate_community_ecc(self, community):
        scores = [self.get_all_scores_for_user(member) for member in community]
        all_scores = [score for sublist in scores for score in sublist]
        if not all_scores or np.all(np.isnan(all_scores)):
            return 0
        ecc = np.nanstd(all_scores)
        #print(f"calculate_community_ecc {ecc}")
        return ecc

    def calculate_community_gec(self, community):
        #print("Calculating all scores...")
        scores = [self.get_all_scores_for_user(member) for member in community]

        #print("Flattening all scores...")
        # Flatten the list, ignoring empty arrays and replacing NaNs with 0
        all_scores = [np.nan_to_num(score) for sublist in scores for score in sublist if len(sublist) > 0]

        # Check if all_scores is empty
        if not all_scores:
            return 0

        #print("Pairwise product sum...")
        # Calculate the sum of products of scores for all pairs of users
        pairwise_product_sum = sum(a * b for a, b in combinations(all_scores, 2))
        #print(f"Pairwise product sum: {pairwise_product_sum}")

        # Normalize by the number of pairs
        number_of_pairs = len(list(combinations(all_scores, 2)))
        #print(f"Number of pairs: {number_of_pairs}")
        gec = pairwise_product_sum / number_of_pairs if number_of_pairs > 0 else 0
        #print(f"calculate_community_gec {gec}")
        return gec


    def calculate_community_exposure(self, community):
        all_community_event_types = set()
        for member in community:
            member_event_types = self.get_all_unique_event_types_for_user(
                member)
            all_community_event_types.update(member_event_types)
        total_community_event_types = len(all_community_event_types)
        if total_community_event_types == 0:
            return 0
        individual_exposures = []
        for member in community:
            member_event_types = self.get_all_unique_event_types_for_user(
                member)
            member_exposure = len(set(member_event_types)) / \
                total_community_event_types
            individual_exposures.append(member_exposure)
        average_exposure = sum(individual_exposures) / len(community)
        #print(f"calculate_community_exposure {average_exposure}")
        return average_exposure

    def identify_echo_chambers(self, beta1=1.0, beta2=1.0, beta3=1.0, beta4=1.0, beta5=1.0, beta6=1.0, beta7=1.0):
        self.beta1 = beta1
        self.beta2 = beta2
        self.beta3 = beta3
        self.beta4 = beta4
        self.beta5 = beta5
        self.beta6 = beta6
        self.beta7 = beta7
        if self.communities is None:
          print("Calculating communities")
          self.communities = self.strategy.detect_communities(self.G)

        print('Number of communities before filtering:', len(self.communities))

        # Filter communities based on the minimum size requirement
        self.communities = [community for community in self.communities if len(community) >= self.min_community_size]

        print('Number of communities after filtering:', len(self.communities))

        self.echo_chambers = []
        self.graph_strength = self.calculate_graph_echo_chamber_strength()
        #self.global_gec = 0
        all_communities_metrics = [self.calculate_echo_chamber_metrics(community) for community in self.communities]
        print(f"all_communities_metrics: {all_communities_metrics}")
        community_percentiles = self.compare_community_metrics(all_communities_metrics)
        print(f"community_percentiles: {community_percentiles}")
        return self.echo_chambers