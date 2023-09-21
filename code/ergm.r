library(network)
library(igraph)
library(ergm)
# Função para checar reciprocidade
check_reciprocity <- function(source, target, data) {
  return(any(data$source == target & data$target == source))
}
# Carrega os dados
data <- read.csv("sampled_graph.csv")
# Aplica a função para checar reciprocidade
data$mutual <- mapply(check_reciprocity, data$source, data$target, MoreArgs = list(data = data))
# Converte a coluna para numérica
data$mutual <- as.numeric(data$mutual)
# Converte o dataframe para um objeto network que representa um grafo em R
network <- network(data[, c("source", "target")], directed = TRUE, loops = TRUE)
# Atribui os atributos ao grafo
network %v% "location" <- data$location
network %v% "gender" <- data$gender
network %v% "age" <- data$age
network %v% "mutual" <- data$mutual
# Exibe um resumo do grafo
summary(network)
# Criando o modelo
model <- ergm(network ~ edges 
              + nodematch("location")
              + istar(1) + ostar(1)
              + nodematch("age")
              + gwidegree(decay=0.2, fixed=T, attr=NULL,cutoff=30,levels=NULL) #Popularity spread (indegree)
              + gwodegree(decay=0.2, fixed=T, attr=NULL,cutoff=30,levels=NULL) #Acitivty spread (outdegree)
              + nodefactor("age")
              + gwdsp(decay = 0.5)
              + nodeicov("age")
              + mutual,
              control = control.ergm(seed = 123))
# Obtem os coeficientes estimados
parameters <- coef(model)
# Simula o modelo
num_simulations <- 2  # Numero de simulações desejadas
simulated_networks <- simulate(model, nsim = num_simulations)
# Exibe os resultados
print(parameters)
print(simulated_networks)