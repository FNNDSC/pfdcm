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

# Fire up the local listener services
curl -X 'POST' \
  'http://localhost:4005/api/v1/listener/initialize/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "value": "default"
}' | jq

# Config ORTHANC PACS
curl -X 'PUT' \
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
curl -X 'GET' \
  'http://localhost:4005/api/v1/PACSservice/list' \
  -H 'accept: application/json' | jq

# GET detail on 'orthanc'
curl -X 'GET' \
  'http://localhost:4005/api/v1/PACSservice/orthanc/' \
  -H 'accept: application/json' | jq

# Perform a QUERY 
curl -X 'POST' \
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
curl -X 'POST' \
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
    "dblogbasepath": "/home/dicom/log",
    "json_response": true
  }
}'

# Request the STATUS
curl -X 'POST' \
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
    "dblogbasepath": "/home/dicom/log",
    "json_response": false
  }
}'
