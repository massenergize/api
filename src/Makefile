essential-folders:
	@if [ ! -d ".massenergize" ]; then mkdir .massenergize; fi
	@if [ ! -d ".massenergize/creds" ]; then mkdir .massenergize/creds; fi
.PHONY: essential-folders

init: essential-folders
	pip3 install -r requirements.txt
.PHONY: init

start: essential-folders
	@echo "Setting environment variables ..."
	python3 _main_/utils/startup/prepare.py
	@echo "Initializing server now ..."
	python3 manage.py runserver
.PHONY: start

startd: essential-folders
	@echo "Setting environment variables ..."
	DOCKER_MODE=true python3 _main_/utils/startup/prepare.py
	sudo docker-compose down --remove-orphans
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

local-docker: install_redis_and_run
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

install_redis_and_restart:
	@if ! command -v redis-server > /dev/null; then \
	    echo "Redis is not installed. Installing..."; \
	    sudo apt-get update && sudo apt-get install redis-server -y; \
	fi
	@echo "Stopping Redis if it's running..."
	-redis-cli shutdown > /dev/null 2>&1 || true
	@echo "Starting Redis..."
	redis-server --daemonize yes --port 6379
.PHONY: install_redis_and_run


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
migrate:
	@echo "Setting environment variables ..."
	python3 _main_/utils/startup/prepare.py
	python3 manage.py makemigrations
	python3 manage.py showmigrations
	python3 _main_/utils/startup/migration_prompt.py
	python3 manage.py migrate
.PHONY: migrate

migrate-dev:
	DJANGO_ENV=dev make migrate
.PHONY: migrate-dev

migrate-prod:
	DJANGO_ENV=prod make migrate
.PHONY: migrate-prod

migrate-canary:
	DJANGO_ENV=canary make migrate
.PHONY: migrate-canary

migrate-local:
	DJANGO_ENV=local make migrate
.PHONY: migrate-local

back-fill-menu-local:
	DJANGO_ENV=local python manage.py back-fill-menu
.PHONY: back-fill-menu-local

back-fill-menu-dev:
	DJANGO_ENV=dev python manage.py back-fill-menu
.PHONY: back-fill-menu-dev

back-fill-menu-prod:
	DJANGO_ENV=prod python manage.py back-fill-menu
.PHONY: back-fill-menu-prod

back-fill-menu-canary:
	DJANGO_ENV=canary python manage.py back-fill-menu
.PHONY: back-fill-menu-canary

release:
	@echo "Running release script..."
	@python3 _main_/utils/release_software.py
	@VERSION=$$(cat version.txt) && \
	rm version.txt && \
	echo "New version is $$VERSION" && \
	git add release_info.json && \
	git commit -m "Release version $$VERSION" && \
	git tag -a "v$$VERSION" -m "Release version $$VERSION" && \
	git push origin main && \
	git push origin --tags
.PHONY: release

tk:
	 if [[ -f "test.sqlite3" ]]; \
	 then \
	  rm test.sqlite3; \
	 fi
	 touch test.sqlite3
	 DJANGO_ENV=test python3 manage.py migrate
	 DJANGO_ENV=test python manage.py test api.tests.integration.test_campaigns.CampaignsIntegrationTestCase

	# coverage report --precision=2
.PHONY: tk


update-recurring-schedule-local:
	DJANGO_ENV=local python manage.py create-initial-recurring-schedule

update-recurring-schedule-dev:
	DJANGO_ENV=dev python manage.py create-initial-recurring-schedule

update-recurring-schedule-canary:
	DJANGO_ENV=canary python manage.py create-initial-recurring-schedule

update-recurring-schedule-prod:
	DJANGO_ENV=prod python manage.py create-initial-recurring-schedule


