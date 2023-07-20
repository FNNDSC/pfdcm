# `pfdcm`

[![Build](https://github.com/FNNDSC/pfdcm/actions/workflows/build.yml/badge.svg)](https://github.com/FNNDSC/pfdcm/actions/workflows/build.yml)

*an Open-source service providing a bridge between a PACS and a ChRIS instance that offers a REST API to communicate with any number of medical image databases (PACS) instances concurrently*

## Abstract

`pfdcm` provides a REST-API aware service that acts as an intermediary between some client, a Picture Archiving and Communication System (PACS), *and* typically a ChRIS instance. The client that consumes this REST-API is usually another software agent, or `curl` type command line calls to the API directly.

`pfdcm` is deployed as a docker container most often built from this source repo (and also available [here](https://hub.docker.com/r/fnndsc/pfdcm)). Once (configured and) initialized, `pfdcm` can greatly simplify the tasks of (bulk) pulling image data from a PACS and saving on local filesystem. In the case where `pfdcm` is instantiated as part of a [ChRIS](https://github.com/FNNDSC/ChRIS_ultron_backEnd) deployment, `pfdcm` can also *push* images to ChRIS storage and also *register* images to the ChRIS internal database. Furthermore, the [ChRIS UI](https://github.com/FNNDSC/ChRIS_ui) uses `pfdcm` to provide a friendly web-based interface to Quering and Retrieving images from a PACS and importing into ChRIS.

This repository provides a shell-based client [`pfdcm.sh`](https://github.com/FNNDSC/pfdcm/blob/master/pfdcm/pfdcm.sh) as reference and working exemplar as well as more detailed Jupyter-style shell [`workflow.sh`](https://github.com/FNNDSC/pfdcm/blob/master/pfdcm/workflow.sh) script.

## TL;DR

If you want to simply get up and running as fast as possible, read this section. Note the *Build* and *Configure* sections only need to be consulted once, thereafter it should be sufficient to only *Run* the service each time a deployment is needed.

### Build

```bash
# Pull repo...
gh repo clone FNNDSC/pfdcm
# Enter the repo...
cd pfdcm
# and build the container
docker build -t local/pfdcm .
```

### Configure

If this is the very first time you are trying to deploy `pfdcm`, you need to configure a `defaults.json` file and create two services files, `swift.json` (for accessing the swift storage to *push* images), and `cube.json` (for logging into ChRIS to *register*  the *pushed* files).

**NB: Take care to assure that the `cube.json` and `swift.json` files have no credentialing errors! Issues with login to CUBE or swift storage can result in hard to identify errors, especially in the ChRIS UI.**

The simplest way to create the `defaults.json` file is to use the helper script [`pfdcm.sh`](https://github.com/FNNDSC/pfdcm/blob/master/pfdcm/pfdcm.sh) that is located in the `pfdcm` subdir of the repo and run, for example:

```bash
cd pfdcm
./pfdcm.sh  --saveToJSON defaults.json                                     \
            --URL http://ip.of.pfdcm.host:4005                             \
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
./pfdcm.sh -u --swiftSetupDo --
./pfdcm.sh -u --cubeSetupDo --
```

which will save the service files in their default location of

```bash
# The default location for all the DICOM related interaction
# is /home/dicom -- if you don't have this directory already
# it's a good idea to create it.
/home/dicom/services/cube.json
/home/dicom/services/swift.json
```

Please check these files very carefully and again make sure that values (in particular login names and passwords) are correct!

### Run

Assuming a completed configuration, start the `pfdcm` service from the root dir of the repo with

```bash
docker run --name pfdcm  --rm -it -d                                            \
        -p 4005:4005 -p 10402:11113 -p 5555:5555 -p 10502:10502 -p 11113:11113  \
        -v /home/dicom:/home/dicom                                              \
        local/pfdcm /start-reload.sh
```

Once the container is successfully launched, initialize it with (note this takes about a second or so) by running (in the `pfdcm` subdirectory of the repo)

```bash
cd pfdcm
./pfdcm.sh -u -i --
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

### Setting Up and Connecting to a PACS Server

While setting up a PACS is largely out-of-scope of this document, you can deploy the most excellent open source [Orthanc](https://www.orthanc-server.com) (developed by Sébastien Jodogne). We recommend a lightly customized version of this, [orthanc-fnndsc](https://github.com/FNNDSC/orthanc-fnndsc) and to use the `persistent-db` branch:

```bash
git clone https://github.com/FNNDSC/orthanc-fnndsc
cd orthanc-fnndsc
git checkout persistent-db
```

In this directory, open the `orthanc.json` file and make the following edits

- Find the `"DicomModalities"` block in the JSON file, and find the `"CHRISLOCAL"` key.

  ```json
  // ...
  "DicomModalities": {
    // ...
    "CHRISLOCAL" : ["CHRISLOCAL", "192.168.1.189", 11113 ],
  }
  ```

- Edit the IP address in this key (`192.168.1.189` in this example), to reflect your local machine's IP address. **We highly recommend to use the actual IP and not `localhost` nor `127.0.0.1`**.

- Now fire up our customized Othanc with

  ```bash
  ./make.sh -i
  ```

To make sure Orthanc started successfully, visit [http://localhost:8042](http://localhost:8042) in a browser and log in with username `orthanc` and password `orthanc`. You should now be able to interact with Orthanc and upload files. Feel free to pull our publically available anonymized [T1 MPRAGE scan of a normal 3 year old brain](https://github.com/FNNDSC/SAG-anon) and upload into your Orthanc.

### "hello, pfdcm"

Using [httpie](https://httpie.org/), let's ask `pfdcm` about itself


```bash
http :4005/api/v1/about/
```

and say `hello` with some info about the system on which `pfdcm` is running:

```bash
http :4005/api/v1/hello/ echoBack=="Hello, World!"
```

For full exemplar documented examples, see `pfdcm/workflow.sh` in this repository as well as `HOWTORUN`. Also consult the `pfdcm/pfdcm.sh` script for more details.

### API swagger

Full API swagger is available. Once you have started `pfdcm`, and assuming that the machine hosting the container is `localhost`, navigate to [http://localhost:4005/docs](http://localhost:4005/docs) .

## CLI example

Once you have started the container, the `pfdcm.sh` script is probably the easiest way to interact with the service. Typically there are four steps/phases in a full cycle, denoted by the following verbs `--query`, `--retrieve`, `--push`, `--register`. The command line for a given interaction largely stays identical, with only the verb above changing, and almost always in the above ordered sequence.

Note that the `--push` and `--register` verbs are only meaningful in the context of pushing and registering to ChRIS. If you only want to pull images to the file system and don't care/need them to also appear in ChRIS, your sequence will be `--query` and `--retrieve` only.

The `--query` operation blocks, meaning that the command line will wait until this completes. All the other verbs are **asynchronous** meaning that the command line will return immediately. **It is very important that you wait until an asynchronous operation is complete before using another verb in the cycle**. To determine the status of an asynchronous operation, use the `--status` verb. This will return a status report where, for each image series, a text result of form:

```bash
[ PACS:116/JSON:116/DCM:116/PUSH:116/REG:116 ] │  GEechoes3_EPI_SMS2_GRAPPA2_Echo_1
```

denotes that (in this example) there were 116 images in the `PACS`, these have been retrieved and cataloged in 116 `JSON` files, packed and saved as 116 `DCM` images, also 116 images have been `PUSH`ed to ChRIS swift storage and 116 images have been `REG`istered by ChRIS, corresponding to each of the verbs in a typical interaction cycle. Obviously you need to wait until the numbers in each cycle match the `PACS` before calling the next cycle.

So, assuming you have setup defaults as described in the `HOWTORUN`, you can query on a DICOM `PatientID` (let's assume additionally that the PACS to interact with has been defined within `pfdcm` and is called `PACSDCM`):

```bash
# Using the setup json file...
./pfdcm.sh -u --query -- "PatientID:2233445"

# Using the PACS details defined within pfdcm...
./pfdcm.sh --pfdcmPACS PACSDCM --query -- "PatientID:2233445"

# If you wanted to use a different PACS...
./pfdcm.sh --pfdcmPACS TeleRIS --query -- "PatientID:2233445"

# or...
./pfdcm.sh --pfdcmPACS orthanc --query -- "PatientID:2233445"

# This all assumes that "PACSDCM", "TeleRIS", and "orthanc" are
# the names (or keys) for services that pfdcm knows about. A list
# of known keys for PACS servers can be found with:
xh http://localhost:4005/api/v1/PACSservice/list/

HTTP/1.1 200 OK
Content-Length: 82
Content-Type: application/json
Date: Thu, 03 Nov 2022 23:41:11 GMT
Server: uvicorn

[
    "default",
    "orthanc",
    "PACSDCM",
    "EO",
    "orthanc-pangea",
    "TeleRIS",
    "orthanc-fromInit"
]

# and the details of a specific PACS service with
xh http://localhost:4005/api/v1/PACSservice/orthanc/

HTTP/1.1 200 OK
Content-Length: 270
Content-Type: application/json
Date: Thu, 03 Nov 2022 23:41:58 GMT
Server: uvicorn

{
    "info": {
        "aet": "CHRISLOCAL",
        "aet_listener": "ORTHANC",
        "aec": "ORTHANC",
        "serverIP": "192.168.1.200",
        "serverPort": "4242"
    },
    "time_created": {
        "time": "2022-11-03 13:55:02.245543"
    },
    "time_modified": {
        "time": "2022-11-03 13:55:02.245578"
    },
    "message": "Service information for 'orthanc'"
}
```

The above showed two different ways to reach the same goal. In the first, the setup file called 'defaults.json' is used to read the PACS details. This method of course assumes that the 'defaults.json' file exists. This is considered more of a "boot strap" method and only shown for completeness and legacy sake.

A more effective method is the second example. Here, assuming `pfdcm` has been instantiated, it can be queried to use any of its configured PACS servers to service the query. This example is used in the rest of this document.

In general, you can use any reasonable DICOM tag to drive the query. For more fine tuned searches, you can do

```bash
./pfdcm.sh --pfdcmPACS PACSDCM --query -- "PatientID:2233445,StudyDate:20210901"
```

to limit the query to, in this case, a specific study date. Once you have determined an image set of interest, you can request a `retrieve`

```bash
./pfdcm.sh --pfdcmPACS PACSDCM --retrieve -- "PatientID:2233445,StudyDate:20210901"
```

which will handle incoming file transmission from the PACS and store/pack the files on the local (container) filesystem. Note that the `retrieve` is an asynchronous request and will return to the client immediately. To determine the status of the operation,

```bash
./pfdcm.sh --pfdcmPACS PACSDCM --status -- "PatientID:2233445,StudyDate:20210901"
```

Once all the files have been retrieved, the files can be pushed to CUBE swift storage (assuming an available CUBE instance):

```bash
./pfdcm.sh --pfdcmPACS PACSDCM --push -- "PatientID:2233445,StudyDate:20210901"
```

after a successful push operation (check on progress using `status`), files in swift storage can be registered to the CUBE internal database with

```bash
./pfdcm.sh --pfdcmPACS PACSDCM --register -- "PatientID:2233445,StudyDate:20210901"
```

Note that the `--pfdcmPACS PACSDCM` means "use configured parameters" which are defined initially in the `defaults.json` file and written to the `pfdcm`  database using appropriate setup directives (see the `workflow.sh`).

Please note that many more options/tweaks etc are available. Feel free to ping the authors for additional info.

#### SeriesInstanceUID operations

Often it might be necessary to operate at the SeriesInstanceUID level, especially if retrieval of a single series is desired. In this case, it is best to generate a report in csv format with the `SeriesInstanceUID` in the table (note, sometimes the `StudyInstanceUID` might also be needed):

```bash
./pfdcm.sh --pfdcmPACS PACSDCM  --query \
           -T csv -H PatientID,StudyInstanceUID \
           --csvCLI "--reportBodySeriesTags SeriesDescription,SeriesInstanceUID --csvPrettify" -- \
           "AccessionNumber:22315573"
```

Here, the `-H PatientID,StudyInstanceUID` overrides the "header" information, while the `--csvCLI` and `--reportBodySeriesTags` define the body information to display.

#### Bulk operations

`pfdcm.sh` also offers bulk operations that follow the same contract as above (i.e. `--query`, `--retrieve`, `--status`, `--push`, `--register`). To perform a bulk set of operations, simply specify the set of search terms separated by a semi colon `;` as a tokenization character. So imagine you have four MRNs, `1111111`, `2222222`, `3333333`, `4444444`. You can specify all these in one search construct:

```bash
./pfdcm.sh --pfdcmPACS PACSDCM --query -- \
    "PatientID:1111111;PatientID:2222222;PatientID:3333333;PatientID:4444444"
```

Note that each component of the search can be further specified by adding a comma list of refinements if you choose:

```bash
./pfdcm.sh --pfdcmPACS PACSDCM --query -- \
    "PatientID:1111111,StudyDate:20210901;PatientID:2222222;PatientID:3333333;PatientID:4444444"
```

which will limit `PatientID:1111111` results to only those that had the specified `StudyDate` as well.

In general, the search construct can become cumbersome especially if a long list of single search tokens (e.g. `PatientID`) is used. In that case, you can use the `-K` (or `--multikey`) flag to simplify somewhat by indicating _apply this DICOM key to each element of the search construct_:

```bash
./pfdcm.sh --pfdcmPACS PACSDCM --query -K PatientID -- \
    "1111111;2222222;3333333;4444444"
```

When using a `-K` then it is not possible to add additional filter arguments on a search construct (in other words you can't further filter on `StudyDate` for example). Note that you can also present the above command as

```bash
./pfdcm.sh --pfdcmPACS PACSDCM --query -K PatientID -- \"
1111111;
2222222;
3333333;
4444444;
"
```

which might be easier if you have a spreadsheet of MRNs to process. Take care to still add the semicolon `;` for all the entries! This semi-colon is optional on the final entry.

For completeness sake, and staying with the spreadsheet theme, you can construct a rather complete query specification on the CLI using a copy-paste from a properly "formatted" spreadsheet:

```bash
./pfdcm.sh --pfdcmPACS PACSDCM --query -- \"
PatientID:1111111,StudyDate:19000101;
PatientID:2222222,StudyDate:19001101;
PatientID:3333333,StudyDate:19002101;
PatientID:4444444,StudyDate:19003101;
AccessionNumber:7654321;
SeriesInstanceUID:1.3.12.2.1107.5.2.32.35201.30000017082012560654900020230
"
```

The above should perform 6 queries, each on the specified patterning.

#### ILoveCandy (and maybe spreadsheets)

When doing bulk operations, the default colorized tabular output can become confusing. Adding a `-Q` to the CLI will also indicate the search token being as it is being processed used which can help. Another option is to use a `-T csv` (or equivalently `--reportType csv`) to generate a spreadsheet-type output.

```bash
./pfdcm.sh --pfdcmPACS PACSDCM --query -Q -T csv -K PatientID -- \
    "1111111;2222222;3333333;4444444"
```

This will still attempt to print a report-style result that while pretty in the console, is not ideal for using in a spreadsheet. If you want to create import-friendly output with a specific cell separator character (like `,`) you can do

```bash
./pfdcm.sh --pfdcmPACS PACSDCM --query -Q -T csv --csvCLI "--csvSeparator ," \
          -K PatientID -- \
          "1111111;2222222;3333333;4444444" > table.csv
```

which will save the results into a file `table.csv` that is suitable for ingestion into a spreadsheet program.

#### Orthanc quirks

If you are using Orthanc, it is possible to perform an open ended interaction on **all** the images in the database. This is *NOT* recommended for obvious reasons on production systems! Still, to get a list of _everything_ in an Orthanc PACS server, do

```bash
./pfdcm.sh --pfdcmPACS PACSDCM --query -T csv -K "" -- ":all"
```

The following will dump the entire contents of Orthanc into a csv file suitable for loading in a spreadsheet:

```bash
./pfdcm.sh --pfdcmPACS PACSDCM --query -Q -T csv --csvCLI "--csvSeparator ," -K "" -- ":all" > /tmp/table.csv
```

**DO NOT ATTEMPT ON A REAL PACS SYSTEM**.

## Development

To debug code within `pfdcm` from a containerized instance, perform volume mappings in an interactive session:

```bash
# Run with support for source debugging
docker run --name pfdcm  --rm -it                                              	\
        -p 4005:4005 -p 11113:11113 	                                        \
        -v /home/dicom:/home/dicom                                             	\
        -v $PWD/pfdcm:/app:ro                                                  	\
        local/pfdcm /start-reload.sh
```

_-30-_
