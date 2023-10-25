.PHONY: tests

DEPLOY_REQ_FILE = ansible-python-requirements.txt
DEPLOY_REQ_SHA1 = $(shell sha1sum $(DEPLOY_REQ_FILE) | cut -f1 -d " " | sed -e 's/^\(.\{5\}\).*/\1/')
VENV_NAME       = .ansible-venv-$(DEPLOY_REQ_SHA1)

ANSIBLE_COLLECTION_VERSION_FILE="version.txt"
ANSIBLE_COLLECTION_VERSION=`cat galaxy.yml | grep -oP 'version: \K(\d.\d.\d)$$'`

BUILD_PATH="build"

DOCKER_BUILD_IMAGE="python:3.11.6-alpine3.18"
DOCKER_CMD=docker run --rm -v `pwd`:/data --workdir /data ${DOCKER_BUILD_IMAGE} sh -c

build: set-env
	${VENV_NAME}/bin/ansible-galaxy collection build --output-path ${BUILD_PATH}

clean:
	@rm -rf ${BUILD_PATH}

docker-build:
	@${DOCKER_CMD} "python -m pip install -r ${DEPLOY_REQ_FILE} && ansible-galaxy collection build --force --output-path ${BUILD_PATH} && chown -R `id -u`:`id -g` ${BUILD_PATH}"

docker-test:
	@${DOCKER_CMD} "python -m pip install -r ${DEPLOY_REQ_FILE} && PYTHONPATH="${PYTHONPATH}:${pwd}" pytest"

get-version:
	@echo ${ANSIBLE_COLLECTION_VERSION}

release-version:
	@./scripts/create_release.sh

set-version:
	@if [ -z "${NEW_VERSION}" ]; then \
		echo "Usage: make set-version NEW_VERSION=X.Y.Z" && \
		exit 1; \
	fi
	@sed -i "s/$(ANSIBLE_COLLECTION_VERSION)/${NEW_VERSION}/" galaxy.yml
	@echo ${ANSIBLE_COLLECTION_VERSION}

set-env: ## Generate ansible virtual env and vault file
	@if [ ! -d "${VENV_NAME}" ]; then \
		python3 -m venv ${VENV_NAME} && \
		${VENV_NAME}/bin/python3 -m pip install --upgrade pip setuptools && \
		${VENV_NAME}/bin/python3 -m pip install -r ${DEPLOY_REQ_FILE} ; \
	fi

tests: set-env
	@PYTHONPATH="${PYTHONPATH}:${pwd}" ${VENV_NAME}/bin/pytest
