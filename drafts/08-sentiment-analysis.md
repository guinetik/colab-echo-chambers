# Introdução à Análise de Sentimento

A análise de sentimento é uma técnica de processamento de linguagem natural que envolve a identificação e extração de informações subjetivas a partir de dados textuais. Esse processo pode ser usado para identificar a polaridade, ou tom emocional, de um determinado texto, o que pode ser útil em várias aplicações, como pesquisa de mercado e análise de mídias sociais. Pesquisas anteriores demonstraram a utilidade da análise de sentimento em diversos domínios, incluindo política, negócios e saúde (Pang & Lee, 2008; Chen et al., 2014; Nguyen et al., 2015).

Técnicas de aprendizado de máquina podem ser usadas para automatizar o processo de análise de sentimento. Essas técnicas envolvem o treinamento de um modelo de aprendizado de máquina em um conjunto de dados rotulados, onde os rótulos indicam a polaridade dos dados textuais. Uma vez treinado, o modelo pode ser usado para prever a polaridade de novos dados textuais que não foram vistos anteriormente. Algoritmos de aprendizado de máquina comumente usados para análise de sentimento incluem regressão logística, máquinas de vetor de suporte e redes neurais (Haddi et al., 2013; Kim, 2014).

## Aplicações da Análise de Sentimento na mitigação de Câmaras de Eco

No contexto da polarização em redes sociais, a Análise de Sentimento é uma ferramenta poderosa para detectar e mitigar a formação de câmaras de eco. Pesquisas anteriores mostraram que a análise de sentimento pode ser usada para identificar as crenças e inclinações políticas dos usuários com base em sua linguagem e sentimento expressos em postagens de mídias sociais. Algoritmos de aprendizado de máquina, como Naive Bayes, Random Forest e Support Vector Machines (SVM), têm sido amplamente utilizados para análise de sentimento (Hutto & Gilbert, 2014).

Para identificar câmaras de eco, a análise de sentimento pode ser usada como uma métrica para medir a homofilia em uma rede social. A homofilia refere-se à tendência dos indivíduos de se associarem com outros que são semelhantes a eles em termos de características, opiniões e sentimentos. Ao analisar o sentimento expresso nas postagens de usuários, podemos determinar se um grupo de usuários está polarizado, ou seja, se a maioria de suas postagens apresenta um sentimento ou inclinação política semelhante.

A análise de sentimento permite medir o grau de polarização dentro desse grupo, fornecendo uma medida quantitativa do nível de homofilia na rede. Se os usuários dentro de um grupo apresentarem predominantemente sentimentos semelhantes, isso indica uma maior homofilia e uma maior probabilidade de formação de uma câmara de eco.

Além de identificar a polarização, a análise de sentimento também pode revelar os tópicos específicos que estão impulsionando a polarização dentro dessas câmaras de eco. Ao examinar o conteúdo das postagens e identificar os principais temas discutidos, é possível compreender melhor os fatores que contribuem para a formação e manutenção dessas câmaras de eco.

Com essa abordagem, a análise de sentimento não apenas fornece insights sobre a polarização em uma rede social, mas também ajuda a identificar os grupos de usuários que estão mais propensos a formar câmaras de eco e a perpetuar a polarização. Essas informações são valiosas para a compreensão dos padrões de interação e para o desenvolvimento de estratégias de mitigação da polarização e promoção do diálogo diversificado e inclusivo.

Por exemplo, em um estudo de Colleoni et al. (2014), a análise de sentimento foi usada para medir a polarização de usuários em discussões políticas no Twitter. Os autores descobriram que os usuários tendem a se agrupar em torno de indivíduos com opiniões semelhantes e que esse agrupamento leva à formação de câmaras de eco. Os autores sugeriram que a análise de sentimento poderia ser usada para identificar os usuários que estão impulsionando a polarização e direcioná-los com contra-argumentos ou pontos de vista alternativos.

# Análise de sentimento das postagens do Colab.re

O objetivo deste experimento é criar duas métricas adicionais no modelo de dados dos usuários do Colab: score e persona. O score se refere à classificação das postagens do usuário como positiva ou negativa de acordo com os dicionários léxicos. A classificação de persona envolve o usuário ser classificado como "helper" ou "complainer" de acordo com critérios específicos.

## 2.2 Score

