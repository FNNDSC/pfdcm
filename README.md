# pfdcm

An Open-source REST API to communicate with any number of PACS instances concurrently

## Abstract

`pfdcm` provides a REST-API aware service that acts as an intermediary between a client and a Radiology Medical Image Picture Archiving and Communication System (PACS). PACS is a largely pre-21st century attempt at digitizing medical imaging and uses paradigms and approaches that seem outdated by today's networking standards. While various PACS vendors have tried in some shape or form to adapt to newer approaches, there exists no standard PACS API-REST interface, leading to a large space of vendor specific and often non-opensource interfaces.

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

Running with hot-reloading

```bash
docker run --rm -it                                                            \
        -p 4005:4005 -p 5555:5555 -p 10502:10502 -p 11113:11113                \
        -v $PWD/pfdcm:/app:ro                                                  \
        local/pfdcm /start-reload.sh
```



## Development

#### Setting up PACS Server

The PACS server used typically for development is Orthanc. We use a slightly customized version of this, called [orthanc-fnndsc](https://github.com/FNNDSC/orthanc-fnndsc). Clone this repository locally and checkout to the `persistent-db` branch.

```bash
git clone https://github.com/FNNDSC/orthanc-fnndsc
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

- Edit the IP address in this key (192.168.1.189 in this example), to your local machine's IP address. You can either find this by using the `ip` command or set this to 127.0.0.1 (loopback IP).

- Now run orthanc with

  ```bash
  ./make.sh -i
  ```

To make sure Orthanc started successfully, open `http://localhost:8042` in a browser and you should get a Basic Auth prompt. Use username `orthanc` and password `orthanc` which are the defaults. You should now be able to interact with Orthanc and upload files.

#### Running a local PFDCM API

Colorful, <kbd>Ctrl-C</kbd>-able server with live/hot reload. Source code changes do not requre a server restart (although some server components might need to be re-initialized).
Changes are applied automatically when the file is saved to disk.

```bash
docker run --rm -it                                                            \
        -p 4005:4005 -p 5555:5555 -p 10502:10502 -p 11113:11113                \
        -v $PWD/pfdcm:/app:ro                                                  \
        local/pfdcm /start-reload.sh
```

Now you'll need to initialize PFDCM to use it as an API for ChRIS UI. Either follow the instructions in [workflow.sh](./examples/workflow.sh) or use a REST client like [Insomnia](https://insomnia.rest/) (a [request collection file](./examples/Insomnia.yaml) is provided, import this) or PostMan.

- Initialize the xinetd listener. Simply use the default.
- Register a PACS service, orthanc in our case. Make sure that the `serverIP` field matches exactly with the IP address of your machine that you put in `orthanc.json` in a previous step.
- Register a local CUBE and a local Swift. The `"cubeKeyName"` and `"swifteyName"` that you provide here will be used in setting up ChRIS_ui.
- Test by performing a find query.



### API swagger

Full API swagger is available. Once you have started `pfdcm`, simply navigate to the machine hosting the container (usually `localhost`), so http://localhost:4005/docs .

### Examples

Using [httpie](https://httpie.org/)

```bash
http :4005/api/v1/hello/ echoBack==lol
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

Please note that many more options/tweaks etc are available. Feel free to ping the authors for additional info. This page (and wiki) will be updated.

_-30-_
