FROM jupyter/scipy-notebook:latest

USER root

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    tshark \
    tcpdump \
    p7zip-full \
    && rm -rf /var/lib/apt/lists/*

USER jovyan

WORKDIR /home/jovyan/work

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt