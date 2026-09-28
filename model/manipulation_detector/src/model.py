import re
from pathlib import Path
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

LABELS = ['healthy', 'gaslighting', 'guilt_tripping', 'emotional_blackmail', 'emotional_pressure', 'blame_shifting']

class DataPreprocessor:
    def clean(self, text: str) -> str:
        if not isinstance(text, str) or not text.strip():
            raise ValueError('Provide nonempty text.')
        return re.sub(r'\s+', ' ', text).strip()

    def tokenize(self, text: str) -> list[str]:
        return re.findall(r"\b[\w']+\b", self.clean(text).lower())


def build_model() -> Pipeline:
    return Pipeline([('tfidf', TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)),
                     ('classifier', LogisticRegression(max_iter=2000, class_weight='balanced', random_state=42))])

class ManipulationDetector:
    def __init__(self, model_path: str | Path = 'models/model.joblib'):
        self.model_path = Path(model_path)
        self.preprocessor = DataPreprocessor()
        self.model = None

    def load_model(self):
        if self.model is None:
            if not self.model_path.is_file():
                raise FileNotFoundError(f'Model missing: {self.model_path}. Run: python -m src.train')
            self.model = joblib.load(self.model_path)
        return self.model

    def get_prediction_explanation(self, text: str, label: str, limit: int = 5) -> list[dict]:
        model = self.load_model()
        vectorizer, classifier = model.named_steps['tfidf'], model.named_steps['classifier']
        row = vectorizer.transform([text]).tocoo()
        class_index = list(classifier.classes_).index(label)
        weights = classifier.coef_[class_index]
        terms = vectorizer.get_feature_names_out()
        candidates = [(terms[col], float(value * weights[col])) for col, value in zip(row.col, row.data) if value * weights[col] > 0]
        candidates.sort(key=lambda item: item[1], reverse=True)
        return [{'phrase': phrase, 'contribution': round(score, 4)} for phrase, score in candidates[:limit]]

    def predict_manipulation(self, text: str, threshold: float = 0.25) -> dict:
        if not 0 <= threshold <= 1:
            raise ValueError('threshold must be between 0 and 1')
        clean = self.preprocessor.clean(text)
        model = self.load_model()
        probabilities = model.predict_proba([clean])[0]
        classes = model.named_steps['classifier'].classes_
        best = int(np.argmax(probabilities))
        label = str(classes[best]) if probabilities[best] >= threshold else 'uncertain'
        return {'label': label, 'top_candidate': str(classes[best]),
                'confidence': round(float(probabilities[best]), 4),
                'scores': {str(k): round(float(v), 4) for k, v in zip(classes, probabilities)},
                'influential_phrases': self.get_prediction_explanation(clean, str(classes[best])),
                'notice': 'Pattern classification only; context and intent cannot be established from text alone. Not professional advice.'}
