#!/bin/bash
#
# NAME
#
#       singleEx.sh
#
# SYNOPSIS
#
#       singleEx.sh [-i] <MRN>
#
# DESC
#
#       A simple exemplar script that demonstrates how to setup the 
#       pfdcm infrastructure, and run/execute a *full* PACS Q/R 
#       with resultant images registered to a CUBE instance.
#
# ARGS
#
#       <MRN>
#       The MRN to use for the pull/push/register workflow
#
#       [-i]
#       If specified, perform the initialization steps, otherwise
#       skip.
#
# PRECONDITIONS
# o A pull on the current `pfdcm`
# o Building the docker image, and executing with
#
EXECpfdm="
docker run --rm -it                                                            \
        -p 4005:4005 -p 5555:5555 -p 10502:10502 -p 11113:11113                \
        -v /home/dicom:/home/dicom                                             \
        -v $PWD/pfdcm:/app:ro                                                  \
        local/pfdcm /start-reload.sh
"

declare -i b_initDo=0
declare -i b_queryDo=0
declare -i b_retrieveDo=0
declare -i b_pushDo=0
declare -i b_registerDo=0
declare -i b_statuDos=0

while getopts "iqrpgs" opt; do
    case $opt in
        i) b_initDo=1                   ;;
        q) b_queryDo=1                  ;;
        r) b_retrieveDo=1               ;;
        p) b_pushDo=1                   ;;
        g) b_registerDo=1               ;;
        s) b_statusDo=1                 ;;
    esac
done
shift $(($OPTIND - 1))
MRN=$*

if (( b_initDo )) ; then
        # Configure a swift access key/detail
        curl -s -X 'POST' \
          'http://localhost:4005/api/v1/SMDB/swift/' \
          -H 'accept: application/json' \
          -H 'Content-Type: application/json' \
          -d '{
          "swiftKeyName": {
            "value": "megalodon"
          },
          "swiftInfo": {
            "ip": "192.168.1.216",
            "port": "8080",
            "login": "chris:chris1234"
          }
        }' | jq

        # Configure CUBE access key/detail
        curl -s -X 'POST' \
          'http://localhost:4005/api/v1/SMDB/CUBE/' \
          -H 'accept: application/json' \
          -H 'Content-Type: application/json' \
          -d '{
          "cubeKeyName": {
            "value": "megalodon"
          },
          "cubeInfo": {
            "url": "http://192.168.1.216:8000/api/v1/",
            "username": "chris",
            "password": "chris1234"
          }
        }' | jq

        #
        # REST API Calls -- on the "client"
        #
        #
        # SETUP
        #
        #
        # CONFIGURE PACS RELATED SERVICES
        #
        # On hot restart of the app (whenever a software change has been made)
        # internal "hot" data in the app is lost. Specifically this relates to the
        # listener service and the orthanc/PACS service.
        #
        # Here we configure two services -- a listener based off xinetd that will
        # intercept and handle data pushed from the PACS, and the actual PACS 
        # detail as well.
        #
        # Start by firing up the local listener services... after this call pfdcm
        # is ready to process incoming DICOM transmissions (on a port configured in
        # the Dockerfile and port mapped -- obviously this port must be known to the
        # PACS service since it will transmit data to this location).
        #
        # Note this call has a slight delay...
        curl -s -X 'POST' \
          'http://localhost:4005/api/v1/listener/initialize/' \
          -H 'accept: application/json' \
          -H 'Content-Type: application/json' \
          -d '{
          "value": "default"
        }' | jq

        # Now let pfdcm know what PACS service it will communicate with.
        # Here, we configure an ORTHANC PACS (that in turn is suitably configured
        # to speak with pfdcm). Circular comms, oh my!
        # Oh, and obviously YMMV -- set your serverIP appropriately!
        curl -s -X 'PUT' \
          'http://localhost:4005/api/v1/PACSservice/orthanc/' \
          -H 'accept: application/json' \
          -H 'Content-Type: application/json' \
          -d '{
          "info": {
            "aet": "CHRISLOCAL",
            "aet_listener": "ORTHANC",
            "aec": "ORTHANC",
            "serverIP": "192.168.1.189",
            "serverPort": "4242"
          }
        }' | jq
