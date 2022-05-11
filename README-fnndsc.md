# `pfdcm` (FNNDSC notes)

[![Build](https://github.com/FNNDSC/pfdcm/actions/workflows/build.yml/badge.svg)](https://github.com/FNNDSC/pfdcm/actions/workflows/build.yml)

*Notes relevant to starting/using the `pfdcm` service at the FNNDSC.*

## Abstract

This document provides some quick and simple notes on starting the `pfdcm` service at the Fetal Neonatal and Development Science Center.

## Preliminaries

`pfdcm` is deployed on host `titan` as the `chris-local` user. To start/reset a deployment, log in to `titan` with appropriate password (consult the `dev` team if you need this):

```bash
# This only works from within the FNNDSC/BCH local network
ssh chris-local@titan
```

Once logged in, simply type `v` to switch to a properly configured `fish` shell session (some trivia: `v` denotes the word _vis_ which is `fish` in Dutch/Afrikaans).

Now, change to the `pfdcm` source repo and pull any latest changes

```bash
cd ~/src/pfdcm
git pull
```

## Build

Build the latest docker image

```bash
# Set some vars
set UID (id -u)
export PROXY="http://10.41.13.4:3128"

# Here we build an image called local/pfdcm
# Using --no-cache is a good idea to force the image to build all from scratch
docker build --no-cache --build-arg http_proxy=$PROXY --build-arg UID=$UID -t local/pfdcm .
```

## Deploy

```bash
docker run --name pfdcm  --rm -it -d                                            \
        -p 4005:4005 -p 5555:5555 -p 10502:10502 -p 11113:11113                 \
        -v /home/dicom:/home/dicom                                              \
        -v /neuro/users/chris/PACS:/neuro/users/chris/PACS                      \
        local/pfdcm /start-reload.sh
```

## Startup

```bash
# Assuming you are currently here
# titan:/home/chris-local/src/pfdcm
cd pfdcm
./pfdcm.sh -u -i --

# Wait a few seconds. On susc
```

## Test

To check that the service is working properly, run the following query

```bash
./pfdcm.sh -u -Q --query -T csv  -- (cat qr.txt)
```

_-30-_
