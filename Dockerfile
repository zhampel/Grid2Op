# Use an official Python runtime as a parent image
FROM python:3.6-stretch

MAINTAINER Benjamin DONNOT <benjamin.donnot@rte-france.com>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
    apt-get install -y \
    less \
    apt-transport-https \
    git \
    ssh \
    tar \
    gzip \
    ca-certificates

# Retrieve Grid2Op
RUN git clone https://github.com/BDonnot/Grid2Op

# Install Grid2Op
WORKDIR /Grid2Op
# Use the latest release
RUN git pull
RUN git fetch --all --tags
RUN git checkout "tags/v0.6.0" -b "v0.6.0-branch"
# Install Dependencies
RUN pip3 install -U .
RUN pip3 install -e .[optional]
RUN pip3 install -e .[test]
RUN pip3 install -e .[challenge]
WORKDIR /

# Make port 80 available to the world outside this container
EXPOSE 80