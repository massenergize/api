init:
	pip3 install -r requirements.txt
	mkdir .massenergize
.PHONY: init

start:
	@echo "Setting environment variables ..."
	python3 _main_/utils/startup/prepare.py
	@echo "Initializing server now ..."
	python3 manage.py runserver
.PHONY: start

startd:
	@echo "Setting environment variables ..."
	python3 _main_/utils/startup/prepare.py
	sudo docker-compose down
	sudo docker image prune -f
	sudo docker builder prune -f
	sudo docker-compose build
	@echo "Running in docker mode!!!"
	sudo docker-compose up
.PHONY: startd

local: 
	DJANGO_ENV="local" make start
.PHONY: local

dev: 
	DJANGO_ENV="dev" make start
.PHONY: dev

canary: 
	DJANGO_ENV="canary" make start
.PHONY: canary

prod: 
	DJANGO_ENV="prod" make start
.PHONY: prod

local-docker: 
	DJANGO_ENV="local" make startd
.PHONY: local-docker

dev-docker: 
	DJANGO_ENV="dev" make startd
.PHONY: dev-docker

canary-docker: 
	DJANGO_ENV="canary" make startd
.PHONY: canary-docker

prod-docker: 
	DJANGO_ENV="prod" make startd
.PHONY: prod-docker

prepare-prod:
	python3 deployment/prepare_to_deploy.py --prod 0 1
.PHONY: prepare-prod

VERSION=latest
build-and-push-prod:
	$(eval VERSION := $(shell cat api_version_prod.txt))	
	aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 202758212688.dkr.ecr.us-east-2.amazonaws.com
	docker build -t massenergize/api .
	docker tag massenergize/api:latest 202758212688.dkr.ecr.us-east-2.amazonaws.com/massenergize/api:$(VERSION)
	docker push 202758212688.dkr.ecr.us-east-2.amazonaws.com/massenergize/api:$(VERSION)
	eb deploy --label $(VERSION)

	git tag prod@$(VERSION)
	git push origin prod@$(VERSION)
.PHONY: build-and-push-prod

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
	 DJANGO_ENV=test python3 -m coverage run --source='.' manage.py test $(package)
	 python3 -m coverage report
.PHONY: test

celery:
	DJANGO_ENV=local celery -A _main_.celery.app worker --loglevel=info --pool=solo -B
.PHONY: celery 

beat:
	celery -A _main_.celery.app beat -l info

celery-remote:
	celery -A _main_.celery.app worker -l info

full-celery-local: 
	make -j 2 start celery
.PHONY: full-celery-local

beat-remote:
	celery -A _main_.celery.app beat -l info


#-------------- NEW  MIGRATE ----------------
migrate-dev:
	DJANGO_ENV=dev python manage.py migrate
.PHONY: migrate-dev

migrate-prod:
	DJANGO_ENV=prod python manage.py migrate
.PHONY: migrate-prod

migrate-canary:
	DJANGO_ENV=canary python manage.py migrate
.PHONY: migrate-canary

migrate-local:
	DJANGO_ENV=local python manage.py migrate
.PHONY: migrate-local