fi

if (( ${#MRN} )) ; then

        if (( b_queryDo )) ; then 
                curl -s -X 'POST' \
                  'http://localhost:4005/api/v1/PACS/sync/pypx/' \
                  -H 'accept: application/json' \
                  -H 'Content-Type: application/json' \
                  -d '{
                  "PACSservice": {
                    "value": "orthanc"
                  },
                  "listenerService": {
                    "value": "default"
                  },
                  "pypx_find": {
                    "AccessionNumber": "",
                    "PatientID": "'$MRN'",
                    "PatientName": "",
                    "PatientBirthDate": "",
                    "PatientAge": "",
                    "PatientSex": "",
                    "StudyDate": "",
                    "StudyDescription": "",
                    "StudyInstanceUID": "",
                    "Modality": "",
                    "ModalitiesInStudy": "",
                    "PerformedStationAETitle": "",
                    "NumberOfSeriesRelatedInstances": "",
                    "InstanceNumber": "",
                    "SeriesDate": "",
                    "SeriesDescription": "",
                    "SeriesInstanceUID": "",
                    "ProtocolName": "",
                    "AcquisitionProtocolDescription": "",
                    "AcquisitionProtocolName": "",
                    "withFeedBack": false,
                    "then": "",
                    "thenArgs": "",
                    "dblogbasepath": "/home/dicom/log",
                    "json_response": true
                  }
                }'| jq '.pypx' |\
                 px-report      --colorize dark \
                                --printReport csv \
                                --csvPrettify \
                                --csvPrintHeaders \
                                --reportHeaderStudyTags PatientName,PatientID,StudyDate \
                                --reportBodySeriesTags SeriesDescription,SeriesInstanceUID
        fi

        if (( b_retrieveDo )) ; then
                curl -s -X 'POST' \
                  'http://localhost:4005/api/v1/PACS/exec/pypx/' \
                  -H 'accept: application/json' \
                  -H 'Content-Type: application/json' \
                  -d '{
                  "PACSservice": {
                    "value": "orthanc"
                  },
                  "listenerService": {
                    "value": "default"
                  },
                  "PACSdirective": {
                    "AccessionNumber": "",
                    "PatientID": "'$MRN'",
                    "PatientName": "",
                    "PatientBirthDate": "",
                    "PatientAge": "",
                    "PatientSex": "",
                    "StudyDate": "",
                    "StudyDescription": "",
                    "StudyInstanceUID": "",
                    "Modality": "",
                    "ModalitiesInStudy": "",
                    "PerformedStationAETitle": "",
                    "NumberOfSeriesRelatedInstances": "",
                    "InstanceNumber": "",
                    "SeriesDate": "",
                    "SeriesDescription": "",
                    "SeriesInstanceUID": "",
                    "ProtocolName": "",
                    "AcquisitionProtocolDescription": "",
                    "AcquisitionProtocolName": "",
                    "withFeedBack": false,
                    "then": "retrieve",
                    "thenArgs": "",
                    "dblogbasepath": "/home/dicom/log",
                    "json_response": true
                  }
                }' | jq
        fi

        if (( b_statusDo )) ; then 
                curl -s -X 'POST' \
                  'http://localhost:4005/api/v1/PACS/sync/pypx/' \
                  -H 'accept: application/json' \
                  -H 'Content-Type: application/json' \
                  -d '{
                  "PACSservice": {
                    "value": "orthanc"
                  },
                  "listenerService": {
                    "value": "default"
                  },
                  "pypx_find": {
                    "AccessionNumber": "",
                    "PatientID": "'$MRN'",
                    "PatientName": "",
                    "PatientBirthDate": "",
                    "PatientAge": "",
                    "PatientSex": "",
                    "StudyDate": "",
                    "StudyDescription": "",
                    "StudyInstanceUID": "",
                    "Modality": "",
                    "ModalitiesInStudy": "",
                    "PerformedStationAETitle": "",
                    "NumberOfSeriesRelatedInstances": "",
                    "InstanceNumber": "",
                    "SeriesDate": "",
                    "SeriesDescription": "",
                    "SeriesInstanceUID": "",
                    "ProtocolName": "",
                    "AcquisitionProtocolDescription": "",
                    "AcquisitionProtocolName": "",
                    "withFeedBack": false,
                    "then": "status",
                    "thenArgs": "",
                    "dblogbasepath": "/home/dicom/log",
                    "json_response": true
                  }
                }' | jq '.pypx' |\
                px-report       --seriesSpecial seriesStatus                                   \
                                --printReport tabular                                          \
                                --colorize dark                                                \
                                --reportBodySeriesTags seriesStatus
        fi

        if (( b_pushDo )) ; then
                curl -s -X 'POST' \
                  'http://localhost:4005/api/v1/PACS/exec/pypx/' \
                  -H 'accept: application/json' \
                  -H 'Content-Type: application/json' \
                  -d '{
                  "PACSservice": {
                    "value": "orthanc"
                  },
                  "listenerService": {
                    "value": "default"
                  },
                  "pypx_find": {
                    "AccessionNumber": "",
                    "PatientID": "'$MRN'",
                    "PatientName": "",
                    "PatientBirthDate": "",
                    "PatientAge": "",
                    "PatientSex": "",
                    "StudyDate": "",
                    "StudyDescription": "",
                    "StudyInstanceUID": "",
                    "Modality": "",
                    "ModalitiesInStudy": "",
                    "PerformedStationAETitle": "",
                    "NumberOfSeriesRelatedInstances": "",
                    "InstanceNumber": "",
                    "SeriesDate": "",
                    "SeriesDescription": "",
                    "SeriesInstanceUID": "",
                    "ProtocolName": "",
                    "AcquisitionProtocolDescription": "",
                    "AcquisitionProtocolName": "",
                    "withFeedBack": false,
                    "then": "push",
                    "thenArgs": "{\"db\": \"/home/dicom/log\", \"swift\": \"megalodon\", \"swiftServicesPACS\": \"WIP2\", \"swiftPackEachDICOM\":   true}",
                    "dblogbasepath": "/home/dicom/log",
                    "json_response": true
                  }
                }' | jq
        fi

        if (( b_registerDo )) ; then
                curl -s -X 'POST' \
                  'http://localhost:4005/api/v1/PACS/exec/pypx/' \
                  -H 'accept: application/json' \
                  -H 'Content-Type: application/json' \
                  -d '{
                  "PACSservice": {
                    "value": "orthanc"
                  },
                  "listenerService": {
                    "value": "default"
                  },
                  "pypx_find": {
                    "AccessionNumber": "",
                    "PatientID": "'$MRN'",
                    "PatientName": "",
                    "PatientBirthDate": "",
                    "PatientAge": "",
                    "PatientSex": "",
                    "StudyDate": "",
                    "StudyDescription": "",
                    "StudyInstanceUID": "",
                    "Modality": "",
                    "ModalitiesInStudy": "",
                    "PerformedStationAETitle": "",
                    "NumberOfSeriesRelatedInstances": "",
                    "InstanceNumber": "",
                    "SeriesDate": "",
                    "SeriesDescription": "",
                    "SeriesInstanceUID": "",
                    "ProtocolName": "",
                    "AcquisitionProtocolDescription": "",
                    "AcquisitionProtocolName": "",
                    "withFeedBack": true,
                    "then": "register",
                    "thenArgs": "{\"db\": \"/home/dicom/log\", \"CUBE\": \"megalodon\", \"swiftServicesPACS\": \"WIP2\", \"parseAllFilesWithSubStr\":   \"dcm\"}",
                    "dblogbasepath": "/home/dicom/log",
                    "json_response": false
                  }
                }' | jq
        fi
fi

#
# _-30-_
#

