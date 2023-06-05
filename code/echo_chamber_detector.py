import pandas as pd
import networkx as nx
from sklearn.cluster import SpectralClustering
import community as community_louvain
import numpy as np


class EchoChamberDetector:

    def __init__(self, nodes_df, edges_df, min_community_density=0.5, min_community_size=3):
        """
        Initializes an EchoChamberDetector object with the given nodes and edges dataframes, and sets the minimum community 
        density and size thresholds.

        Parameters:
        -----------
        nodes_df : pandas.DataFrame
            Dataframe containing the nodes of the graph. Must have a column named 'id' with the unique identifier of each node.
        edges_df : pandas.DataFrame
            Dataframe containing the edges of the graph. Must have two columns named 'source' and 'target' with the IDs of 
            the nodes connected by each edge.
        min_community_density : float
            Minimum density required for a community to be considered an echo chamber. Default is 0.5.
        min_community_size : int
            Minimum size required for a community to be considered an echo chamber. Default is 3.
        """
        self.nodes = nodes_df
        self.edges = edges_df
        self.G = nx.from_pandas_edgelist(self.edges, 'source', 'target')
        self.min_community_density = min_community_density
        self.min_community_size = min_community_size
    ##

    def louvain_partition(self):
        """
        Applies the Louvain community detection algorithm to the graph and returns the partition.

        Returns:
            partition (dict): A dictionary mapping node IDs to community IDs.
        """
        partition = community_louvain.best_partition(self.G)
        return partition
    ##
    def spectral_partition(self, n_clusters):
        """
        Perform spectral clustering on the graph using the adjacency matrix and return the resulting partition.

        Args:
        - n_clusters (int): The number of clusters to create.

        Returns:
        - partition (numpy.ndarray): A one-dimensional array containing the cluster assignments of each node in the graph.

        This method uses the adjacency matrix of the graph to perform spectral clustering, which is a technique that aims to group nodes with similar connectivity patterns. Specifically, it constructs an affinity matrix from the adjacency matrix, and applies the SpectralClustering algorithm from scikit-learn to obtain the cluster assignments. The resulting partition is returned as a one-dimensional numpy array, where each element represents the cluster assignment of the corresponding node in the graph. The number of clusters is controlled by the `n_clusters` parameter.
        """
        A = nx.adjacency_matrix(self.G)
        sc = SpectralClustering(n_clusters=n_clusters,
                                affinity='precomputed', n_init=100)
        sc.fit(A)
        partition = sc.labels_
        return partition
    ##
    def louvain_score(self):
        """
        Calculates the modularity score of the Louvain community detection algorithm.

        Returns:
            score (float): The modularity score of the detected communities.
        """
        partition = self.louvain_partition()
        score = community_louvain.modularity(partition, self.G)
        return score
    ##
    def spectral_score(self, n_clusters):
        """
        Calculates the modularity score of the spectral clustering partition.

        Args:
        - n_clusters (int): number of clusters to partition the graph.

        Returns:
        - float: modularity score of the spectral clustering partition.

        This method partitions the graph using spectral clustering algorithm with a given number of clusters.
        Then it calculates the modularity score of the partitioned clusters using the networkx's modularity function.
        Modularity is a measure of the density of edges within communities compared to the density of edges between communities.
        Higher modularity scores indicate better community structures.

        """
        partition = self.spectral_partition(n_clusters)
        score = nx.algorithms.community.modularity(self.G, partition)
        return score
    ##
    def get_eigenvector_top_users(self, n):
        """
        Returns the top n users with the highest eigenvector centrality score in the network.
        
        Eigenvector centrality measures the influence of a node in a network, taking into account the centrality of its 
        neighboring nodes. A node with a high eigenvector centrality score indicates that it is connected to other 
        well-connected nodes, making it influential in the network.
        
        Args:
        - n (int): The number of top users to return.
        
        Returns:
        - top_users (numpy.ndarray): A 1D numpy array of the IDs of the top n users with the highest eigenvector 
        centrality score in the network.
        """
        centrality = nx.eigenvector_centrality_numpy(self.G)
        sorted_centrality = sorted(
            centrality.items(), key=lambda x: x[1], reverse=True)
        top_users = np.array([int(u[0]) for u in sorted_centrality[:n]])
        return top_users
    ##

    def detect_echo_chambers(self, method='spectral', community_density=0.5, min_community_size=3, n_clusters=5):
        """
        Detects echo chambers in the network.

        Parameters:
        -----------
        method: str, default 'spectral'
            The method used to partition the network. It can be either 'spectral' or 'louvain'.
        community_density: float, default 0.5
            Minimum community density required to consider it as an echo chamber.
        min_community_size: int, default 3
            Minimum number of nodes required for a community to be considered an echo chamber.
        n_clusters: int, default 5
            Number of clusters to use in the spectral partitioning method.

        Returns:
        --------
        subgraphs: list
            List of subgraphs containing echo chambers detected in the network.
        """
        if method == 'spectral':
            partition = self.spectral_partition(n_clusters)
        elif method == 'louvain':
            partition = self.louvain_partition()
        else:
            raise ValueError("Method should be 'spectral' or 'louvain'.")

        subgraphs = []
        for c in set(partition):
            nodes = [n for n, p in partition.items() if p == c]
            if len(nodes) >= min_community_size:
                sg = self.G.subgraph(nodes)
                if len(sg) / self.G.subgraph(self.nodes['id']).order() >= community_density:
                    subgraphs.append(sg)

        return subgraphs
    ##

    def is_echo_chamber(self, community):
        """
        Determines if a given community is an echo chamber based on the community density.

        Parameters:
        -----------
        community : list of str
            A list of node IDs that belong to the community.

        Returns:
        --------
        bool
            True if the community is an echo chamber, False otherwise.
        """

        if len(community) < self.min_community_size:
            return False

        edges = [(n1, n2) for n1 in community for n2 in community if n1 != n2 and (n1, n2) in self.edges]
        density = len(edges) / (len(community) * (len(community) - 1) / 2)

        return density >= self.min_community_density
    ##

    def identify_echo_chambers(self, method='spectral', community_density=0.5, community_size=3, n_clusters=2):
        """
        Identifies echo chambers in the network using either spectral clustering or Louvain community detection algorithm.

        Parameters:
            - method (str): Method for community detection. Default is 'spectral', can be set to 'louvain' for Louvain community detection.
            - community_density (float): Minimum density required for a community to be considered an echo chamber. Default is 0.5.
            - community_size (int): Minimum size required for a community to be considered an echo chamber. Default is 3.
            - n_clusters (int): Number of clusters to create for spectral clustering. Default is 2.

        Returns:
            - echo_chambers (list): List of echo chambers identified in the network.
        """
        if method == 'spectral':
            communities = self.spectral_partition(n_clusters=n_clusters)
        elif method == 'louvain':
            communities = self.louvain_community_detection(
                community_density=community_density, community_size=community_size)
        else:
            raise ValueError(
                f"Invalid method '{method}' specified. Please choose 'spectral' or 'louvain'.")

        echo_chambers = []
        for community in communities:
            if self.is_echo_chamber(community):
                echo_chambers.append(community)

        return echo_chambers