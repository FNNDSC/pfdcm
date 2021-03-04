# `pfdcm` intermediary ChRIS-2-PACS service

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
docker run --rm -it -p 4005:4005    \
           -v $PWD/notpfdcm:/app:ro \
           local/pfdcm /start-reload.sh
```

See http://localhost:4005/docs

### Examples

Using [httpie](https://httpie.org/)

```bash
http :4005/api/v1/hello/ echoBack==lol
```

_-30-_