init:
	$(MAKE) init -C qontrol_controller

install:
	apt update
	$(MAKE) install -C qontrol_controller
	rosdep install --from-paths . --ignore-src

.PHONY: install clean
clean:
	rm -rf build/ install/