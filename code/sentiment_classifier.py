import pandas as pd
import matplotlib.pyplot as plt
from multiprocessing import Pool, cpu_count
from enum import Enum
import re
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import export_graphviz
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import roc_curve, auc, roc_auc_score
import nltk
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from gensim.models.doc2vec import LabeledSentence
import os
#
nltk.download('stopwords')
#
#
class ModelType(Enum):
    RANDOM_FOREST = 'RandomForest'
    LOGISTIC_REGRESSION = 'LogisticRegression'
    DECISION_TREE = 'DecisionTree'
    KNN = 'KNN'
#
#
class SentimentClassifierModel:
    def __init__(self, train_file_url):
        self.train_file_url = train_file_url
        self.data = None
        self.cv = CountVectorizer()
        self.trained_models = {}
        self.current_model = None
    #
    def load_data(self):
        self.data = pd.read_csv(self.train_file_url, low_memory=False)
    #
    @staticmethod
    def sanitize_phrase(phrase):
        stopwords_set = set(stopwords.words('portuguese'))
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
    #
    def vectorize_data(self):
        self.cv = CountVectorizer(stop_words=stopwords.words('portuguese'))
        words = self.cv.fit_transform(self.data.description)
        self.x = words.toarray()
        self.y = self.data.iloc[:, 1]
    #
    def train_model(self, model_type=ModelType.RANDOM_FOREST):
        x_train, x_valid, y_train, y_valid = train_test_split(self.x, self.y, test_size=0.25, random_state=42)
        sc = MinMaxScaler()
        x_train = sc.fit_transform(x_train)
        x_valid = sc.transform(x_valid)
        #
        if model_type == ModelType.RANDOM_FOREST:
            model = RandomForestClassifier()
        elif model_type == ModelType.LOGISTIC_REGRESSION:
            model = LogisticRegression()
        elif model_type == ModelType.DECISION_TREE:
            model = DecisionTreeClassifier()
        elif model_type == ModelType.KNN:
            model = KNeighborsClassifier()
        else:
            raise ValueError("Invalid model_type. Supported values: 'RandomForest', 'LogisticRegression', "
                             "'DecisionTree', 'KNN'")

        model.fit(x_train, y_train)
        y_pred = model.predict(x_valid)
        print("Training Accuracy:", model.score(x_train, y_train))
        print("Validation Accuracy:", model.score(x_valid, y_valid))
        print("F1 score:", f1_score(y_valid, y_pred, average="weighted"))
        cm = confusion_matrix(y_valid, y_pred)
        print(cm)
        #
        self.trained_models[model_type] = model
        self.current_model = model_type
    #
    def predict(self, phrase, model_type=None):
        if model_type is None:
            model_type = self.current_model
        else:
            if model_type not in ModelType:
                raise ValueError("Invalid model_type. Supported values: 'RandomForest', 'LogisticRegression', "
                                 "'DecisionTree', 'KNN'")
            if model_type not in self.trained_models:
                raise ValueError(f"Model '{model_type.value}' has not been trained yet.")
        #
        model = self.trained_models[model_type]
        phrase = self.sanitize_phrase(phrase)
        vectorized_phrase = self.cv.transform([phrase]).toarray()
        sentiment_score = model.predict(vectorized_phrase)[0]
        #
        return {'status': 'ok', 'score': sentiment_score, 'model': model_type.value}
#
#
class ColabSentimentClassifier:
    def __init__(self, events_file_url, model_train_file_url):
        self.events_file_url = events_file_url
        self.model = SentimentClassifierModel(train_file_url=model_train_file_url)
        self.user_scores = {}
    #
    def process(self):
        self.load_events_data()
        self.initialize_model()
        self.update_user_scores()
    #
    def load_events_data(self):
        colab_events = pd.read_csv(self.events_file_url)
        self.events_data = colab_events[['user_id', 'description']]
    #
    def initialize_model(self):
        self.model.load_data()
        self.model.vectorize_data()
        self.model.train_model(model_type=ModelType.RANDOM_FOREST)
    #
    def calculate_user_scores(self):
        for colab_user_id, scores in self.user_scores.items():
            total_events = len(scores)
            aggregate_score = sum(scores) / total_events if total_events > 0 else 0
            normalized_score = (aggregate_score - 1) / (10 - 1)
            self.user_scores[colab_user_id] = normalized_score
    #
    def update_user_scores(self):
        num_cpus = cpu_count()  # Obtém o número de CPUs disponíveis no sistema
        pool = Pool(processes=num_cpus)  # Cria um pool de processos
    #
        # Função auxiliar para processar uma linha do DataFrame de eventos
        def process_row(row):
            colab_user_id = row['user_id']
            description = row['description']
            prediction = self.model.predict(description)
            score = prediction['score']
            #
            if colab_user_id not in self.user_scores:
                self.user_scores[colab_user_id] = []
            #
            self.user_scores[colab_user_id].append(score)
        #
        # Mapeia a função de processamento em paralelo para cada linha do DataFrame de eventos
        pool.map(process_row, self.events_data.itertuples(index=False))
        #
        pool.close()
        pool.join()
        #
        self.calculate_user_scores()
    #
    def plot_user_scores(self):
        user_ids = list(self.user_scores.keys())
        scores = list(self.user_scores.values())
        #
        plt.bar(user_ids, scores)
        plt.xlabel('User ID')
        plt.ylabel('Normalized Score')
        plt.title('Sentiment Scores per User')
        plt.xticks(rotation='vertical')
        plt.show()
#
#
def main(events_file_path, model_train_file_path):
    classifier = ColabSentimentClassifier(events_file_url=events_file_path, model_train_file_url=model_train_file_path)
    classifier.process()
    classifier.plot_user_scores()
#
#
if __name__ == '__main__':
    events_file_path = 'path/to/events.csv'
    model_train_file_path = 'path/to/model_train.csv'
    main(events_file_path, model_train_file_path)