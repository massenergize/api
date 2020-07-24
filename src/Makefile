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