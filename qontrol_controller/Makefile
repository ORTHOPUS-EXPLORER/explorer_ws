qontrol_controller/.git:
	git submodule update --init --recursive

init: qontrol_controller/.git

install_pinocchio:
	apt update && apt install -qy ros-${ROS_DISTRO}-pinocchio

install: install_pinocchio

.PHONY: install pinocchio_env_var