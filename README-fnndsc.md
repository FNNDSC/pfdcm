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

### Build issues

Sometimes the build has been noticed to fail with 

```bash
WARNING: Retrying (Retry(total=4, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<pip._vendor.urllib3.connection.HTTPSConnection object at 0x7fb28ccc79a0>: Failed to establish a new connection: [Errno -3] Temporary failure in name resolution')': /simple/pip
```

If this is the case, the simplest resolution is to restart `docker` services:

```bash
sudo service docker restart
```

## Deploy

```bash
docker run --name pfdcm  --rm -it -d                                            \
        -p 4005:4005 -p 10402:11113 -p 5555:5555 -p 10502:11113 -p 11113:11113  \
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
```

The prompt will block. Wait a few seconds. On success you'll see a screen full of JSON, typically ending with

```json
{
  {
    { 
        "prior": {
        "status": true,
        "install": {
          "stdout": "",
          "stderr": "",
          "cwd": "/app",
          "cmd": "mv /tmp/dicomlistener /etc/xinetd.d/dicomlistener",
          "returncode": 0
        },
        "prior": {
          "status": true,
          "fileContents": "\n        service dicomlistener\n        {\n            disable             = no\n            socket_type         = stream\n            wait                = no\n            user                = root\n            server              = /usr/local/bin/storescp.sh\n            server_args         = -t /tmp/data -E /usr/local/bin -D /home/dicom -p 11113\n            type                = UNLISTED\n            port                = 10502\n            bind                = 0.0.0.0\n        } ",
          "file": "/tmp/dicomlistener"
        }
      }
    }
  }
}
```
and the prompt will return.

## Test

To check that the service is working properly, run the following query

```bash
./pfdcm.sh -u -Q --query -T csv  -- (cat qr.txt)
```

which will perform a quick PACS Query on the contents of the file `qr.txt` (note that this file is NOT part of this repo and exists solely in the FNNDSC directory; note also the `fish` shell conventions).

_-30-_
