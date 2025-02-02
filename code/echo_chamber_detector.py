class EchoChamberDetector:
    def __init__(self, nodes_df, edges_df, events_df, colab_comments_df, colab_likes_df, colab_updown_df, strategy, classifier=None, communities=None):
        self.nodes = nodes_df
        self.edges = edges_df
        self.events = events_df
        self.colab_comments = colab_comments_df
        self.colab_likes = colab_likes_df
        self.colab_updown = colab_updown_df
        self.G = nx.from_pandas_edgelist(self.edges, 'source', 'target', create_using=nx.DiGraph())
        self.strategy = strategy
        self.classifier = classifier
        self.communities = communities
        self.min_community_size = 3
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
        #scores_from_updown = np.where(updown_votes['vote'] == 'down', -1, 1)
        scores_from_updown = []
        all_scores = np.concatenate([scores_from_events, scores_from_updown])
        return all_scores

    def get_persona_for_user(self, user_id):
        user_events = self.events[self.events['colab_user_id'] == user_id]
        if not user_events.empty:
            return user_events['persona'].iloc[0]
        else:
            return None

    def get_events_created_by_user(self, user_id):
        return self.events[self.events['colab_user_id'] == user_id]

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
        #print(f"graph modularity {modularity}")
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
        #print(f"Global Echo Chamber Coefficient {global_gec}")
        return global_gec

    def calculate_average_external_connections(self, G):
        external_connections = {}  # A dictionary to store external connections for each node

        # Initialize external connections count to 0 for all nodes
        for node in G.nodes():
            external_connections[node] = 0

        # Calculate external connections for each node
        for edge in G.edges():
            source, target = edge
            if source not in G.nodes() or target not in G.nodes():
                # One of the nodes is external, increment external connections count
                if source not in G.nodes():
                    external_connections[target] += 1
                if target not in G.nodes():
                    external_connections[source] += 1

        # Calculate the total external connections count
        total_external_connections = sum(external_connections.values())

        # Calculate the average external connections
        average_external_connections = total_external_connections / len(G.nodes())

        return average_external_connections

    def calculate_external_connections(self, community):
        external_connections = 0
        possible_connections = 0
        for node in community:
            for neighbor in self.G.neighbors(node):
                if neighbor not in community:
                    external_connections += 1
                possible_connections += 1
        if possible_connections > 0:
            factor = 1.0 - (external_connections / possible_connections)
        else:
            factor = 1.0
        return factor

    def calculate_homogeneity_of_opinions(self,community):
        # Obter todas as pontuações de opinião dos membros da comunidade
        all_scores = [score for user in community for score in self.get_all_scores_for_user(user)]

        # Filtrar out NaN values
        all_scores = [score for score in all_scores if not np.isnan(score)]
        #print("ALL SCORES", all_scores)

        # Se não houver pontuações suficientes
        if len(all_scores) <= 1:
            return 0

        # Calculate weighted homogeneity
        total_weight = len(all_scores)
        weighted_std = np.std(all_scores) * total_weight

        # Normalize the weighted std to a value between 0 and 1
        normalized_weighted_std = 1 / (1 + weighted_std)

        return normalized_weighted_std


    def calculate_echo_chamber_metrics(self, community):
        print(f"calculate_echo_chamber_metrics {community}")
        # Calculate individual metrics
        density = self.calculate_community_density(community)
        homogeneity = self.calculate_homogeneity_of_opinions(community)
        external_connections = self.calculate_external_connections(community)
        influencers = self.calculate_community_influence(self.G, community)
        ecc = self.calculate_ecc_for_community(community)
        gec = self.global_gec  # Global Echo Chamber factor
        average_exposure = self.calculate_community_exposure(community)

        # Echo chamber strength calculation
        strength = np.exp(
            self.beta1 * density +
            self.beta2 * homogeneity +
            self.beta3 * external_connections +
            self.beta4 * influencers +
            self.beta5 * average_exposure  +
            self.beta6 * gec +
            self.beta7 * ecc
        )

        # Create a dictionary to store all metrics including strength
        echo_chamber_metrics = {
            'graph_size': len(self.G.nodes()),
            'echo_chamber_strength': round(strength,4),
            'density': round(density,4),
            'homogeneity': round(homogeneity,4),
            'external_connections': round(external_connections,4),
            'ecc': round(ecc,4),
            'gec': round(gec,4),
            'average_exposure': round(average_exposure,4),
            'size': len(community)
        }
        print(f"metrics {echo_chamber_metrics}")
        return echo_chamber_metrics


    def calculate_graph_echo_chamber_strength(self):
        #print("Calculating graph echo chamber strength...")
        # Extract the largest connected component as a subgraph
        largest_cc = max(nx.connected_components(self.G.to_undirected() ), key=len)
        subgraph = self.G.subgraph(largest_cc)

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
        try:
            eig_centralities = nx.eigenvector_centrality_numpy(G, max_iter=1000, tol=1e-03)
        except:
            #print("ARPACK did not converge, falling back to largest component or different method")
            # Handle the error by using the largest connected component, for example
            largest_cc = max(nx.connected_components(self.G.to_undirected()), key=len)
            subgraph = self.G.subgraph(largest_cc)
            eig_centralities = nx.eigenvector_centrality_numpy(subgraph, max_iter=1000, tol=1e-03)
        #
        influencers = median(eig_centralities.values())
        external_connections = self.calculate_average_external_connections(self.G)
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
            self.beta4 * influencers +
            self.beta5 * average_exposure +
            self.beta6 * self.global_gec+
            self.beta7 * ecc
        )
        #print(f"Graph Echo Chamber Strength {strength}")
        return strength

    def calculate_community_influence(self, G, community_nodes):
        try:
            eig_centralities = nx.eigenvector_centrality_numpy(G, max_iter=1000, tol=1e-03)
        except:
            #print("ARPACK did not converge, falling back to largest component or different method")
            # Handle the error by using the largest connected component, for example
            largest_cc = max(nx.connected_components(G), key=len)
            subgraph = G.subgraph(largest_cc)
            eig_centralities = nx.eigenvector_centrality_numpy(subgraph, max_iter=1000, tol=1e-03)

        # Calculate influence scores for nodes in the community
        community_influence_scores = {node: eig_centralities[node] for node in community_nodes}

        # Calculate the community-level influence score (e.g., average)
        community_influence_score = sum(community_influence_scores.values()) / len(community_nodes)

        # Normalize the influence score
        max_influence_score = max(eig_centralities.values())
        normalized_influence_factor = community_influence_score / max_influence_score

        return normalized_influence_factor

    def is_echo_chamber(self, community):
        if not hasattr(self, 'graph_strength'):
          self.graph_strength = self.calculate_graph_echo_chamber_strength()
        community_strength = self.calculate_echo_chamber_strength(community)
        return community_strength >= self.graph_strength

    def derive_betas(self, G):
        #print("Deriving Betas...")
        # Beta1 - Coeficiente de Agrupamento Médio
        avg_clustering_coeff = nx.average_clustering(G)
        beta1 = avg_clustering_coeff  # Ou um valor inicial de 0.171, conforme o contexto

        # Beta2 - Homogeneidade das Opiniões
        num_communities = len(list(nx.community.greedy_modularity_communities(G)))
        beta2 = 1  # Ou um valor inicial de 1/352

        # Beta3 - Conexões Externas
        num_weakly_connected_components = nx.number_weakly_connected_components(G)
        beta3 = 1 / num_weakly_connected_components  # Ou um valor inicial de 1/329

        # Bfeta4 - Efeito dos Influenciadores
        try:
            eig_centralities = nx.eigenvector_centrality_numpy(G, max_iter=1000, tol=1e-03)
        except:
            #print("ARPACK did not converge, falling back to largest component or different method")
            # Handle the error by using the largest connected component, for example
            largest_cc = max(nx.connected_components(G), key=len)
            subgraph = G.subgraph(largest_cc)
            eig_centralities = nx.eigenvector_centrality_numpy(subgraph, max_iter=1000, tol=1e-03)
        median_centrality = median(eig_centralities.values())
        beta4 = median_centrality
        # Beta5 - Exposição Média
        if nx.is_strongly_connected(G):
            avg_path_length = nx.average_shortest_path_length(G)
        else:
            largest_cc = max(nx.strongly_connected_components(G), key=len)
            subgraph = G.subgraph(largest_cc)
            avg_path_length = nx.average_shortest_path_length(subgraph)
        beta5 = avg_path_length / len(self.G.nodes)
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

    def calculate_ecc_for_community(self, community):
        total_contribution = 0

        for member in community:
            user_events = self.get_events_created_by_user(member)
            #print(f"user_events {user_events}")
            user_contribution = 0

            for index, row in user_events.iterrows():
                # Avalie a contribuição do evento com base em score e persona
                event_contribution = self.evaluate_event_contribution(row, community)
                user_contribution += event_contribution

            total_contribution += user_contribution

        # ECC da comunidade como um todo
        ecc = total_contribution / len(community)
        #print(f"ecc {ecc}")
        return ecc

    def evaluate_event_contribution(self, event, community):
        scores = [self.get_all_scores_for_user(member) for member in community]
        all_scores = [score for sublist in scores for score in sublist]
        if not all_scores or np.all(np.isnan(all_scores)):
            return 0
        scores = all_scores
        personas = [self.get_persona_for_user(member) for member in community]
        #print(f"scores {scores}")
        #print(f"personas {personas}")
        event_score = event['score']  # Score do evento
        event_persona = event['persona']  # Persona do evento
        #print(f"event_score {event_score}")
        #print(f"event_persona {event_persona}")
        if(event_score > 0): event_score = 1
        else: event_score = -1

        # Assuming you have already defined 'scores' and 'personas' for the community
        positive_scores = [score for score in scores if not np.isnan(score) and score > 0]
        negative_scores = [score for score in scores if not np.isnan(score) and score < 0]

        # Calculate the predominant score (positive or negative)
        predominant_score = 1 if len(positive_scores) > len(negative_scores) else -1 if len(negative_scores) > len(positive_scores) else 0
        #print(f"predominant_score {predominant_score}")
        non_none_personas = [persona for persona in personas if persona is not None]

        if non_none_personas:
            count_ones = non_none_personas.count(1)
            count_zeros = non_none_personas.count(0)

            # Calculate the predominant persona (1 or 0)
            predominant_persona = 1 if count_ones > count_zeros else 0 if count_zeros > count_ones else None
        else:
            predominant_persona = None
        #print(f"predominant_persona {predominant_persona}")
        # Compare o evento com as características predominantes da comunidade
        if event_score == predominant_score and event_persona == predominant_persona:
            #print("event contributes to polarization")
            return 1  # Evento contribui positivamente
        else:
            #print("event DOES NOT contribute to polarization")
            return 0  # Evento não contribui

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

    def analyse_metrics(self, metrics_list, t):
        data = [metrics['echo_chamber_strength'] for metrics in metrics_list]
        peaks, _ = find_peaks(data, height=1)
        print(f"Peaks: {peaks}")
        echo_chamber_indices = peaks.tolist()
        return echo_chamber_indices

    def identify_echo_chambers(self, beta1=1.0, beta2=1.0, beta3=1.0, beta4=1.0, beta5=1.0, beta6=1.0, beta7=1.0, metric='threshold', metric_param = 2):
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

        #print('Number of communities before filtering:', len(self.communities))

        # Filter communities based on the minimum size requirement
        self.communities = [community for community in self.communities if len(community) >= self.min_community_size]

        print('Number of communities after filtering:', len(self.communities))

        self.echo_chambers = []
        self.graph_strength = self.calculate_graph_echo_chamber_strength()
        #self.global_gec = 0
        print("Calculating community metrics...")
        all_communities_metrics = [self.calculate_echo_chamber_metrics(community) for community in self.communities]
        print(f"Community Metrics: {all_communities_metrics}")
        self.community_metrics = all_communities_metrics
        if self.classifier != None:
          b = self.classifier.analyse_metrics(all_communities_metrics)
        else :
          b = self.analyse_metrics(all_communities_metrics, metric_param)
        echo_chambers = [self.communities[index] for index in b]
        return echo_chambers
