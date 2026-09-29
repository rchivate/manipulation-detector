# Signal

Signal is a Next.js interface for the local communication-pattern classifier in `../model/manipulation_detector`.

## Run locally

Install the Python model dependencies once:

```powershell
cd ../model/manipulation_detector
python -m pip install -r requirements.txt
cd ../../manipulation-detector-website
npm install
npm run dev
```

The website starts the Python model on demand. The first request trains the bundled synthetic demo data if `model/manipulation_detector/models/model.joblib` is missing. Set `MODEL_PYTHON` if Python is not available as `python` on `PATH`.

## Upload format

Upload a CSV with one conversation per row and a `text`, `cleaned_text`, or `conversation_text` column. An optional `label` column is shown beside predictions. Files are limited to 25 MB and 500 rows per analysis.

The sample download is the model's actual 48-row `text,label` training dataset. It is synthetic demonstration data, not a validated dataset. Predictions describe language patterns and do not establish intent or provide professional advice.
