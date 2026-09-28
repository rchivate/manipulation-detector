import argparse
import json
from .model import ManipulationDetector

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('text')
    parser.add_argument('--model', default='models/model.joblib')
    parser.add_argument('--threshold', type=float, default=0.25)
    args = parser.parse_args()
    print(json.dumps(ManipulationDetector(args.model).predict_manipulation(args.text, args.threshold), indent=2))
