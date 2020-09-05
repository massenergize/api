init:
	pip install -r requirements.txt
	touch prod.env
	touch dev.env
	touch local.env
.PHONY: init

start:
	python deployment/prepare_to_deploy.py dev 1
	python manage.py runserver
.PHONY: start


prepare-prod:
	python deployment/prepare_to_deploy.py --prod 0 1
.PHONY: prepare-prod

VERSION=latest
deploy-prod:
	$(eval VERSION := $(shell cat api_version_prod.txt))	
	aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 202758212688.dkr.ecr.us-east-2.amazonaws.com
	docker build -t massenergize/api .
	docker tag massenergize/api:latest 202758212688.dkr.ecr.us-east-2.amazonaws.com/massenergize/api:$(VERSION)
	docker push 202758212688.dkr.ecr.us-east-2.amazonaws.com/massenergize/api:$(VERSION)
	eb deploy --label $(VERSION)
.PHONY: deploy-prod


prepare-dev:
	python deployment/prepare_to_deploy.py --dev 0 1
.PHONY: deploy-dev

DEV_VERSION=latest
deploy-dev:
	$(eval DEV_VERSION := $(shell cat api_version_dev.txt))	
	aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 202758212688.dkr.ecr.us-east-2.amazonaws.com
	docker build -t massenergize/api-dev .
	docker tag massenergize/api-dev:latest 202758212688.dkr.ecr.us-east-2.amazonaws.com/massenergize/api-dev:$(DEV_VERSION)
	docker push 202758212688.dkr.ecr.us-east-2.amazonaws.com/massenergize/api-dev:$(DEV_VERSION)
	eb deploy --label $(DEV_VERSION)
.PHONY: deploy-dev

deploy:
	python deployment/prepare_to_deploy.py --dev
	docker-compose build
	docker-compose push
.PHONY: deploy

package = carbon_calculator
infile = $(package)/tests/allPossibleInputs.txt
outfile = $(package)/tests/allPossibleOutputs.txt
generate_inputs = 0
export TEST_INPUTS=$(infile)
export TEST_OUTPUTS=$(outfile)
export GENERATE_INPUTS=$(generate_inputs)

test:	
	python -W ignore manage.py test $(package)
.PHONY: test 