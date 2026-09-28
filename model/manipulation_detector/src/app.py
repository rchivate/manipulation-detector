import html
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from .model import ManipulationDetector

app = FastAPI(title='Communication Pattern Explorer', version='0.1.0')
detector = ManipulationDetector(os.getenv('MODEL_PATH', 'models/model.joblib'))

class Input(BaseModel):
    text: str = Field(min_length=1, max_length=10000)
    threshold: float = Field(default=0.25, ge=0, le=1)

@app.post('/predict')
def predict(payload: Input):
    try:
        return detector.predict_manipulation(payload.text, payload.threshold)
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400 if isinstance(exc, ValueError) else 503, detail=str(exc)) from exc

@app.get('/', response_class=HTMLResponse)
def home():
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Communication Pattern Explorer</title><style>body{font:17px system-ui;max-width:760px;margin:4rem auto;padding:0 1rem;line-height:1.5}textarea{width:100%;height:170px}button{padding:.65rem 1rem;margin:.5rem .4rem .5rem 0}pre{white-space:pre-wrap;background:#f4f4f4;padding:1rem}small{color:#555}</style><h1>Communication Pattern Explorer</h1><p>Explore language patterns in a message. A label is a model prediction, not a judgment about a person or their intent.</p><textarea id="input" aria-label="Message to analyze" placeholder="Paste a message here"></textarea><br><button id="analyze">Analyze</button><button class="example" data-text="You are imagining things. That never happened, and you always remember it wrong.">Gaslighting-like example</button><button class="example" data-text="I remember our meeting differently. Can we review the notes together?">Healthy example</button><button class="example" data-text="I hoped you would help me today.">Ambiguous example</button><pre id="result" aria-live="polite"></pre><small>Demo data is synthetic. Do not submit private conversations to a server you do not trust. Results are not professional advice.</small><script>document.querySelectorAll('.example').forEach(b=>b.onclick=()=>document.querySelector('#input').value=b.dataset.text);document.querySelector('#analyze').onclick=async()=>{const out=document.querySelector('#result');out.textContent='Analyzing…';try{const r=await fetch('/predict',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:document.querySelector('#input').value})});const data=await r.json();out.textContent=JSON.stringify(data,null,2)}catch(e){out.textContent=String(e)}}</script></html>'''
