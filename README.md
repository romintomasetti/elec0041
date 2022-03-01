# elec0041

Repository for the course ELEC0041 (ULiege - https://people.montefiore.uliege.be/geuzaine/ELEC0041/).

This repository will contain all the work done for the homework assignments during this course.

## Starting a GUI-based application from a Docker container

Tested with host : Ubuntu Jammy (1st March 2022)

1. You need `--net=host` and `--env="DISPLAY"`, see also how it was done in [devcontainer](.devcontainer/devcontainer.json)
2. You need to allow Docker to use your host for display with `xhost +local:docker`

Resources:
* https://forums.docker.com/t/start-a-gui-application-as-root-in-a-ubuntu-container/17069
* https://stackoverflow.com/questions/43015536/xhost-command-for-docker-gui-apps-eclipse