#
def detect_echo_chambers(df, n, e, comments_df, likes_df, votes_df, t=2.0, debug_g=None, validate_communities=None):
  selected_ids = set(df['colab_user_id'])
  # Direct filtering
  edgez = e[e['source'].apply(lambda x: x in selected_ids) | e['target'].apply(lambda x: x in selected_ids)]
  edgez
  # Crie um grafo a partir do DataFrame de arestas (edges_df)
  if debug_g != None:
    graph = debug_g
    #print("Using debug Graph")
  else:
    graph = nx.from_pandas_edgelist(edgez, 'source', 'target', create_using=nx.DiGraph())
  #
  print(graph)
  #print("Analysing Communities...")
  strategy = LeidenClusteringStrategy(algo=leidenalg.SignificanceVertexPartition, resolution=2, num_iterations=10)
  communities_summary = analyze_communities(graph, algorithm="leiden", resolution=2, algo=leidenalg.SignificanceVertexPartition)
  net_communities = communities_summary['communities']
  #print('number_of_communities:', communities_summary['number_of_communities'])
  #print('largest_community_size:', communities_summary['largest_community_size'])
  #print('smallest_community_size:', communities_summary['smallest_community_size'])
  #print('average_community_size:', communities_summary['average_community_size'])
  community_sizes = {}
  #
  if validate_communities != None:
    validate_communities(graph, net_communities)
  #
  filtered_comments, filtered_likes, filtered_updown = filter_dfs_based_on_edgelist(edgez,comments_df,likes_df,votes_df)
  # Print the number of rows for each DataFrame
  #print(f"Comments: {len(filtered_comments)}")
  #print(f"Likes: {len(filtered_likes)}")
  #print(f"Votes: {len(filtered_updown)}")
  detector = EchoChamberDetector(
    n, nx.to_pandas_edgelist(graph), df, filtered_comments, filtered_likes, filtered_updown,
    strategy=strategy,
    classifier=echo_chamber_metrics_classifier,
    communities=net_communities
  )
  beta1, beta2, beta3, beta4, beta5, beta6, beta7 = detector.derive_betas(graph)
  #print(f'beta1: {beta1}, beta2: {beta2}, beta3:{beta3}, beta4: {beta4}, beta5: {beta5}, beta6: {beta6}, beta7: {beta7}')
  echo_chambers = detector.identify_echo_chambers(beta1, beta2, beta3, beta4, beta5, beta6, beta7, metric_param=t)
  # Exiba as echo chambers encontradas
  print(f"Echo Chambers: {len(echo_chambers)}")
  for i, chamber in enumerate(echo_chambers, 1):
      print(f"Echo Chamber {i}: {len(chamber)}")
  return echo_chambers