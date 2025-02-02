import string
import pandas as pd
from dotenv import load_dotenv
import os
import csv
import spacy
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from wordcloud import WordCloud
import stanza
import deplacy
import graphviz
import matplotlib.pyplot as plt

load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env

# Baixar os módulos do Spacy em português
!python -m spacy download pt_core_news_sm

# Baixar os recursos do NLTK
nltk.download('stopwords')
nltk.download('rslp')

# Carregar o modelo do Spacy em português
nlp = spacy.load("pt_core_news_sm")

# Inicializar os stemmers e lemmatizers
stemmer = RSLPStemmer()
lemmatizer = WordNetLemmatizer()

# Função para exibir o mapa sintático da frase utilizando Stanza e Deplacy
def exibirMapaSintatico(frase):
  nlp_stanza = stanza.Pipeline("pt")
  doc = nlp_stanza(frase)
  deplacy.render(doc)
  graphviz.Source(deplacy.dot(doc))

# Função para exibir a distribuição de palavras e nuvem de palavras
def visualizarDistribuicaoPalavras(collection, top):
  cv = CountVectorizer(stop_words=stopwords.words('portuguese'))
  words = cv.fit_transform(collection)
  sum_words = words.sum(axis=0)

  words_freq = [(word, sum_words[0, i]) for word, i in cv.vocabulary_.items()]
  words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)

  frequency = pd.DataFrame(words_freq, columns=['word', 'freq'])

  frequency.head(top).plot(x='word', y='freq', kind='bar', figsize=(20, 7), color='blue')
  wordcloud = WordCloud(background_color='white', width=1000, height=1000).generate_from_frequencies(dict(words_freq))
  plt.figure(figsize=(20, 8))
  plt.imshow(wordcloud)
  plt.title("WordCloud", fontsize=22)
  plt.show()

# Carregar o arquivo CSV com o dicionário Oplexicon
dict_oplexicon = {}
csvfile = pd.read_csv(os.getenv('URL_OPLEXICON'), low_memory=False)
for index, row in csvfile.iterrows():
  palavra = row[0]
  polaridade = row[2]
  dict_oplexicon[palavra] = polaridade

# Carregar o arquivo CSV com o dicionário Unilex
dict_unilex = {}
csvfile = pd.read_csv(os.getenv('URL_UNILEX'), low_memory=False)
for index, row in csvfile.iterrows():
  palavra = row[0]
  polaridade = row[1]
  dict_unilex[palavra] = polaridade

# Carregar o arquivo CSV com o dicionário WordNetAffectBr
dict_wordnetaffectbr = {}
csvfile = pd.read_csv("URL_WORDAFBR", low_memory=False)
for index, row in csvfile.iterrows():
  palavra = row[0]
  polaridade = row[1]
  dict_wordnetaffectbr[palavra] = polaridade

# Função de pré-processamento do texto
def preprocessamento(texto):
  texto = str(texto).lower()
  documento = nlp(texto)
  lista = []
  
  for token in documento:
    lista.append(lemmatizer.lemmatize(token.text))
  
  lista = [palavra for palavra in lista if palavra not in stopwords.words('portuguese') and palavra not in string.punctuation and not palavra.isdigit()]
  return lista

# Função para obter a polaridade da frase usando um dicionário
def obterPolaridade(frase, dicionario):
  frase_processada = preprocessamento(frase)
  frase_polaridade = [float(dicionario.get(palavra, 0)) for palavra in frase_processada]
  score = sum(frase_polaridade)
  return score

# Função para analisar o sentimento da frase usando diferentes dicionários
def analisarSentimento(frase, dicionarios):
  scores = [obterPolaridade(frase, dicionario) for dicionario in dicionarios]
  return scores

# Frase de teste
frase_teste = "Eu queria amar, mas tive medo"

# Comparando polaridades utilizando diferentes dicionários
dict_senticnet = {}  # Adicione o dicionário SenticNet
scores = analisarSentimento(frase_teste, [dict_oplexicon, dict_senticnet, dict_unilex, dict_wordnetaffectbr])
dicionarios = ["Oplexicon", "SenticNet", "Unilex", "WordNetAffectBr"]
for i in range(len(scores)):
  print("A polaridade da frase '", frase_teste, "' segundo o dicionário", dicionarios[i], "é:", scores[i])

# Carregar os dados do CSV de eventos do Colab
colab_events_url = os.getenv('URL_COLAB_EVENTS')
colab_events = pd.read_csv(colab_events_url, low_memory=False)

# Função para criar o conjunto de dados a partir dos eventos do Colab
def criarDataset(colab_events):
  dataset = colab_events.drop(columns=['status', 'created_at', 'event_type_id', 'event_type_name'])
  return dataset

# Ajustando o motor de sentimento

