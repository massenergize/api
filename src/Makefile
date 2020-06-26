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

test:	
	package = carbon_calculator
	infile = $(package)/tests/standard_inputs.json
	outfile = $(package)/tests/standard_outputs.json
	export TEST_INPUTS=$(infile)
	export TEST_OUTPUTS=$(outfile)
	python manage.py test $(package)
.PHONY: test