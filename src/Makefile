init:
	pip3 install -r requirements.txt
	touch prod.env
	touch dev.env
	touch local.env
.PHONY: init

# run this with 'make start env=local'
env=remote
export DJANGO_ENV=$(env)
start:
	python3 deployment/prepare_to_deploy.py local 1
	python3 manage.py runserver
.PHONY: start


prepare-prod:
	python3 deployment/prepare_to_deploy.py --prod 0 1
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

prepare-canary:
	python3 deployment/prepare_to_deploy.py --canary 0 1
.PHONY: prepare-canary

CANARY_VERSION=latest
deploy-canary:
	$(eval CANARY_VERSION := $(shell cat api_version_canary.txt))	
	aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 202758212688.dkr.ecr.us-east-2.amazonaws.com
	docker build -t massenergize/api-canary .
	docker tag massenergize/api-canary:latest 202758212688.dkr.ecr.us-east-2.amazonaws.com/massenergize/api-canary:$(CANARY_VERSION)
	docker push 202758212688.dkr.ecr.us-east-2.amazonaws.com/massenergize/api-canary:$(CANARY_VERSION)
	eb deploy --label $(CANARY_VERSION)
.PHONY: deploy-canary

prepare-dev:
	python3 deployment/prepare_to_deploy.py --dev 0 1
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
	python3 deployment/prepare_to_deploy.py --dev
	docker-compose build
	docker-compose push
.PHONY: deploy

.PHONY: migrations
migrations: 
	python3 manage.py makemigrations
	python3 manage.py migrate

# Default: test api routes
package=api
#package = carbon_calculator
# for carbon_calculator testing these default options:
infile = $(package)/tests/allPossibleInputs.txt
outfile = $(package)/tests/allPossibleOutputs.txt
generate_inputs = 0
export TEST_INPUTS=$(infile)
export TEST_OUTPUTS=$(outfile)
export GENERATE_INPUTS=$(generate_inputs)

test:
	if [[ -f "test.sqlite3" ]]; \
	then \
		rm test.sqlite3; \
	fi
	touch test.sqlite3
	DJANGO_ENV=test python3 manage.py migrate
	DJANGO_ENV=test python3 -W ignore manage.py test $(package)
.PHONY: test


celery:
	DJANGO_ENV=local celery -A _main_.celery.app worker -l info
.PHONY: celery 


beat:
	DJANGO_ENV=local celery -A _main_.celery.app beat -l info

celery-remote:
	celery -A _main_.celery.app worker -l info

beat-remote:
	celery -A _main_.celery.app beat -l info