O score é uma métrica que classifica as postagens do usuário como positivas ou negativas. Esta classificação é baseada em dicionários léxicos, que são conjuntos de palavras pré-definidas associadas a uma polaridade de sentimento (positiva, negativa ou neutra). A análise de sentimento tem sido aplicada em quase todos os domínios de negócios e sociais, pois as opiniões são centrais para quase todas as atividades humanas e são influenciadores-chave de nossos comportamentos (Zhang & Liu, 2012)[^1^].

## 2.2 Persona

Personas são representações fictícias e generalizadas de um grupo de usuários que compartilham características e comportamentos semelhantes. No contexto das redes sociais, as personas representam os diferentes tipos de usuários que interagem dentro dessas plataformas. Essas personas podem ser identificadas e categorizadas com base em uma variedade de fatores, incluindo, entre outros, seus comportamentos online, interesses, padrões de comunicação e atividades de postagem.

A análise de personas é uma área de pesquisa significativa, pois ajuda a entender melhor os usuários de redes sociais e a forma como interagem e se comportam online. Por exemplo, a pesquisa de Jung et al. (2018) apresenta a Geração Automática de Personas (APG), um sistema e metodologia para gerar quantitativamente personas usando grandes quantidades de dados de mídia social online. Este sistema permite identificar segmentos de público distintos e impactantes, criando perfis de personas aprimorados com características pertinentes, como nomes, fotos e interesses.

No contexto do Colab.re, propomos a hipótese de duas personas principais: os "Helpers" e os "Complainers". Essas personas são identificadas com base em suas atividades de postagem e interações dentro da plataforma.

### Helper

A persona "helper" é caracterizada por um comportamento proativo e colaborativo em uma comunidade online. Esses indivíduos são frequentemente encontrados respondendo a perguntas, oferecendo conselhos e compartilhando informações úteis com outros membros da comunidade. Eles tendem a expressar sentimentos positivos em suas postagens e são motivados pelo desejo de ajudar os outros e contribuir para a comunidade.

Os "helpers" são fundamentais para o sucesso de qualquer comunidade online, pois eles ajudam a criar um ambiente de apoio e colaboração. Eles são frequentemente vistos como líderes informais ou especialistas em suas respectivas áreas de interesse. Eles podem ser motivados por uma variedade de fatores, incluindo o desejo de compartilhar conhecimento, a satisfação de ajudar os outros, ou o reconhecimento e respeito que recebem da comunidade.

### Complainer

A persona "complainer" é caracterizada por um comportamento mais crítico ou negativo em uma comunidade online. Esses indivíduos são frequentemente encontrados expressando insatisfação, fazendo reclamações ou criticando outros membros da comunidade ou a comunidade como um todo. Eles tendem a expressar sentimentos negativos em suas postagens e são motivados por uma variedade de fatores, incluindo frustração, descontentamento ou a necessidade de expressar suas opiniões.

Os "complainers" desempenham um papel importante em qualquer comunidade online, pois eles ajudam a identificar problemas, desafios ou áreas de melhoria. Embora suas postagens possam ser percebidas como negativas, elas podem fornecer feedback valioso que pode ser usado para melhorar a comunidade. No entanto, é importante gerenciar e responder adequadamente a esses usuários para evitar a criação de um ambiente negativo ou tóxico.

## 2.3 Relevância das Personas "Helpers" e "Complainers" no Colab.re

A presença das personas "Helpers" e "Complainers" dentro do Colab.re é altamente relevante para o ecossistema dessa plataforma colaborativa. Ambas as personas desempenham papéis distintos e complementares que podem influenciar a experiência do usuário e fornecer insights valiosos para o aprimoramento contínuo do aplicativo. A seguir, são apresentados os argumentos que sustentam a relevância dessas personas específicas:

### 2.3.1 Helpers: Fomentando a Colaboração e o Aprendizado Coletivo

Os Helpers desempenham um papel fundamental no Colab.re, pois contribuem ativamente para a comunidade, oferecendo suporte, compartilhando conhecimento e fornecendo soluções para os desafios enfrentados pelos usuários. Eles ajudam a fomentar a colaboração e o aprendizado coletivo, tornando-se recursos valiosos para aqueles que precisam de assistência ou orientação. Sua presença cria um ambiente propício para troca de ideias, resolução de problemas e crescimento mútuo.

