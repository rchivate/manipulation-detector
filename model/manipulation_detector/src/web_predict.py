import argparse
import contextlib
import csv
import io
import json
import os
import sys
from collections import Counter
from pathlib import Path

from .model import ManipulationDetector
from .train import train


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = ROOT / 'data' / 'sample.csv'
MODEL_PATH = Path(os.getenv('MODEL_PATH', ROOT / 'models' / 'model.joblib'))
MAX_ROWS = 500
TEXT_COLUMNS = ('text', 'cleaned_text', 'conversation_text')


def get_detector() -> ManipulationDetector:
    if not MODEL_PATH.is_file():
        with contextlib.redirect_stdout(io.StringIO()):
            train(SAMPLE_PATH, MODEL_PATH.parent)
    return ManipulationDetector(MODEL_PATH)


def predict_csv(contents: str) -> dict:
    reader = csv.DictReader(io.StringIO(contents.lstrip('\ufeff')))
    if not reader.fieldnames:
        raise ValueError('CSV needs a header row with a text column.')

    columns = {name.strip().lower(): name for name in reader.fieldnames if name}
    text_column = next((columns[name] for name in TEXT_COLUMNS if name in columns), None)
    if text_column is None:
        raise ValueError('CSV needs a text, cleaned_text, or conversation_text column.')

    rows = list(reader)
    if not rows:
        raise ValueError('CSV needs at least one conversation row.')
    if len(rows) > MAX_ROWS:
        raise ValueError(f'CSV is limited to {MAX_ROWS} rows per analysis.')

    detector = get_detector()
    predictions = []
    for row_number, row in enumerate(rows, start=1):
        text = (row.get(text_column) or '').strip()
        if not text:
            raise ValueError(f'Row {row_number} has empty conversation text.')
        prediction = detector.predict_manipulation(text)
        label_column = columns.get('label') or columns.get('manipulation_type')
        prediction['row'] = row_number
        prediction['text'] = text
        if label_column and row.get(label_column):
            prediction['expected_label'] = row[label_column].strip()
        predictions.append(prediction)

    label_counts = Counter(prediction['label'] for prediction in predictions)
    return {
        'total': len(predictions),
        'summary': dict(sorted(label_counts.items())),
        'predictions': predictions,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--health', action='store_true')
    args = parser.parse_args()

    try:
        detector = get_detector()
        if args.health:
            pipeline = detector.load_model()
            result = {'model': 'ready', 'labels': list(pipeline.named_steps['classifier'].classes_)}
        else:
            result = predict_csv(sys.stdin.read())
        print(json.dumps(result))
    except (ValueError, FileNotFoundError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        raise SystemExit(2) from error


if __name__ == '__main__':
    main()