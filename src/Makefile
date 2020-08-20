init:
	pip install -r requirements.txt
.PHONY: init

start:
	python deployment/prepare_to_deploy.py dev 1
	python manage.py runserver
.PHONY: start

deploy-prod:
	python deploy/prepare-for-deploy.py --prod
	aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 202758212688.dkr.ecr.us-east-2.amazonaws.com
	docker build -t massenergize/api .
	docker tag massenergize/api:latest 202758212688.dkr.ecr.us-east-2.amazonaws.com/massenergize/api:latest
	docker push 202758212688.dkr.ecr.us-east-2.amazonaws.com/massenergize/api:latest
.PHONY: deploy-prod

deploy-dev:
	python deploy/prepare-for-deploy.py --dev
	aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 202758212688.dkr.ecr.us-east-2.amazonaws.com
	docker build -t massenergize/api-dev .
	docker tag massenergize/api-dev:latest 202758212688.dkr.ecr.us-east-2.amazonaws.com/massenergize/api-dev:latest
	docker push 202758212688.dkr.ecr.us-east-2.amazonaws.com/massenergize/api-dev:latest
.PHONY: deploy-dev

deploy:
	docker-compose build
	docker-compose push
.PHONY: deploy