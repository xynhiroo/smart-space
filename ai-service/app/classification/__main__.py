"""Entrypoint untuk menjalankan runner klasifikasi via `python -m app.classification`."""

import sys
from app.classification.cli import parse_args, run_classification_cli

if __name__ == "__main__":
    args = parse_args()
    sys.exit(run_classification_cli(args))
