from model import SpotLawfulAI
from data import DataHandler

def main():
    # Initialize the AI model
    ai_model = SpotLawfulAI()

    # Load and preprocess data
    data_handler = DataHandler('data.csv')  # Example file path
    data = data_handler.load_data()
    processed_data = data_handler.preprocess_data(data)

    # Example: Train the model with processed data
    # Assuming the last column is the target variable
    x_train = processed_data.iloc[:, :-1].values
    y_train = processed_data.iloc[:, -1].values
    ai_model.train(x_train, y_train, epochs=10)

    # Example prediction
    predictions = ai_model.predict(x_train)
    print(predictions)

if __name__ == "__main__":
    main()
