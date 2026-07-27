REPOSITORY_URL= "git@gitlab.inria.fr:auctus-team/people/estebancosserat/qontrol_controller.git"
TARGET_BRANCH="explorer_mode_0"

## Helper echo colour vars
COLOUR_GREEN=\033[0;32m
COLOUR_RED=\033[0;31m
COLOUR_END=\033[0m

## Pinocchio related install files
PINOCCHIO_ASC_FILE=/etc/apt/keyrings/robotpkg.asc
PINOCCHIO_LIST_FILE=/etc/apt/sources.list.d/robotpkg.list
# Define a hidden stamp file in your workspace
PINOCCHIO_STAMP_FILE := .pinocchio_installed

qontrol_controller/.git:
	@if git clone --quiet --recurse-submodules -b ${TARGET_BRANCH} ${REPOSITORY_URL}; then \
        echo -e "${COLOUR_GREEN}'qontrol_controller' package has properly been cloned.${COLOUR_END}";\
	else\
		echo -e "${COLOUR_RED}Impossible to clone package with url: '${REPOSITORY_URL}', you may need to ask INRIA team an access to the repository.${COLOUR_END}";\
    fi\

init: qontrol_controller/.git

## Pinocchio: Create keyrings ASC file
$(PINOCCHIO_ASC_FILE):
	mkdir -p /etc/apt/keyrings; \
 	curl http://robotpkg.openrobots.org/packages/debian/robotpkg.asc | tee $@; 

## Pinocchio: Create apt list file
$(PINOCCHIO_LIST_FILE): $(PINOCCHIO_ASC_FILE)
	echo "deb [arch=amd64 signed-by=$(PINOCCHIO_ASC_FILE)] http://robotpkg.openrobots.org/packages/debian/pub `lsb_release -cs` robotpkg" | tee $(PINOCCHIO_LIST_FILE); \

## Pinocchio: install apt package + export env vars
$(PINOCCHIO_STAMP_FILE): $(PINOCCHIO_LIST_FILE)
	apt update; \
	apt install -qy robotpkg-py3*-pinocchio;
## Export vars needed to make use of installed libs
	@echo 'export PATH=/opt/openrobots/bin:$$PATH' >> ~/.bashrc
	@echo 'export PKG_CONFIG_PATH=/opt/openrobots/lib/pkgconfig:$$PKG_CONFIG_PATH' >> ~/.bashrc
	@echo 'export LD_LIBRARY_PATH=/opt/openrobots/lib:$$LD_LIBRARY_PATH' >> ~/.bashrc
## Adapt desired python version if needed
	@echo 'export PYTHONPATH=/opt/openrobots/lib/python3.10/site-packages:$$PYTHONPATH' >> ~/.bashrc
	@echo 'export CMAKE_PREFIX_PATH=/opt/openrobots:$$CMAKE_PREFIX_PATH' >> ~/.bashrc
## Create hidden file to mark pinocchio as 'already installed'
	@touch $@

install_pinocchio: $(PINOCCHIO_STAMP_FILE)

install: install_pinocchio

.PHONY: install