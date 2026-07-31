REPOSITORY_USE_SSH ?= 1

init:
	@$(MAKE) init -C qontrol_controller QONTROL_CONTROLLER_REPOSITORY_USE_SSH:=$(REPOSITORY_USE_SSH)

install:
	apt update
	$(MAKE) install -C qontrol_controller
	rosdep install --from-paths . --ignore-src -y

.PHONY: install clean
clean:
	rm -rf build/ install/