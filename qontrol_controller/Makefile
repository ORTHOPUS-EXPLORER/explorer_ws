## Allow SSH or HTTPS
QONTROL_CONTROLLER_REPOSITORY_USE_SSH ?= 1
## Only used when using HTTPS
QONTROL_CONTROLLER_REPOSITORY_HTTPS_USERNAME ?= $(INRIA_REPOSITORY_HTTPS_USERNAME)
QONTROL_CONTROLLER_REPOSITORY_HTTPS_TOKEN ?= $(INRIA_REPOSITORY_HTTPS_TOKEN)

PROJECT_URL=auctus-team/people/estebancosserat/qontrol_controller.git
QONTROL_CONTROLLER_TARGET_BRANCH := explorer_mode_0_fixed

INSTALL_USER ?= `whoami`

## SSH
ifeq ($(QONTROL_CONTROLLER_REPOSITORY_USE_SSH),1)
 	REPOSITORY_BASE_SCHEME = git@gitlab.inria.fr:
## HTTPS
else
	ifeq ($(QONTROL_CONTROLLER_REPOSITORY_HTTPS_USERNAME),)
    	$(error HTTPS scheme is used but QONTROL_CONTROLLER_REPOSITORY_HTTPS_USERNAME is not defined, exiting)
	endif
	ifeq ($(QONTROL_CONTROLLER_REPOSITORY_HTTPS_TOKEN),)
    	$(error HTTPS scheme is used but QONTROL_CONTROLLER_REPOSITORY_HTTPS_TOKEN is not defined, exiting)
	endif
	REPOSITORY_BASE_SCHEME = https://$(QONTROL_CONTROLLER_REPOSITORY_HTTPS_USERNAME):$(QONTROL_CONTROLLER_REPOSITORY_HTTPS_TOKEN)@gitlab.inria.fr/
endif
REPOSITORY_URL=$(REPOSITORY_BASE_SCHEME)$(PROJECT_URL)

## Helper echo colour vars
COLOUR_GREEN := \033[0;32m
COLOUR_RED := \033[0;31m
COLOUR_END := \033[0m

## Pinocchio related install files
PINOCCHIO_ASC_FILE := /etc/apt/keyrings/robotpkg.asc
PINOCCHIO_LIST_FILE := /etc/apt/sources.list.d/robotpkg.list
# Define a hidden stamp file in your workspace
PINOCCHIO_STAMP_FILE := .pinocchio_installed

qontrol_controller/.git:
	git clone --recurse-submodules -b ${QONTROL_CONTROLLER_TARGET_BRANCH} ${REPOSITORY_URL}

init: qontrol_controller/.git

## Pinocchio: Create keyrings ASC file
$(PINOCCHIO_ASC_FILE):
	mkdir -p /etc/apt/keyrings; \
 	curl http://robotpkg.openrobots.org/packages/debian/robotpkg.asc | tee $@; 

## Pinocchio: Create apt list file
$(PINOCCHIO_LIST_FILE): $(PINOCCHIO_ASC_FILE)
	echo "deb [arch=amd64 signed-by=$(PINOCCHIO_ASC_FILE)] http://robotpkg.openrobots.org/packages/debian/pub `lsb_release -cs` robotpkg" | tee $(PINOCCHIO_LIST_FILE); \

pinocchio_env_var:
	@getent passwd $(INSTALL_USER) > /dev/null 2>&1 || (echo "User '$(INSTALL_USER)' doesn't exists." && false)
	@INSTALL_USER_HOME=$$(getent passwd $(INSTALL_USER) | cut -d: -f6); \
## Export vars needed to make use of installed libs \
	grep -q "PATH=/opt/openrobots/bin" $$INSTALL_USER_HOME/.bashrc || echo 'export PATH=/opt/openrobots/bin:$$PATH' >> $$INSTALL_USER_HOME/.bashrc; \
	grep -q "PKG_CONFIG_PATH=/opt/openrobots/lib/pkgconfig:" $$INSTALL_USER_HOME/.bashrc || echo 'export PKG_CONFIG_PATH=/opt/openrobots/lib/pkgconfig:$$PKG_CONFIG_PATH' >> $$INSTALL_USER_HOME/.bashrc; \
	grep -q "LD_LIBRARY_PATH=/opt/openrobots/lib" $$INSTALL_USER_HOME/.bashrc || echo 'export LD_LIBRARY_PATH=/opt/openrobots/lib:$$LD_LIBRARY_PATH' >> $$INSTALL_USER_HOME/.bashrc; \
## Adapt desired python version if needed \
	grep -q "PYTHONPATH=/opt/openrobots/lib/python3.10/site-packages:" $$INSTALL_USER_HOME/.bashrc || echo 'export PYTHONPATH=/opt/openrobots/lib/python3.10/site-packages:$$PYTHONPATH' >> $$INSTALL_USER_HOME/.bashrc; \
	grep -q "CMAKE_PREFIX_PATH=/opt/openrobots:" $$INSTALL_USER_HOME/.bashrc || echo 'export CMAKE_PREFIX_PATH=/opt/openrobots:$$CMAKE_PREFIX_PATH' >> $$INSTALL_USER_HOME/.bashrc; \

## Pinocchio: install apt package + export env vars
$(PINOCCHIO_STAMP_FILE): $(PINOCCHIO_LIST_FILE)
	$(MAKE) pinocchio_env_var
	apt update && apt install -qy robotpkg-py3*-pinocchio
	@touch $@

install_pinocchio: $(PINOCCHIO_STAMP_FILE)

install: install_pinocchio

.PHONY: install pinocchio_env_var