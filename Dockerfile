#
# Dockerfile for pfdcm.
#
# Build with
#
#   docker build -t <name> .
#
# For example if building a local version, you could do:
#
#   docker build --build-arg UID=$UID -t local/pfdcm .
#
# In the case of a proxy (located at say 10.41.13.4:3128), do:
#
#    export PROXY="http://10.41.13.4:3128"
#    docker build --build-arg http_proxy=${PROXY} --build-arg UID=$UID -t local/pfdcm .
#
# To run an interactive shell inside this container, do:
#
#   docker run -ti --entrypoint /bin/bash local/pfdcm
#
# To pass an env var HOST_IP to the container, do:
#
#   docker run -ti -e HOST_IP=$(ip route | grep -v docker | awk '{if(NF==11) print $9}') --entrypoint /bin/bash local/pfdcm
#
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim

LABEL DEVELOPMENT="                                     \
    docker run --rm -it -p 4005:4005                    \
    -v $PWD/pfdcm:/app:ro  local/pfdcm /start-reload.sh \
"

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && rm -v /tmp/requirements.txt

COPY ./pfdcm /app

RUN apt update              && \
    apt -y install xinetd   && \
    apt -y install dcmtk

ENV PORT=4005
EXPOSE ${PORT} 10402
