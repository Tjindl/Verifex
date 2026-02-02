.PHONY: backend-install backend-serve backend-test docker-build docker-run frontend-install frontend-dev

backend-install:
	cd backend && pip install -r requirements.txt

backend-serve:
	cd backend && python3 -m uvicorn code_explainer.main:app --reload

backend-test:
	cd backend && python3 -m pytest test_api.py

docker-build:
	docker-compose build

docker-run:
	docker-compose up

frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev
