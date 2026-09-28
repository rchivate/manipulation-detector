# Communication Pattern Explorer

## Project Overview
A local NLP demonstration that classifies text into `healthy`, `gaslighting`, `guilt_tripping`, `emotional_blackmail`, `emotional_pressure`, or `blame_shifting`. It predicts language patterns, not intent, truth, or a clinical conclusion.

## Features
- Train a TF-IDF unigram/bigram and balanced logistic regression classifier.
- Stratified train/test evaluation saved as JSON; probability scores and influential n-grams.
- Local FastAPI web page and JSON endpoint; no persistence or external model service.
- Uncertain response when the highest score falls below the configurable threshold.

## Dataset
`data/sample.csv` contains **48 synthetic examples**, eight per class, for a runnable demonstration. It is not a validated psychology dataset. To use a research dataset, obtain it under its own terms, document consent/licensing and provenance, remove personal information, map labels to the six categories, and supply a UTF-8 CSV with `text,label` columns. Keep conversations from the same source/person together when splitting a real dataset to prevent leakage. The included train script makes a stratified random split and should not be used as a final research evaluation on related dialogues.

## Installation
Python 3.10+ is recommended. From this directory:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## How to Run
```bash
python -m src.train
python -m src.predict "I remember our meeting differently. Can we review the notes?"
uvicorn src.app:app --host 127.0.0.1 --port 8000
```
Open http://127.0.0.1:8000 . The API accepts `POST /predict` with JSON `{"text":"...","threshold":0.25}`. Interactive API docs: http://127.0.0.1:8000/docs . Use `python -m src.train --data path/to/labeled.csv --output models` for your own dataset. A trained model is generated locally in `models/` and is not bundled. Set `MODEL_PATH` to load a different trained file.

## Example Inputs and Outputs
The page includes a clear gaslighting-like example, healthy disagreement, and ambiguous statement. Outputs contain `label`, `top_candidate`, `confidence`, all class `scores`, and `influential_phrases`. Scores depend on training and are not calibrated probabilities of actual manipulation; low-confidence predictions return `uncertain`.

## Model/Prediction Explanation
`DataPreprocessor` validates text, normalizes whitespace, and can tokenize for inspection; the vectorizer handles its own word/ngram tokenization. `ManipulationDetector.load_model()` caches the trained pipeline in an instance. `predict_manipulation()` returns model class scores. `get_prediction_explanation()` reports positively weighted TF-IDF features for the top candidate class. These correlations do not prove why a speaker wrote a message. The web UI is in `src/app.py`.

## Limitations
Synthetic examples are short and formulaic. The model can miss context, irony, quoting, cultural differences, power dynamics, and repeated patterns across conversations. The labels may overlap; this first version chooses one class. False positives and false negatives are expected. Do not use scores for HR discipline, safety decisions, diagnosis, or judgments about individuals. Avoid entering identifiable private conversations into any deployment without appropriate consent and safeguards. This software is not professional advice.

## Contributors
Project starter implementation; add contributor names and roles here.

## License
MIT; see `LICENSE`. Dataset samples were created for this demonstration. External datasets retain their own licenses.
