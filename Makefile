.PHONY: install install-dev api dashboard quality consistency ingest notebook train validate forecast

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

api:
	PYTHONPATH=. .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8080

dashboard:
	GYMPULSE_API_URL=http://localhost:8080 PYTHONPATH=. .venv/bin/streamlit run dashboard/app.py --server.port 8501

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

validate:
	PYTHONPATH=. python scripts/validate.py

forecast:
	PYTHONPATH=. python scripts/forecast.py

pipeline: quality consistency
