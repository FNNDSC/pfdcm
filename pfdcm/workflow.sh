# Build
set UID (id -u)
docker build --build-arg UID=$UID -t local/pfdcm .   

# Quick n dirty
docker run --rm -it                                                            \
        -p 4005:4005 -p 5555:5555 -p 10502:10502 -p 11113:11113                \
        local/pfdcm /start-reload.sh

# With support for source debugging
docker run --rm -it                                                            \
        -p 4005:4005 -p 5555:5555 -p 10502:10502 -p 11113:11113                \
        -v $PWD/pfdcm:/app:ro                                                  \
        local/pfdcm /start-reload.sh

# Access documentation        
URL :4005/docs

# Configure a swift access key -- needed for 
# pypx/push operations
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

# Get a list of swift services
curl -s -X 'GET' \
  'http://localhost:4005/api/v1/SMDB/swift/list' \
  -H 'accept: application/json' | jq

# Get info on a specific swift service
curl -s -X 'GET' \
  'http://localhost:4005/api/v1/SMDB/swift/megalodon' \
  -H 'accept: application/json' | jq
  
# Configure a CUBE access key -- needed for
# pypx/register operations
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

# Get a list of CUBE services
curl -s -X 'GET' \
  'http://localhost:4005/api/v1/SMDB/CUBE/list' \
  -H 'accept: application/json' | jq

# Get info on a specific CUBE service
curl -s -X 'GET' \
  'http://localhost:4005/api/v1/SMDB/CUBE/megalodon' \
  -H 'accept: application/json' | jq

# Fire up the local listener services
curl -s -X 'POST' \
  'http://localhost:4005/api/v1/listener/initialize/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "value": "default"
}' | jq

# Config ORTHANC PACS
curl -s -X 'PUT' \
  'http://localhost:4005/api/v1/PACSservice/orthanc' \
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

# list PACS services
curl -s -X 'GET' \
  'http://localhost:4005/api/v1/PACSservice/list' \
  -H 'accept: application/json' | jq

# GET detail on 'orthanc'
curl -s -X 'GET' \
  'http://localhost:4005/api/v1/PACSservice/orthanc/' \
  -H 'accept: application/json' | jq

# Perform a QUERY 
curl -s -X 'POST' \
  'http://localhost:4005/api/v1/PACS/pypx/' \
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
    "PatientID": "5644810",
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
                --reportHeaderStudyTags PatientName,PatientID,StudyDate

# Retrieve data 
curl -s -X 'POST' \
  'http://localhost:4005/api/v1/PACS/pypx/' \
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
    "PatientID": "5644810",
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

# Request the STATUS
curl -s -X 'POST' \
  'http://localhost:4005/api/v1/PACS/pypx/' \
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
    "PatientID": "5644810",
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
    "then": "status",
    "thenArgs": "",
    "dblogbasepath": "/home/dicom/log",
    "json_response": false
  }
}' | jq

# PUSH to swift
curl -s -X 'POST' \
  'http://localhost:4005/api/v1/PACS/pypx/' \
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
    "PatientID": "5644810",
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
    "then": "push",
    "thenArgs": "{\"db\": \"/home/dicom/log\", \"swift\": \"megalodon\", \"swiftServicesPACS\": \"WIP2\", \"swiftPackEachDICOM\":   true}",
    "dblogbasepath": "/home/dicom/log",
    "json_response": false
  }
}' | jq

# REGISTER to CUBE
curl -s -X 'POST' \
  'http://localhost:4005/api/v1/PACS/pypx/' \
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
    "PatientID": "5644810",
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
    "thenArgs": "{\"db\": \"/home/dicom/log\", \"swift\": \"megalodon\", \"swiftServicesPACS\": \"WIP2\", \"swiftPackEachDICOM\":   true}",
    "dblogbasepath": "/home/dicom/log",
    "json_response": false
  }
}' | jq

