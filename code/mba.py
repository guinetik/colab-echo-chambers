class User:
    def __init__(self, id):
        self.id = id
        self.opinion = np.random.uniform(-1, 1)
        self.exposure = 0a
##
class News:
    def __init__(self):
        self.sentiment = np.random.uniform(-1, 1)
##
class OpinionUpdateStrategy:
    def __init__(self, mu=0.1):
        self.mu = mu  # Convergence parameter

    def update_graph(self, graph):
        self.graph = graph

    def update_opinion(self, user, news, threshold, **kwargs):
        # Update the user's exposure
        user.exposure += abs(user.opinion - news.sentiment)

        # If the news sentiment is close to the user's opinion, they accept the news
        if abs(user.opinion - news.sentiment) < threshold:
            # Update the user's opinion
            user.opinion += self.mu * (news.sentiment - user.opinion)
##
class NeighborInfluenceOpinionUpdateStrategy(OpinionUpdateStrategy):
    def __init__(self, mu=0.1, influence_factor=0.5):
        super().__init__(mu)
        self.influence_factor = influence_factor  # How much neighbors' opinions influence the user's opinion

    def update_opinion(self, user, news, threshold, neighbors):
        super().update_opinion(user, news, threshold)
        # If the average opinion of the user's neighbors has the same sign as the user's opinion, they are influenced by their neighbors
        if np.sign(user.opinion) == np.sign(np.mean([neighbor.opinion for neighbor in neighbors])):
            # Update the user's opinion towards the average opinion of their neighbors
            user.opinion += self.influence_factor * (np.mean([neighbor.opinion for neighbor in neighbors]) - user.opinion)
##
class WeightedNeighborInfluenceOpinionUpdateStrategy(OpinionUpdateStrategy):
    def __init__(self, mu=0.1):
        super().__init__(mu)
        self.graph = None  # The network graph
        self.centralities = None  # The eigenvector centrality of each node

    def update_graph(self, graph):
        super().update_graph(graph)
        self.centralities = nx.eigenvector_centrality(self.graph)
        #print(f"Centralities:{self.centralities}")

    def update_opinion(self, user, news, threshold, neighbors):
      super().update_opinion(user, news, threshold)

      # Check if the neighbors list is not empty
      if neighbors:
          # If the average opinion of the user's neighbors has the same sign as the user's opinion, they are influenced by their neighbors
          if np.sign(user.opinion) == np.sign(np.mean([neighbor.opinion for neighbor in neighbors if neighbor is not None])):
              # Update the user's opinion towards the weighted average opinion of their neighbors
              total_weight = sum(self.centralities.get(neighbor.id, 0) for neighbor in neighbors if neighbor is not None)
              #print(f"Total Weight: {total_weight}")
              weighted_average_opinion = sum(self.centralities.get(neighbor.id, 0) * neighbor.opinion for neighbor in neighbors if neighbor is not None) / total_weight
              user.opinion += self.mu * (weighted_average_opinion - user.opinion)
      else:
          # Handle the case where the neighbors list is empty
          # Add appropriate code or error handling here
          print("no neighbors")
##
class BasicOpinionUpdateStrategy(OpinionUpdateStrategy):
    def update_opinion(self, user, news, threshold):
        user.exposure += abs(user.opinion - news.sentiment)
        if abs(user.opinion - news.sentiment) < threshold:
            user.opinion += 0.1 * (news.sentiment - user.opinion)
##
class AgentBasedSimulation:
    def __init__(self, num_users, num_news, opinion_update_strategy):
        self.users = {i: User(i) for i in range(num_users)}  # Store users as key-value pairs with indices as keys
        self.news = [News() for _ in range(num_news)]
        self.graph = nx.barabasi_albert_graph(num_users, 8)
        self.opinion_update_strategy = opinion_update_strategy
        self.opinion_update_strategy.update_graph(self.graph)

    def run(self):
        for news in self.news:
            for user_index in self.users:
                user = self.users[user_index]
                if np.random.rand() < 0.5:
                    neighbors = self.graph.neighbors(user_index)  # Get the neighbors using the user's index
                    neighbors_users = [self.users[i] for i in neighbors]
                    if isinstance(self.opinion_update_strategy, WeightedNeighborInfluenceOpinionUpdateStrategy):
                        self.opinion_update_strategy.update_opinion(user, news, 0.5, neighbors_users)
                    else:
                        self.opinion_update_strategy.update_opinion(user, news, 0.5)
                    if np.sign(user.opinion) == np.sign(np.mean([self.users[i].opinion for i in neighbors])):
                        for i in neighbors:
                            self.opinion_update_strategy.update_opinion(self.users[i], news, 0.1)

    def calculate_measures(self):
      ECC = {
          user_index: np.std(
              [self.users[i].opinion for i in self.graph.neighbors(user_index)]
          )
          for user_index in self.users
      }
      GEC = sum(
          np.sign(self.users[i].opinion) * np.sign(self.users[j].opinion)
          for i, j in self.graph.edges
      )
      average_opinion = np.mean([user.opinion for user in self.users.values()])
      average_exposure = np.mean([user.exposure for user in self.users.values()])
      return ECC, GEC, average_opinion, average_exposure