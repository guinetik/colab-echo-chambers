metrics_training_url = "https://drive.google.com/uc?export=download&id=1UBx1lTHipKqwVwFO7Sz4WAu-PsgQmFdG"
metrics_training = pd.read_csv(metrics_training_url, sep=',', decimal='.', header=0, low_memory=False)
metrics_training
# create a Random Forest Classifier to predict the is_echo_chamber variable
