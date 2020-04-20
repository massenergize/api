init:
	pip install -r requirements.txt
.PHONY: init

start:
	python manage.py runserver
.PHONY: start

deploy-prod:
	python prepare-for-deploy.py --prod
	eb deploy
.PHONY: deploy-prod

deploy-dev:
	python prepare-for-deploy.py --dev
	eb deploy
.PHONY: deploy-dev
