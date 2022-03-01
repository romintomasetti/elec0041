FROM ubuntu:focal

ARG GMSH_VERSION=4.9.5
ARG GETDP_VERSION=3.4.0

COPY requirements.system.gmsh.and.getdp.txt requirements.system.gmsh.and.getdp.txt
COPY requirements.system.working.txt        requirements.system.working.txt
COPY requirements.python.working.txt        requirements.python.working.txt

RUN    apt update \
    # Install system requirements
    && apt --yes --no-install-recommends install $(grep -vE "^\s*#" requirements.system.gmsh.and.getdp.txt  | tr "\n" " ") \
    && apt --yes --no-install-recommends install $(grep -vE "^\s*#" requirements.system.working.txt         | tr "\n" " ") \
    # Update alternative for python
    && update-alternatives --install /usr/bin/python python /usr/bin/python3 10 \
    # Install Python requirements
    && python -m pip install -r requirements.python.working.txt \
    # Fetch GMSH and GETDP installers and extract them
    && wget https://gmsh.info/bin/Linux/gmsh-${GMSH_VERSION}-Linux64.tgz \
    && wget https://getdp.info/bin/Linux/getdp-${GETDP_VERSION}-Linux64c.tgz \
    && tar xvf gmsh-${GMSH_VERSION}-Linux64.tgz \
    && tar xvf getdp-${GETDP_VERSION}-Linux64c.tgz \
    # Remove archives
    && rm gmsh-${GMSH_VERSION}-Linux64.tgz \
    && rm getdp-${GETDP_VERSION}-Linux64c.tgz \
    # Lighter image (https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
    && rm -rf /var/lib/apt/lists/* 

# Setup environment
ENV PATH=${PWD}/getdp-${GETDP_VERSION}-Linux64/bin:${PWD}/gmsh-${GMSH_VERSION}-Linux64/bin:${PATH}

LABEL maintainer="Romin Tomasetti"
