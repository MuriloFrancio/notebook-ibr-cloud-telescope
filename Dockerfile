FROM jupyter/scipy-notebook:latest

USER root

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    tshark \
    tcpdump \
    p7zip-full \
    iproute2 \
    curl \
    iputils-ping \
    net-tools \
    dnsutils \
    libcap2-bin \
    && setcap cap_net_raw,cap_net_admin=eip /usr/bin/tcpdump \
    && rm -rf /var/lib/apt/lists/*

USER jovyan

WORKDIR /home/jovyan/ibr-notebook

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY --chown=jovyan:users notebooks/ /home/jovyan/ibr-notebook/notebooks/
COPY --chown=jovyan:users scripts/ /home/jovyan/ibr-notebook/scripts/
COPY --chown=jovyan:users data/ /home/jovyan/ibr-notebook/data/

CMD ["start-notebook.py", "--ServerApp.root_dir=/home/jovyan/ibr-notebook", "--ServerApp.token=", "--ServerApp.password="]