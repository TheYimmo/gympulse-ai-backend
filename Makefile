.PHONY: install install-dev api quality consistency ingest notebook train

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

api:
	uvicorn main:app --reload --port 8000

ingest:
	python scripts/ingest.py

quality:
	python scripts/quality.py

consistency:
	python scripts/consistency.py

notebook:
	cd notebooks && jupyter notebook

train:
	PYTHONPATH=. python scripts/train.py

pipeline: quality consistency
