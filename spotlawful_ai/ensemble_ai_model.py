import numpy as np
from spotlawful_ai.simple_ai_model import SimpleAIModel

class EnsembleAIModel:
    def __init__(self, n_models=5):
        self.models = [SimpleAIModel() for _ in range(n_models)]

    def train(self, x_train, y_train, epochs=10, learning_rate=0.01):
        # Train each model on the same data
        for model in self.models:
            model.train(x_train, y_train, epochs, learning_rate)

    def predict(self, x):
        # Aggregate predictions from all models by averaging
        predictions = np.array([model.predict(x) for model in self.models])
        return np.mean(predictions, axis=0)

    def parse(self, text, hierarchical=False):
        # Delegate parse to the first model if it has parse method
        if hasattr(self.models[0], 'parse'):
            return self.models[0].parse(text, hierarchical=hierarchical)
        else:
            raise NotImplementedError("Parse method is not implemented in the underlying models.")

    def fine_tune_with_feedback(self, feedback):
        # Fine-tune all models with user feedback
        for model in self.models:
            model.fine_tune_with_feedback(feedback)

    def train_on_new_data(self, new_data):
        # Train all models on new data incrementally
        for model in self.models:
            model.train_on_new_data(new_data)

    def evaluate_model(self):
        # Evaluate all models and return average performance
        performances = [model.evaluate_model() for model in self.models]
        avg_performance = sum(performances) / len(performances)
        print(f"Ensemble model average performance: {avg_performance}")
        return avg_performance
