import networkx as nx
import numpy as np
import random
from scipy.stats import zscore
###########################################

class CommunityStrategy:
    def detect_communities(self, G):
        raise NotImplementedError


class GreedyModularityCommunityStrategy(CommunityStrategy):
    def detect_communities(self, G):
        return list(nx.algorithms.community.greedy_modularity_communities(G))


class SpectralClusteringStrategy(CommunityStrategy):
    def __init__(self, n_clusters):
        self.n_clusters = n_clusters

    def detect_communities(self, G):
        adjacency_matrix = nx.to_numpy_array(G)
        spectral_model = SpectralClustering(
            n_clusters=self.n_clusters, affinity='precomputed')
        labels = spectral_model.fit_predict(adjacency_matrix)
        communities = []
        for label in np.unique(labels):
            nodes = list(np.where(labels == label)[0])
            communities.append(set(nodes))
        return communities


class InfomapStrategy(CommunityStrategy):
    def detect_communities(self, G):
        infomap_model = Infomap()
        for edge in G.edges():
            infomap_model.addLink(*edge)
        infomap_model.run()
        communities = []
        for node in infomap_model.iterTree():
            if node.isLeaf():
                communities.append(set(node.physicalId))
        return communities


class LouvainCommunityStrategy(CommunityStrategy):
    def detect_communities(self, G):
        partitions = community_louvain.best_partition(G)
        values = set(partitions.values())
        communities = [set([key for key in partitions.keys()
                           if partitions[key] == val]) for val in values]
        return communities


class LeidenClusteringStrategy(CommunityStrategy):
    def __init__(self, algo=leidenalg.RBERVertexPartition, resolution=1.0, num_iterations=10):
        self.algo = algo
        self.resolution = resolution
        self.num_iterations = num_iterations

    def detect_communities(self, G):
        g = ig.Graph.from_networkx(G)
        # Set the 'name' attribute for each vertex in the igraph graph
        g.vs["name"] = list(G.nodes())
        # Find the communities using the Leiden algorithm with the specified parameters
        if self.algo != leidenalg.ModularityVertexPartition:
            partition = leidenalg.find_partition(
                g, self.algo, n_iterations=self.num_iterations, resolution_parameter=self.resolution)
        else:
            partition = leidenalg.find_partition(g, self.algo)
        # Extract the communities
        network_communities = [list(partition.subgraph(
            i).vs["name"]) for i in range(len(partition))]
        return network_communities


class GirvanNewmanCommunityStrategy(CommunityStrategy):
    def detect_communities(self, G):
        def find_best_edge(G0):
            # Function to find the edge with the highest betweenness centrality.
            edge_betweenness = nx.edge_betweenness_centrality(G0)
            sorted_edge_betweenness = sorted(
                edge_betweenness.items(), key=lambda x: x[1], reverse=True)
            return sorted_edge_betweenness[0][0]

        def girvan_newman_step(G):
            # Function to perform one step of the Girvan-Newman algorithm.
            if len(G.edges) == 0:
                return []

            initial_components = nx.number_connected_components(G)
            edge_to_remove = find_best_edge(G)
            G.remove_edge(*edge_to_remove)
            new_components = nx.number_connected_components(G)

            if new_components > initial_components:
                return [c for c in nx.connected_components(G)]
            else:
                return girvan_newman_step(G)

        communities = girvan_newman_step(G)
        return communities


class EchoChamberDetector:
    def __init__(self, nodes_df, edges_df, events_df, colab_comments_df, colab_likes_df, colab_updown_df, strategy,
                 min_community_density=0.5, min_community_size=3):
        self.nodes = nodes_df
        self.edges = edges_df
        self.events = events_df
        self.colab_comments = colab_comments_df
        self.colab_likes = colab_likes_df
        self.colab_updown = colab_updown_df
        self.G = nx.from_pandas_edgelist(self.edges, 'source', 'target')
        self.strategy = strategy
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
        return np.unique(all_event_types)

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
        community_scores = [self.get_all_scores_for_user(
            user) for user in community]
        z_scores = [zscore(scores)
                    for scores in community_scores if len(scores) > 1]
        homogeneity = np.nanstd(z_scores)
        return homogeneity

    def calculate_echo_chamber_probability(self, community):
        density = self.calculate_community_density(community)
        homogeneity = self.calculate_homogeneity_of_opinions(community)
        external_connections = self.calculate_external_connections(community)
        ecc = self.calculate_community_ecc(community)
        gec = self.calculate_community_gec(community)
        average_exposure = self.calculate_community_exposure(community)
        beta1, beta2, beta3, beta4, beta5, beta6, beta7 = self.derive_betas(
            community)
        probability = np.exp(
            beta1 * density +
            beta2 * homogeneity +
            beta3 * external_connections +
            beta4 * ecc +
            beta5 * gec +
            beta6 * average_exposure +
            beta7
        )
        return probability

    def is_echo_chamber(self, community):
        graph_probability = self.calculate_echo_chamber_probability(
            list(self.G.nodes))
        community_probability = self.calculate_echo_chamber_probability(
            community)
        return community_probability >= graph_probability

    def derive_betas(self, community):
        avg_clustering_coeff = nx.average_clustering(self.G)
        num_communities = len(list(self.strategy.get_communities(self.G)))
        num_weakly_connected_components = nx.number_weakly_connected_components(
            self.G.to_undirected())
        eigenvector_centrality_sum_change = sum(
            nx.eigenvector_centrality(self.G).values())
        modularity_score = nx.community.modularity(
            self.G, self.strategy.get_communities(self.G))
        if len(community) > 0:
            avg_shortest_path_length = nx.average_shortest_path_length(
                self.G.subgraph(community))
        else:
            avg_shortest_path_length = 0

        beta1 = avg_clustering_coeff
        beta2 = 1 / num_communities
        beta3 = 1 / num_weakly_connected_components
        beta4 = eigenvector_centrality_sum_change
        beta5 = avg_shortest_path_length
        beta6 = modularity_score
        beta7 = 1 / len(self.G.nodes)

        return beta1, beta2, beta3, beta4, beta5, beta6, beta7

    def calculate_community_ecc(self, community):
        scores = [self.get_all_scores_for_user(member) for member in community]
        all_scores = [score for sublist in scores for score in sublist]
        if not all_scores or np.all(np.isnan(all_scores)):
            return 0
        ecc = np.nanstd(all_scores)
        return ecc

    def calculate_community_gec(self, community):
        scores = [self.get_all_scores_for_user(member) for member in community]
        all_scores = [score for sublist in scores for score in sublist]
        if not all_scores or np.all(np.isnan(all_scores)):
            return 0
        gec = np.nansum(np.sign(all_scores))
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
        return average_exposure

    def identify_echo_chambers(self, beta1=1.0, beta2=1.0, beta3=1.0, beta4=1.0, beta5=1.0, beta6=1.0, beta7=1.0):
        self.beta1 = beta1
        self.beta2 = beta2
        self.beta3 = beta3
        self.beta4 = beta4
        self.beta5 = beta5
        self.beta6 = beta6
        self.beta7 = beta7
        communities = self.strategy.get_communities(self.G)
        self.echo_chambers = []
        for community in communities:
            if len(community) >= self.min_community_size:
                if self.is_echo_chamber(list(community)):
                    self.echo_chambers.append(list(community))
        return self.echo_chambers
