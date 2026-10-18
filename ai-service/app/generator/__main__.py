"""Entrypoint untuk menjalankan generator via `python -m app.generator`."""

import sys
from app.generator.cli import parse_args, run_generator

if __name__ == "__main__":
    args = parse_args()
    sys.exit(run_generator(args))
