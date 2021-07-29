# `pfdcm` intermediary ChRIS-to-PACS service

## Abstract

`pfdcm` provides a REST-API aware service that acts as an intermediary between a `CUBE` instance and some medical image PACS repository. While designed to function in the `ChRIS` / CUBE ecosystem, `pfdcm` is fully functional without `CUBE` and can be used as a REST-API service to do generic PACS Query/Retrieve operations.

At a minimum, `pfdcm` cycle allows for a client to:

* Query a PACS service
* Based on the query, ask the PACS to transmit various data files
* Check on the status of transmission

Files received from the PACS are stored in the `pfdcm` container. From here, a client can additionally:

* Push received files to `CUBE` swift storage
* Once pushed, register files to `CUBE`


## Usage

Simplest build:

```bash
docker build -t local/pfdcm .
```

### Run

Production server with worker auto-tuning

```bash
docker run --rm -it                                                            \
        -p 4005:4005 -p 5555:5555 -p 10502:10502 -p 11113:11113                \
        local/pfdcm /start-reload.sh
```

### Development

Colorful, <kbd>Ctrl-C</kbd>-able server with live/hot reload. Source code changes do not requre a server restart (although some server components might need to be re-initialized).
Changes are applied automatically when the file is saved to disk.

```bash
docker run --rm -it                                                            \
        -p 4005:4005 -p 5555:5555 -p 10502:10502 -p 11113:11113                \
        -v $PWD/pfdcm:/app:ro                                                  \
        local/pfdcm /start-reload.sh
```

See http://localhost:4005/docs

### Examples

Using [httpie](https://httpie.org/)

```bash
http :4005/api/v1/hello/ echoBack==lol
```

For full exemplar documented examples, see `workflow.sh` in this repository.

_-30-_