# Experimento de análise de sentimento com algumas frases de exemplo obtidas do CSV de eventos
# Adicionando palavras extras e corrigindo valores de palavras no dicionário lexicon
lexicon = dict(dict_oplexicon, **dict_senticnet)

palavras_lexicon = {
    "colabora": 1,
    "rua": 1,
    "iptu": -1,
    "prefeito": -1,
    "prefeitos": -1,
    "irregulares": -1,
    "indesejadas": -1,
    "bastasse": -1,
    "pública": 1,
    "horrorosas": -1,
    "indigência": -1,
    "inadequados": -1,
    "pt": -1,
    "psdb": -1,
    "pdt": -1,
    "corrupção": -1,
    "varias": -1,
    "árvore": 1,
    "urgente": 1,
    "número": 1,
    "frente": 1,
    "façam": -1,
    "asfaltem": -1,
    "prefeitura": 0.5,
    "sofreu": -1,
    "extremamente": -1,
    "mal": -1,
    "dejetos": -1,
    "vistoria": -1,
    "responsabilidade": -1,
    "secretaria": -1,
    "providência": -1,
    "gargalhadas": -1,
    "barulho": -1,
    "botequim": -1,
    "colab": -1,
    "algazarra": -1,
    "descaso": -1,
    "deveria": -1,
    "providências": -1,
    "reclamação": -1,
    "irrespirável": -1,
    "recorrentes": -1,
    "irregularidade": -1,
    "irregularidades": -1,
    "trabalhando": 1,
    "trabalhado": 1,
    "transparente": 1,
    "resolver": 0.5,
    "problemas": 0.5,
    "obstáculos": -1,
    "abismo": -1,
    "descumprimento": -1
}

for palavra, valor in palavras_lexicon.items():
  lexicon[palavra] = valor

# Testando a polaridade das frases de exemplo
frases_teste = [
    "Isso é culpa dos prefeitos que não ligam para a população",
    "Eu pago meu IPTU em dia é um absurdo isso acontecer",
    "Parabéns a prefeitura que tem trabalhado de uma forma transparente para resolver os problemas da cidade",
    "Fiação sem vergonha na Vila Olímpia. Fios caem até o chão, pondo em perigo a segurança do pedestre.",
    "Calçadão de Boa Viagem com várias depressões e buracos causados por infiltração de água",
    "O descumprimento da política nacional de mobilidade é evidente nessa intervenção feita na ponte Paulo Guerra. Não basta o resto da calçada da ponte estar esburacada e cheia de obstáculos, é preciso também abrir um abismo para o pedestre ter que ultrapassar. Essa alça construída para dar acesso ao Shopping Riomar é imoral e com certeza haverá atropelamentos, que chamarão de 'acidentes'. Não será acidente, será apenas o fruto de uma infraestrutura toda voltada para o fluxo de automóveis individuais em detrimento do pedestre em descumprimento a lei federal. Infelizmente o Ministério Público não intervém nesse caso. Ainda estamos muito longe de atingir a acessibilidade universal."
]

for frase in frases_teste:
  print("Polaridade da frase '", frase, "':", obterPolaridade(frase, lexicon))
  print("BREAKDOWN LEXICON")
  printLexiconPhrase(frase)
  print()

# Criar o dataset a partir dos eventos do Colab
dataset = criarDataset(colab_events)

# Calcular os scores das postagens usando o lexicon
scores = []
for index, row in dataset.iterrows():
  post = row[2]
  score = obterPolaridade(post, lexicon)
  scores.append(score)

dataset["score"] = scores

# Filtrar os piores e melhores scores
worst_scores = dataset.sort_values(by='score', ascending=True).head(1000)
best_scores = dataset.sort_values(by='score', ascending=False).head(1000)

# Visualizar a distribuição de palavras nos piores scores
visualizarDistribuicaoPalavras(worst_scores['description'], 10)

# Exibir o mapa sintático de uma postagem com pior score
exibirMapaSintatico(worst_scores['description'].values[0])

# Exibir os valores associados a cada palavra da postagem com pior score
printLexiconPhrase(worst_scores['description'].values[0])

# Visualizar a distribuição de palavras nos melhores scores
visualizarDistribuicaoPalavras(best_scores['description'], 10)

# Exibir o mapa sintático de uma postagem com melhor score
exibirMapaSintatico(best_scores['description'].values[0])

# Exibir os valores associados a cada palavra da postagem com melhor score
printLexiconPhrase(best_scores['description'].values[0])

# Concatenar os dataframes dos piores e melhores scores
frames = [worst_scores, best_scores]
result = pd.concat(frames).drop_duplicates().reset_index(drop=True).sort_values(by='score', ascending=True)

# Salvar o dataframe como CSV
result.to_csv('colab_sentiment_training.csv', encoding='utf-8-sig', index=False) 