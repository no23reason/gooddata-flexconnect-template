SHELL := /bin/bash

#######################################################################
# Setup of development environment
#######################################################################

.PHONY: init-secrets
init-secrets:
	# if needed, initialize files that are not committed to VCS
	touch .secrets && chmod 600 .secrets

.PHONY: dev
dev: init-secrets
	python3.12 -m venv .venv --upgrade-deps
	source .venv/bin/activate && pip3 install -r requirements.txt -r requirements-dev.txt
	.venv/bin/pre-commit install

.PHONY: prod
prod:
	python3.12 -m venv .venv --upgrade-deps
	source .venv/bin/activate && pip3 install -r requirements.txt

.PHONY: mypy
mypy:
	.venv/bin/mypy --show-error-codes src

.PHONY: fix-format
fix-format:
	.venv/bin/ruff format .
	.venv/bin/ruff check . --fix --fixable I

.PHONY: fix-all
fix-all:
	pre-commit run --all-files


.PHONY: test
test:
	pytest tests

.PHONY: docker
docker:
	docker build -t flexconnect-server:latest -f Dockerfile .

.PHONY: archive
archive:
	tar --exclude __pycache__ \
		-cvpzf flexconnect.tar.gz \
		./config \
		./src \
		./requirements.txt \
		./Makefile \
		./run-server.sh \
		./.python-version