Ao compartilhar suas habilidades e conhecimentos, os Helpers estabelecem uma cultura de generosidade e reciprocidade dentro da comunidade do Colab.re. Eles inspiram outros usuários a se envolverem ativamente, encorajando a participação e a colaboração entre os membros. Além disso, a presença de Helpers é essencial para garantir que novos usuários se sintam bem-vindos e apoiados, promovendo assim um ambiente inclusivo e acolhedor.

### 2.3.2 Complainers: Destacando Problemas e Áreas de Melhoria

Embora os Complainers possam ser vistos como usuários críticos ou negativos, sua presença é igualmente importante para o Colab.re. Essas personas desempenham o papel de destacar problemas, lacunas e áreas de melhoria dentro do aplicativo. Ao expressar suas preocupações e insatisfações, eles fornecem um feedback valioso que pode impulsionar o aprimoramento contínuo da plataforma.

Os Complainers atuam como "sentinelas" da comunidade, chamando a atenção para questões que podem ter sido negligenciadas ou passado despercebidas. Suas críticas construtivas podem levar a melhorias significativas na usabilidade, funcionalidade e qualidade geral do Colab.re. Além disso, ao abordar e resolver essas preocupações, a equipe responsável pelo desenvolvimento do aplicativo demonstra seu compromisso com a satisfação e o engajamento dos usuários.

### 2.3.3 Sinergia entre Helpers e Complainers

A interação entre as personas "Helpers" e "Complainers" no Colab.re é uma relação simbiótica que impulsiona o crescimento e o aprimoramento contínuo da plataforma. Os Helpers oferecem suporte, orientação e soluções, tornando o ambiente colaborativo e enriquecedor. Por outro lado, os Complainers fornecem feedback crítico e identificam áreas de melhoria, promovendo a evolução e aprimoramento do aplicativo. Essa sinergia entre essas personas complementares é essencial para criar uma comunidade vibrante, responsiva e em constante aprimoramento no Colab.re.

Nas próximas páginas, detalharemos as técnicas e metodologias utilizadas para identificar e classificar as personas "Helpers" e "Complainers" dentro do Colab.re, fornecendo uma visão mais aprofundada sobre a implementação dessas personas e sua contribuição para a análise de dados e aprimoramento da plataforma.

# 3. Classificação por score

## 3.1. Treinamento da classificação de postagens por Score

Para treinar um modelo de classificação de sentimento, utilizamos um script Python executado no ambiente do Google Colaboratory. Este modelo foi treinado usando um conjunto de dados de treinamento que consiste em postagens de usuário rotuladas como positivas ou negativas. O modelo então aprende a associar certas palavras e frases a sentimentos positivos ou negativos.

O script (prover referencia do script) é um exemplo de aplicação de técnicas de Processamento de Linguagem Natural (PLN) e Análise de Sentimentos para criar um conjunto de dados de treinamento para um algoritmo de classificação de sentimentos. O objetivo é analisar postagens do Colab.re, e classificá-las como positivas ou negativas com base em seu conteúdo textual.

O script utiliza uma abordagem de pontuação de sentimentos, onde cada postagem é atribuída a um score de sentimento que varia de 0 a 1. Um score próximo a 0 indica um sentimento negativo, enquanto um score próximo a 1 indica um sentimento positivo. Esta métrica de sentimento fornece uma maneira quantitativa de medir o sentimento geral expresso em uma postagem. Isso pode oferecer insights valiosos sobre a percepção dos usuários sobre diferentes tópicos, permitindo a identificação de problemas emergentes, a avaliação da satisfação do usuário e a orientação de estratégias de engajamento.

Para realizar a análise de sentimentos, o script emprega várias técnicas de PLN, incluindo tokenização, lematização e remoção de palavras de parada. A tokenização é o processo de dividir o texto em palavras individuais ou "tokens". A lematização é o processo de reduzir as palavras à sua forma base ou raiz, o que ajuda a consolidar diferentes formas da mesma palavra. A remoção de palavras de parada envolve a eliminação de palavras comuns que geralmente não contribuem para o significado de uma frase, como "e", "o" e "em".

O script utiliza quatro dicionários léxicos diferentes para a análise de sentimentos: OpLexicon, SenticNet, UniLex e WordNetAffectBR. Cada dicionário léxico contém uma lista de palavras junto com um valor de polaridade associado que indica o sentimento geral da palavra (positivo, negativo ou neutro).

