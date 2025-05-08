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
