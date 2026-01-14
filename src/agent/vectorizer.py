import numpy as np


class FeatureVectorizer:

    def __init__(self, model):
        self.feature_names = list(model.feature_names_in_)

    def vectorize(self, prefs):
        vector = [
            getattr(prefs, name)
            for name in self.feature_names
        ]

        return np.array([vector])