- OpLexicon: É um dicionário léxico para o idioma português que contém mais de 32.000 palavras, cada uma com um valor de polaridade associado.
- SenticNet: É um dicionário léxico multilíngue que fornece valores de polaridade para palavras com base em sua semântica e psicologia.
- UniLex: É um dicionário léxico multilíngue que fornece valores de polaridade para palavras com base em uma variedade de recursos linguísticos.
- WordNetAffectBR: É uma versão em português do WordNet-Affect, um dicionário léxico que fornece valores de polaridade para palavras com base em sua associação com diferentes emoções.

O script compara a eficácia desses dicionários léxicos analisando a mesma frase com cada dicionário e calculando a polaridade resultante. Isso permite uma avaliação objetiva de qual dicionário léxico é mais eficaz para a análica de sentimentos no contexto específico das postagens do Colab.

Finalmente, o script cria um conjunto de dados de treinamento selecionando as 1000 postagens com os scores de sentimento mais altos e as 1000 postagens com os scores de sentimento mais baixos. Este conjunto dedados de treinamento pode ser usado para treinar um algoritmo de aprendizado de máquina para classificar automaticamente o sentimento das postagens do Colab. A ideia é que o algoritmo aprenda a associar certos padrões de palavras e frases com sentimentos positivos ou negativos com base nos exemplos fornecidos no conjunto de dados de treinamento.

O script também inclui uma etapa de pré-processamento de texto, que envolve a conversão de todo o texto para minúsculas, a tokenização do texto em palavras individuais, a lematização das palavras para sua forma base e a remoção de palavras de parada e pontuação. Este pré-processamento é uma etapa crucial para garantir que o texto esteja em um formato que possa ser facilmente analisado e interpretado pelo algoritmo de aprendizado de máquina.

O script também utiliza a biblioteca Spacy para o processamento de linguagem natural e a biblioteca NLTK (Natural Language Toolkit) para tarefas como a tokenização e a lematização. Além disso, ele usa a biblioteca pandas para manipulação de dados e a biblioteca matplotlib para visualização de dados.

Em resumo, este script Python demonstra como as técnicas de processamento de linguagem natural e análise de sentimentos podem ser usadas para criar um conjunto de dados de treinamento para um algoritmo de classificação de sentimentos. O conjunto de dados resultante pode ser usado para treinar um algoritmo de aprendizado de máquina para classificar automaticamente o sentimento das postagens do Colab, proporcionando insights valiosos sobre a percepção dos usuários.

## 3.2. Classificação de Score

Nesta seção, descrevemos a metodologia empregada para a análise de dados e a construção do modelo de aprendizado de máquina. O código foi implementado em Python, utilizando várias bibliotecas para análise de dados, visualização, pré-processamento de texto e aprendizado de máquina.

Os dados foram carregados a partir de URLs fornecidos, que continham informações sobre eventos postados por usuários em uma plataforma social. Realizamos várias etapas de pré-processamento nos dados, incluindo a remoção de padrões indesejados, a conversão de texto para minúsculas, a divisão de texto em palavras (tokenização), a remoção de palavras irrelevantes (stopwords), e a redução das palavras à sua forma base (stemming) [1].

Realizamos uma análise exploratória dos dados para entender melhor as características dos dados. Isso incluiu a visualização da distribuição das palavras mais frequentes e a criação de nuvens de palavras para postagens positivas e negativas. Além disso, utilizamos a biblioteca Word2Vec para criar um modelo de palavras em vetores, que foi usado para visualizar as associações de palavras mais comuns [2].

Para converter o texto em uma representação numérica que pudesse ser usada por algoritmos de aprendizado de máquina, utilizamos a técnica de "Bag of Words" [3]. Esta técnica transforma o texto em uma matriz de ocorrências de palavras no corpus de texto.

Após a extração de recursos, dividimos os dados em conjuntos de treinamento e validação. Em seguida, padronizamos os dados para garantir que todas as características tivessem a mesma escala [4].

Utilizamos vários algoritmos de aprendizado de máquina para classificar as postagens como positivas ou negativas, incluindo RandomForestClassifier, LogisticRegression, DecisionTreeClassifier, SVC e XGBClassifier [5]. Para cada modelo, calculamos a acurácia do treinamento e da validação, a pontuação F1 e a matriz de confusão.

