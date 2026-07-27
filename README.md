# Main ROS workspace for ORTHOPUS Explorer robot

Each folder contains a ROS2 package as a plain folder ready to use or just a minimal folder containing CMakeLists.txt / Makefile with a README.md file for install instructions.

## General workflow

```bash
## Retrieves public packages
git submodule update --init --recursive
## Clone restricted packages
make init
## Install current workspace dependencies
make install
```