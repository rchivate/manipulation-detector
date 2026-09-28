import argparse
import csv
import json
from collections import Counter
from pathlib import Path
import joblib
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from .model import LABELS, DataPreprocessor, build_model


def train(data_path: Path, output_dir: Path, test_size: float = 0.25):
    with data_path.open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    if not rows or not {'text', 'label'}.issubset(rows[0]):
        raise ValueError('CSV needs text and label columns.')
    preprocessor = DataPreprocessor()
    texts = [preprocessor.clean(row['text']) for row in rows]
    labels = [row['label'].strip() for row in rows]
    unknown = set(labels) - set(LABELS)
    if unknown:
        raise ValueError(f'Unknown labels: {sorted(unknown)}')
    if len(set(texts)) != len(texts):
        raise ValueError('Duplicate texts found; remove duplicates before splitting.')
    counts = Counter(labels)
    if len(counts) != len(LABELS) or min(counts.values()) < 2:
        raise ValueError('Provide at least two examples per label.')
    x_train, x_test, y_train, y_test = train_test_split(texts, labels, test_size=test_size, random_state=42, stratify=labels)
    model = build_model().fit(x_train, y_train)
    predictions = model.predict(x_test)
    report = {'dataset_rows': len(rows), 'train_rows': len(x_train), 'test_rows': len(x_test),
              'classification_report': classification_report(y_test, predictions, labels=LABELS, output_dict=True, zero_division=0),
              'labels': LABELS, 'confusion_matrix': confusion_matrix(y_test, predictions, labels=LABELS).tolist(),
              'warning': 'Synthetic demonstration data. These metrics do not establish real-world validity.'}
    output_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_dir / 'model.joblib')
    (output_dir / 'evaluation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f'Saved {output_dir / "model.joblib"} and {output_dir / "evaluation.json"}')
    print(f'Macro F1: {report["classification_report"]["macro avg"]["f1-score"]:.3f} (demonstration only)')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=Path, default=Path('data/sample.csv'))
    parser.add_argument('--output', type=Path, default=Path('models'))
    args = parser.parse_args()
    train(args.data, args.output)
