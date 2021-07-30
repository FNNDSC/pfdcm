# `pfdcm` -- Uniform REST API serivce to various PACS services

## Abstract

`pfdcm` provides a REST-API aware service that acts as an intermediary between a client and a Radiology Medical Image Picture Archiving and Communication System (PACS). PACS is a largely pre-21st century attempt at digitizing medical imaging and uses paradigms and approaches that seem outdated by today's networking standards. While various PACS vendors have tried in some shape or form to adapt to newer approaches, there exists no standard PACS API-REST interface, leading to a large space of vendor specific and often non-opensource interfaces.

`pfdcm` is a completely opensource REST-API-to-PACS system. It is designed to provide a single entry point from which to access various PACS systems. Since `pfdcm` uses raw/native PACS type tools, it is compatible with the vast majority of existing PACS systems and frees an end client from mastering the complex and arcane communications dance that typically defines a PACS interaction.

While `pfdcm` is also designed to be a member service in the `ChRIS` / `CUBE` ecosystem, `pfdcm` is fully functional without `CUBE` and can be used as a REST-API service to do generic PACS Query/Retrieve operations. In other words, you don't have to use/have a `ChRIS` instance to use `pfdcm`; nonetheless the full experience is improved when used within a `ChRIS` ecosystem.

At a minimum (without `ChRIS`), `pfdcm` cycle allows for a client to interace with a PACS and request image files. These image files are contained within the `pfdcm` container filesystem; thus a suitable volume mapping can easily expose these retrieved files to a host system. In this mode, `pfdcm` allows a client entity to:

* `Query` a PACS service
* Based on the `Query`, ask the PACS to transmit various data files, i.e. do a `Retrieve`.
* Check on the status of transmission

After the `Retrieve` files should reside in the `pfdcm` container. From here, a client can additionally:

* Push received files to `CUBE` swift storage
* Once pushed, register files to `CUBE`
* Use the `CUBE` API to further interact with image files.

This provides the full experience -- allowing a client to, using only REST-API calls, `Query`, `Retrieve` and ultimately also to download image files.

Note however that this full experience does imply using two separate REST-API services:

* the `pfdcm` API to `Query`/`Retrieve`/`Push-to-swift`/`Register-to-CUBE`
* the `CUBE` API to download an image file

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