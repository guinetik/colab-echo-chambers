# Methodology

The dataset used in this study was obtained in CSV format from the Brazilian app Colab.re. The dataset contains edge lists, which are lists of connections between users, describing user relationships (i.e., who follows whom) and the users' posts from 2016 to 2022. The research was limited to the cities of Caruaru, Rio de Janeiro, Recife, and Niteroi.

To analyse the dataset, a variety of tools were used.

Gephi is an open-source software program used for exploratory data analysis, specifically for visualizing and analyzing complex networks. In this paper, Gephi was utilized to create visualizations for an exploratory network analysis. The program features a variety of tools, including different layout algorithms, node and edge attributes, and statistics. Gephi allows for customization of visualizations, enabling researchers to highlight specific patterns and structures in the data. Its intuitive interface makes it accessible to both researchers and practitioners. By utilizing Gephi in this paper, the we were able to create visualizations that provided insights into the structure of the network under study, enabling them to identify potential patterns and areas for further investigation.

Google Colaboratory, also known as Colab, is a cloud-based platform that provides a free Jupyter notebook environment for users to write and run Python code.Google Colaboratory enables users to leverage Google's computing power by providing access to a high-performance CPU, GPU, and TPU for free. Google Colaboratory notebooks can be used to develop and execute machine learning models, data analysis, and data visualization tasks, among other things. This paper utilizes the platform to take advantage of its computing power for complex data analysis tasks, including network analysis, visualization, and machine learning. Google Colaboratory's collaborative features also allow for seamless collaboration between researchers and facilitate the sharing of code and data with other users. By utilizing Google Colaboratory, this paper aims to improve the efficiency and accessibility of data analysis for researchers with limited computing resources by incentivize migrating to a cloud based platform, specially if it's free. For disambiguation purposes, this paper will always refer to it as Google Colaboratory to avoid confusion with the app Colab.re, object of this paper's study. 

To generate the models for identifying echo chambers, we used Python as the primary programming language. The following popular Python libraries were used:

- NetworkX: a library for the creation, manipulation, and study of complex networks (i.e., graphs
- Pandas: a library for data manipulation and analysis, specifically designed for handling data in a tabular format.
- Matplotlib: a library for creating visualizations such as graphs, charts, and histograms.
- Epidemics: a Python package for simulating and analyzing the spread of diseases using the SIR and SEIR models.

To implement the network analysis techniques used in this study, we used the NetworkX library. This library provides a set of algorithms and functions that enable us to analyze and manipulate complex networks. Specifically, we used the spectral clustering and community Louvain algorithms to identify the communities within the network.

To implement the SIR and SEIR models for digital epidemiology, we used the Epidemics package. This package provides a set of functions that enable us to simulate and analyze the spread of diseases using the SIR and SEIR models. We used these models to simulate the spread of information within the network and identify the groups of users who were most likely to be in an echo chamber.

Overall, the methodology used in this study involved collecting the dataset from the Colab.re app, pre-processing the data using Pandas, and then analyzing the network using NetworkX. We then applied the SIR and SEIR models using the Epidemics package to simulate the spread of information within the network and identify echo chambers. Finally, we used Matplotlib to create visualizations to aid in the interpretation of the results.