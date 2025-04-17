import pandas as pd

class DataHandler:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self):
        # Load data from a CSV file
        data = pd.read_csv(self.file_path)
        return data

    def preprocess_data(self, data):
        # Example preprocessing steps
        # Here you can add your data cleaning and transformation logic
        return data.dropna()  # Remove missing values as an example
