"""Retrain every model and write models/*.joblib.

    python train.py              # all diseases
    python train.py heart liver  # only some
"""
import sys

from core.training import save_all

if __name__ == "__main__":
    save_all(sys.argv[1:] or None)
