import os
import re
import threading
import time
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.ensemble import (DecisionTreeClassifier, LogisticRegression,
                              RandomForestClassifier)
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC
from xgboost import XGBClassifier


#####################################################
# Classe de pré-processamento de texto
class TextPreprocessor:
    @staticmethod
    def sanitize_phrase(phrase):
        """
        Realiza o pré-processamento de uma frase, removendo stopwords,
        realizando stemming e limpeza.

        Args:
            phrase (str): A frase a ser pré-processada.

        Returns:
            str: A frase pré-processada.
        """
        result = ""
        for word in phrase.split(" "):
            review = re.sub(r'[^ \nA-Za-z0-9À-ÖØ-öø-ÿ/]+', ' ', word)
            review = review.lower()
            review = review.split()
            ps = PorterStemmer()
            # Stemming
            review = [ps.stem(word)
                      for word in review if word not in stopwords_set]
            if review and len(review[0]) > 2:
                result += review[0] + " "
        return result.strip()
#
# Classe de carregamento de dados
class DataLoader:
    @staticmethod
    def load_data():
        """
        Carrega os dados a partir de uma fonte externa.

        Returns:
            pd.DataFrame: O DataFrame contendo os dados carregados.
        """
        colab_events_url = os.getenv('URL_COLAB_EVENTS')
        colab_events_train = pd.read_csv(colab_events_url, low_memory=False)
        return colab_events_train
#
# Classe de serviço do modelo
class SentimentClassifier:
    def __init__(self):
        self.cv = CountVectorizer(stop_words=stopwords.words('portuguese'))
        self.sc = MinMaxScaler()
        self.models = {
            'random_forest': RandomForestClassifier(),
            'logistic_regression': LogisticRegression(),
            'decision_tree': DecisionTreeClassifier(),
            'svc': SVC(),
            'xgboost': XGBClassifier()
        }

    def preprocess_text(self, text):
        """
        Realiza o pré-processamento do texto, incluindo a vetorização.

        Args:
            text (str): O texto a ser pré-processado.

        Returns:
            numpy.ndarray: O vetor pré-processado.
        """
        sanitized_phrase = TextPreprocessor.sanitize_phrase(text)
        vectorized_phrase = self.cv.transform([sanitized_phrase]).toarray()
        standardized_vector = self.sc.transform(vectorized_phrase)
        return standardized_vector

    def train_models(self, x, y):
        """
        Treina os modelos do classificador de sentimento.

        Args:
            x (numpy.ndarray): As características do conjunto de treinamento.
            y (numpy.ndarray): Os rótulos do conjunto de treinamento.
        """
        for model_name, model in self.models.items():
            model.fit(x, y)

    def predict_sentiment(self, text, model_name):
        """
        Realiza a previsão do sentimento do texto usando o modelo especificado.

        Args:
            text (str): O texto a ser classificado.
            model_name (str): O nome do modelo a ser utilizado.

        Returns:
            int: A classe de sentimento prevista.
        """
        standardized_vector = self.preprocess_text(text)
        model = self.models[model_name]
        prediction = model.predict(standardized_vector)
        return int(prediction)
#
# Classe de serviço de aplicação
class ModelService:
    def __init__(self):
        self.sentiment_classifier = None
        self.data_loader = None

    def bootstrap(self):
        """
        Realiza a inicialização do serviço de modelo, carregando os dados e treinando os modelos.
        """
        colab_events_train = self.data_loader.load_data()
        words = self.sentiment_classifier.cv.fit_transform(
            colab_events_train.description)
        x = self.sentiment_classifier.sc.fit_transform(words.toarray())
        y = colab_events_train.iloc[:, 1]
        self.sentiment_classifier.train_models(x, y)

    def predict_sentiment(self, phrase, model_name):
        """
        Realiza a previsão do sentimento da frase usando o modelo especificado.

        Args:
            phrase (str): A frase a ser classificada.
            model_name (str): O nome do modelo a ser utilizado.

        Returns:
            dict: O resultado da previsão de sentimento.
        """
        prediction = self.sentiment_classifier.predict_sentiment(
            phrase, model_name)
        return {'sentiment': prediction}
#####################################################
load_dotenv()  # Carregar variáveis de ambiente do arquivo .env
#
##
class App:
    """
    Classe responsável por encapsular as funcionalidades do Flask e fornecer rotas para previsão de sentimento.

    Attributes:
        app (Flask): Instância do aplicativo Flask.
        model_service (ModelService): Instância do serviço de modelo.
        is_training (bool): Variável para indicar se o treinamento está em andamento.

    Methods:
        predict(): Rota para previsão de sentimento.
        initialize_model_service(): Inicializa o serviço de modelo.
        get_status(): Rota para obter o status da aplicação.
        run(): Executa o aplicativo Flask.
    """

    def __init__(self):
        """
        Inicializa a classe App.

        Initializes:
            app (Flask): Instância do aplicativo Flask.
            model_service (ModelService): Instância do serviço de modelo.
            is_training (bool): Variável para indicar se o treinamento está em andamento.
        """
        self.app = Flask(__name__)
        self.model_service = ModelService()
        self.is_training = True

        self.app.route('/predict', methods=['POST'])(self.predict)
        self.app.route('/status', methods=['GET'])(self.get_status)
        self.app.before_first_request(self.initialize_model_service)    

    def initialize_model_service(self):
        """
        Inicializa o serviço de modelo.

        Este método é executado antes da primeira requisição ao aplicativo Flask.
        Carrega os dados e treina os modelos.
        """
        self.model_service.data_loader = DataLoader()
        self.model_service.sentiment_classifier = SentimentClassifier()

        # Inicia o treinamento em uma thread separada
        training_thread = Thread(target=self.train_models_thread)
        training_thread.start()

    def train_models_thread(self):
        """
        Método executado em uma thread separada para realizar o treinamento dos modelos.
        """
        self.is_training = True
        colab_events_train = self.model_service.data_loader.load_data()
        words = self.model_service.sentiment_classifier.cv.fit_transform(colab_events_train.description)
        x = self.model_service.sentiment_classifier.sc.fit_transform(words.toarray())
        y = colab_events_train.iloc[:, 1]
        self.model_service.sentiment_classifier.train_models(x, y)
        self.is_training = False

    def get_status(self):
        """
        Rota para obter o status da aplicação, incluindo a porcentagem de conclusão do treinamento.

        Returns:
            str: O status da aplicação com a porcentagem de conclusão do treinamento.
        """
        if self.is_training:
            progress = self.calculate_training_progress()
            status = {'status': 'Training in progress', 'progress': progress}
        else:
            status = {'status': 'Available'}

        return jsonify(status)

    def calculate_training_progress(self):
        """
        Calcula a porcentagem de conclusão do treinamento.

        Returns:
            float: A porcentagem de conclusão do treinamento.
        """
        total_steps = len(self.model_service.sentiment_classifier.models)
        completed_steps = total_steps - sum([model.n_jobs for model in self.model_service.sentiment_classifier.models.values()])
        progress = (completed_steps / total_steps) * 100
        return progress
##
if __name__ == '__main__':
    app = App()
    app.run()