No que diz respeito à modelagem de aprendizado de máquina, os resultados foram os seguintes:

- RandomForestClassifier: O modelo RandomForestClassifier alcançou uma acurácia de treinamento de 0.996 e uma acurácia de validação de 0.172 na última execução em 19 de maio de 2022. Em uma execução anterior em 15 de maio de 2022, a acurácia de treinamento foi de 1.0 e a acurácia de validação foi de 0.14.
- LogisticRegression: O modelo LogisticRegression obteve uma acurácia de treinamento de 0.996 e uma acurácia de validação de 0.164 na última execução em 19 de maio de 2022. Em uma execução anterior em 15 de maio de 2022, a acurácia de treinamento foi de 1.0 e a acurácia de validação foi de 0.16.
- DecisionTreeClassifier: O modelo DecisionTreeClassifier alcançou uma acurácia de treinamento de 0.996 e uma acurácia de validação de 0.13 na última execução em 19 de maio de 2022. Em uma execução anterior em 15 de maio de 2022, a acurácia de treinamento foi de 1.0 e a acurácia de validação foi de 0.1.
- SVC: O modelo SVC obteve uma acurácia de treinamento de 0.395 e uma acurácia de validação de 0.098 na última execução em 19 de maio de 2022. Em uma execução anterior em 15 de maio de 2022, a acurácia de treinamento foi de 0.5906 e a acurácia de validação foi de 0.1.
- XGBClassifier: Na última execução em 15 de maio de 2022, o modelo XGBClassifier alcançou uma acurácia de treinamento de 0.3154 e uma acurácia de validação de 0.1.

Esses resultados indicam que o modelo RandomForestClassifier teve o melhor desempenho em termos de acurácia de treinamento, enquanto o modelo LogisticRegression teve a melhor acurácia de validação. No entanto, todos os modelos apresentaram uma grande diferença entre as acurácias de treinamento e validação, sugerindo que os modelos podem estar sofrendo de overfitting. Isso significa que os modelos estão se ajustando muito bem aos dados de treinamento, mas não estão generalizando bem para novos dados. Futuras iterações deste trabalho podem explorar técnicas para mitigar o overfitting, como a regularização ou o uso de mais dados de treinamento.

Referências

[1] Bird, S., Klein, E., & Loper, E. (2009). Natural language processing with Python: analyzing text with the natural language toolkit. " O'Reilly Media, Inc.".

[2] Mikolov, T., Chen, K., Corrado, G., & Dean, J. (2013). Efficient estimation of word representations in vector space. arXiv preprint arXiv:1301.3781.

[3] Harris, Z. S. (1954). Distributional structure. Word, 10(2-3), 146-162.

[4] Jain, A. K., Duin, R. P., & Mao, J. (2000). Statistical pattern recognition: A review. IEEE Transactions on pattern analysis and machine intelligence, 22(1), 4-37.

[5] Kotsiantis, S. B., Zaharakis, I., & Pintelas, P. (2007). Supervised machine learning: A review of classification techniques. Emerging artificial intelligence applications in computer engineering, 160.

# 4. Classificação das personas

## 4.1. Geração de Dados de Treinamento para Classificação de Persona

Os dados de treinamento para a classificação de persona foram gerados usando o ChatGPT. O ChatGPT foi treinado para gerar postagens de usuário que são representativas de "helpers" e "complainers". Estas postagens foram então usadas para treinar o modelo de classificação de persona.

## 4.2. Classificação de personas

Utilizamos novamente o Python para classificar os usuários como "helpers" ou "complainers". Este script utiliza o modelo de classificação de sentimento treinado para analisar as postagens dos usuários e determinar se eles são mais propensos a ajudar ou reclamar.

# 5. Homofilia e Câmaras de Eco

As métricas de homofilia geradas a partir deste experimento podem ajudar a detectar câmaras de eco em um grafo da rede do Colab. Câmaras de eco são fenômenos sociais onde as opiniões e informações são amplificadas ou reforçadas pela comunicação e repetição dentro de um sistema fechado e podem contribuir para a polarização social. Ao identificar e entender estas câmaras de eco, podemos desenvolver estratégias para promover a diversidade de opiniões e a comunicação aberta.