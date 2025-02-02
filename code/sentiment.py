import re
import numpy as np
import pandas as pd
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import export_graphviz
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import roc_curve, auc, roc_auc_score
import nltk
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from wordcloud import WordCloud
from gensim.models.doc2vec import LabeledSentence
import matplotlib.pyplot as plt
import seaborn as sns
import pandas_profiling as pp
import plotly.express as px
from dotenv import load_dotenv
import os
##
load_dotenv()
nltk.download('stopwords')

# Load data
colab_events_url = os.getenv('URL_COLAB_EVENTS')
colab_events_train = pd.read_csv(colab_events_url, low_memory=False)
print(colab_events_train.shape)
colab_events_train.head(2)

# Data preprocessing
colab_events_train['score_norm'] = colab_events_train['score'].apply(lambda x: 1 if x >= 1 else 0)
colab_events_train['score_norm'].value_counts().plot.bar(color='pink', figsize=(6, 4))

# Text preprocessing
stopwords_set = set(stopwords.words('portuguese'))

def sanitize_phrase(phrase):
    result = ""
    for word in phrase.split(" "):
        review = re.sub(r'[^ \nA-Za-z0-9À-ÖØ-öø-ÿ/]+', ' ', word)
        review = review.lower()
        review = review.split()
        ps = PorterStemmer()
        # Stemming
        review = [ps.stem(word) for word in review if word not in stopwords_set]
        if review and len(review[0]) > 2:
            result += review[0] + " "
    return result.strip()

# Example usage
print(sanitize_phrase("O rato roeu a roupa do rei de roma joão josé"))

# Vectorization
cv = CountVectorizer(stop_words=stopwords.words('portuguese'))
words = cv.fit_transform(colab_events_train.description)
sum_words = words.sum(axis=0)
words_freq = [(word, sum_words[0, i]) for word, i in cv.vocabulary_.items()]
words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
frequency = pd.DataFrame(words_freq, columns=['word', 'freq'])
frequency.head(50).plot(x='word', y='freq', kind='bar', figsize=(20, 7), color='blue')
plt.title("Palavras mais utilizadas - Top 50")

# WordCloud
wordcloud = WordCloud(background_color='white', width=1000, height=1000).generate_from_frequencies(dict(words_freq))
plt.figure(figsize=(20, 8))
plt.imshow(wordcloud)
plt.title("WordCloud", fontsize=22)

# Model training
cv = CountVectorizer(max_features=len(colab_events_train))
x = cv.fit_transform(train_corpus).toarray()
y = colab_events_train.iloc[:, 1]

x_train, x_valid, y_train, y_valid = train_test_split(x, y, test_size=0.25, random_state=42)

# Standardization
sc = MinMaxScaler()
x_train = sc.fit_transform(x_train)
x_valid = sc.transform(x_valid)

# RandomForestClassifier
model = RandomForestClassifier()
model.fit(x_train, y_train)
y_pred = model.predict(x_valid)
print("Training Accuracy:", model.score(x_train, y_train))
print("Validation Accuracy:", model.score(x_valid, y_valid))
print("F1 score:", f1_score(y_valid, y_pred, average="weighted"))
cm = confusion_matrix(y_valid, y_pred)
print(cm)

# LogisticRegression
model = LogisticRegression()
model.fit(x_train, y_train)
y_pred = model.predict(x_valid)
print("Training Accuracy:", model.score(x_train, y_train))
print("Validation Accuracy:", model.score(x_valid, y_valid))
print("F1 score:", f1_score(y_valid, y_pred, average="weighted"))
cm = confusion_matrix(y_valid, y_pred)
print(cm)

# DecisionTreeClassifier
model = DecisionTreeClassifier()
model.fit(x_train, y_train)
y_pred = model.predict(x_valid)
print("Training Accuracy:", model.score(x_train, y_train))
print("Validation Accuracy:", model.score(x_valid, y_valid))
print("F1 score:", f1_score(y_valid, y_pred, average="weighted"))
cm = confusion_matrix(y_valid, y_pred)
print(cm)

# SVC
model = SVC()
model.fit(x_train, y_train)
y_pred = model.predict(x_valid)
print("Training Accuracy:", model.score(x_train, y_train))
print("Validation Accuracy:", model.score(x_valid, y_valid))
print("F1 score:", f1_score(y_valid, y_pred, average="weighted"))
cm = confusion_matrix(y_valid, y_pred)
print(cm)

# XGBClassifier
model = XGBClassifier()
model.fit(x_train, y_train)
y_pred = model.predict(x_valid)
print("Training Accuracy:", model.score(x_train, y_train))
print("Validation Accuracy:", model.score(x_valid, y_valid))
print("F1 score:", f1_score(y_valid, y_pred, average="weighted"))
cm = confusion_matrix(y_valid, y_pred)
print(cm)