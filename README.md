# `pfdcm` intermediary ChRIS-to-PACS service

## Abstract

`pfdcm` provides a REST-API aware service that acts as an intermediary between a CUBE instance and some medical image PACS repository.

## Usage

```bash
docker build -t local/pfdcm .
```

### Run

Production server with worker auto-tuning

```bash
docker run --rm -p 4005:4005 local/pfdcm
```

### Development

Colorful, <kbd>Ctrl-C</kbd>-able server with live/hot reload.
You do not need to restart the server after changing source code.
Changes are applied automatically when the file is saved to disk.

```bash
docker run --rm -it                                                            \
        -p 4005:4005 -p 5555:5555 -p 10502:10502 -p 11112:11112                \
        -v $PWD/pfdcm:/app:ro                                                  \
        local/pfdcm /start-reload.sh
```

See http://localhost:4005/docs

### Examples

Using [httpie](https://httpie.org/)

```bash
http :4005/api/v1/hello/ echoBack==lol
```

Fire up the internal listener services

```bash
curl -X 'POST' \
  'http://localhost:4005/api/v1/listener/initialize/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "value": "default"
}'
```

_-30-_