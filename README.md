# `pfdcm`

*an Open-source service providing a REST API to communicate with any number of medical image databases (PACS) instances concurrently*

## Abstract

`pfdcm` provides a REST-API aware service that acts as an intermediary between some client and a Radiology Medical Image Picture Archiving and Communication System (PACS). The client is typically another software agent, or `curl` type command line calls to the API directly.

`pfdcm` is deployed as a docker container most often built from this source repo (and also available [here](https://hub.docker.com/r/fnndsc/pfdcm)). Once (configured and) initialized, `pfdcm` can simplify the pulling of image data from a PACS to the local filesystem. In the case where `pfdcm` is deployed as part of a [ChRIS](https://github.com/FNNDSC/ChRIS_ultron_backEnd) system, `pfdcm` can also *push* images to ChRIS storage and also *register* images to the ChRIS internal database. Furthermore, the [ChRIS UI](https://github.com/FNNDSC/ChRIS_ui) uses `pfdcm` to provide image Query and Retrieve to a PACS.

This repository provides a shell-based client [`pfdcm.sh`](https://github.com/FNNDSC/pfdcm/blob/master/pfdcm/pfdcm.sh) as reference and working exemplar as well as more detailed Jupyter-style shell [`workflow.sh`](https://github.com/FNNDSC/pfdcm/blob/master/pfdcm/workflow.sh).

## TL;DR

If you want to simply get up and running as fast as possible, read this section. Note the *Build* and *Configure* sections only need to be consulted once, thereafter it should be sufficient to only *Run* the service each time a deployment is needed.

### Build

```bash
docker build --build-arg UID=$UID -t local/pfdcm .
```

(make sure that the `UID` environment variable is in fact set)

### Configure

If this is the very first time you are trying to deploy `pfdcm`, you need to configure a `defaults.json` file and create two serivces files, `cube.json` (for logging into ChRIS to *register* files) and `swift.json` (for accessing the swift storage to *push* images).

**NB: Take care to assure that the `cube.json` and `swift.json` files have no credentialing errors! Issues with login to CUBE or swift storage can result in hard to identify errors, especially in the ChRIS UI.**

The simplest way to create the `defaults.json` file is to use the helper script [`pfdcm.sh`](https://github.com/FNNDSC/pfdcm/blob/master/pfdcm/pfdcm.sh) and run, for example:

```bash
    pfdcm.sh    --saveToJSON defaults.json                                     \
                --URL http://ip.of.pfdm.host:4005                              \
                --serviceRoot /home/dicom                                      \
                --swiftKeyName local                                           \
                    --swiftIP ip.of.swift.storage                              \
                    --swiftPort 8080                                           \
                    --swiftLogin chris:chris1234                               \
                --PACS PACSDCM                                                 \
                    --aet CHRISV3                                              \
                    --aetl PACSDCM                                             \
                    --aec PACSDCM                                              \
                    --serverIP ip.of.pacs.server                               \
                    --serverPort 104                                           \
                --cubeKeyName local                                            \
                    --cubeURL http://ip.of.cube.backend:8000/api/v1/           \
                    --cubeUserName chris                                       \
                    --cubePACSservice PACSDCM                                  \
                    --cubeUserPassword chris1234 --
```

Obviously setting appropriate values where needed. Once this file has been created, the two service files can be generated with:

```bash
pfdcm.sh -u --swiftSetupDo --
pfdcm.sh -u --cubeSetupDo --
```

which will save the service files in their default location of

```bash
/home/dicom/services
```

### Run

Assuming a completed configuration, start the `pfdcm` service with

```bash
docker run --name pfdcm  --rm -it -d                                            \
        -p 4005:4005 -p 10402:11113 -p 5555:5555 -p 10502:10502 -p 11113:11113 	\
        -v /home/dicom:/home/dicom                                             	\
        local/pfdcm /start-reload.sh
```

Once the container is successfully launched, initialize it with

```bash
pfdcm.sh -u -i --
```

Congratulations! `pfdcm` should be ready for use!

## Detailed discussion

PACS is a largely pre-21st century attempt at digitizing medical imaging and uses paradigms and approaches that seem outdated by today's networking standards. While various PACS vendors have tried in some shape or form to adapt to newer approaches, there exists no standard PACS API-REST interface, leading to a large space of vendor specific and often non-opensource interfaces.

`pfdcm` is a completely opensource REST-API-to-PACS system. It is designed to provide a single entry point from which to access various PACS systems. Since `pfdcm` uses raw/native PACS type tools, it is compatible with the vast majority of existing PACS systems and frees an end client from mastering the complex and arcane communications dance that typically defines a PACS interaction.

While `pfdcm` is also designed to be a member service in the `ChRIS` / `CUBE` ecosystem, `pfdcm` is fully functional without `CUBE` and can be used as a REST-API service to do generic PACS Query/Retrieve operations. In other words, you don't have to use/have a `ChRIS` instance to use `pfdcm`; nonetheless the full experience is improved when used within a `ChRIS` ecosystem.

At a minimum (without `ChRIS`), the `pfdcm` cycle allows for a client to interace with a PACS and request image files. These image files are contained within the `pfdcm` container filesystem; thus a suitable volume mapping can easily expose these retrieved files to a host system. In this mode, `pfdcm` allows a client entity to:

* `Query` a PACS service
* Based on the `Query`, ask the PACS to transmit various data files, i.e. do a `Retrieve`.
* Check on the status of transmission

After the `Retrieve`, files should reside in the `pfdcm` container. From here, a client can additionally:

* Push received files to `CUBE` swift storage
* Once pushed, register files to `CUBE`
* Use the `CUBE` API to further interact with image files.

When used as part of a `CUBE` deployment, `pfdcm` allows a client to, using only REST-API calls, perform a `Query`, `Retrieve` and ultimately also be able to download image files.

Note however that this full experience does imply using two separate REST-API services:

* the `pfdcm` API to `Query`/`Retrieve`/`Push-to-swift`/`Register-to-CUBE`
* the `CUBE` API to download an image file

### Setting up PACS Server

While setting up a PACS is largely out-of-scope of this document, you can deploy the most excellent open source [Orthanc](https://www.orthanc-server.com) largely developed by Sébastien Jodogne. We recommend a lightly customized version of this, [orthanc-fnndsc](https://github.com/FNNDSC/orthanc-fnndsc):

```bash
git clone https://github.com/FNNDSC/orthanc-fnndsc
cd orthanc-fnndsc
git checkout persistent-db
```

In this directory, find the `orthanc.json` file and make the following edits

- Find the `"DicomModalities"` block in the JSON file, and find the `"CHRISLOCAL"` key.

  ```json
  // ...
  "DicomModalities": {
    // ...
    "CHRISLOCAL" : ["CHRISLOCAL", "192.168.1.189", 11113 ],
  }
  ```

- Edit the IP address in this key (192.168.1.189 in this example), to reflect your local machine's IP address. **Use the actual IP and not `localhost` nor `127.0.0.1`**.
- Now run orthanc with

  ```bash
  ./make.sh -i
  ```

To make sure Orthanc started successfully, open `http://localhost:8042` in a browser and you should get a Basic Auth prompt. Use username `orthanc` and password `orthanc` which are the defaults. You should now be able to interact with Orthanc and upload files.

### API swagger

Full API swagger is available. Once you have started `pfdcm`, simply navigate to the machine hosting the container (usually `localhost`), so [http://localhost:4005/docs](http://localhost:4005/docs) .

### Examples

Using [httpie](https://httpie.org/), let's ask `pfdcm` about itself


```bash
http :4005/api/v1/about/
```

and say `hello` with some info about the system on which `pfdcm` is running:

```bash
http :4005/api/v1/hello/ echoBack=="Hello, World!"
```

For full exemplar documented examples, see `pfdcm/workflow.sh` in this repository as well as `HOWTORUN`. Also consult the `pfdcm/pfdcm.sh` script for more details.

#### Quick-n-dirty CLI example

Once you have started the container, the `pfdcm.sh` script is probably the easiest way to interact with the service. First, assuming you have setup defaults as described in the `HOWTORUN`, you can query on a DICOM `PatientID`:

```bash
pfdcm.sh -u --query -- "PatientID:2233445"
```

In general, you can use any reasonable DICOM tag to drive the query. For more fine tuned searches, you can do

```bash
pfdcm.sh -u --query -- "PatientID:2233445,StudyDate:20210901"
```

to limit the query to, in this case, a specific study date. Once you have determined an image set of interest, you can request a `retrieve`

```bash
pfdcm.sh -u --retrieve -- "PatientID:2233445,StudyDate:20210901"
```

which will handle incoming file transmission from the PACS and store/pack the files on the local (container) filesystem. Note that the `retrieve` is an asynchronous request and will return to the client immediately. To determine the status of the operation,

```bash
pfdcm.sh -u --status -- "PatientID:2233445,StudyDate:20210901"
```

Once all the files have been retrieved, the files can be pushed to CUBE swift storage (assuming an available CUBE instance):

```bash
pfdcm.sh -u --push -- "PatientID:2233445,StudyDate:20210901"
```

after a successful push operation (check on progress using `status`), files in swift storage can be registered to the CUBE internal database with

```bash
pfdcm.sh -u --register -- "PatientID:2233445,StudyDate:20210901"
```

Note that the `-u` means "use configured parameters" which are defined initially in the `defaults.json` file and written to the `pfdcm`  database using appropriate setup directives (see the `workflow.sh`).

Please note that many more options/tweaks etc are available. Feel free to ping the authors for additional info.

_-30-_
