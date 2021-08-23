#
# PRELIMINARIES -- on the "server"
#
# Build the container and then "run" it.
# Depending on your purpose, choose either the Quick 'n dirty run
# or, while developing, choose the run with support for source debugging.
#

# Build (for fish shell syntax!)
set UID (id -u)
docker build --build-arg UID=$UID -t local/pfdcm .   

# Quick 'n dirty run -- this is what you'll mostly do.
# Obviously change port mappings if needed (and in the Dockerfile)
docker run --rm -it                                                            \
        -p 4005:4005 -p 5555:5555 -p 10502:10502 -p 11113:11113                \
        local/pfdcm /start-reload.sh

# Quick 'n dirty run -- with volume mapping.
# Obviously change port mappings if needed (and in the Dockerfile)
docker run --rm -it                                                            \
        -p 4005:4005 -p 5555:5555 -p 10502:10502 -p 11113:11113                \
        -v /home/dicom:/home/dicom                                             \
        local/pfdcm /start-reload.sh

# Run with support for source debugging
docker run --rm -it                                                            \
        -p 4005:4005 -p 5555:5555 -p 10502:10502 -p 11113:11113                \
        -v /home/dicom:/home/dicom                                             \
        -v $PWD/pfdcm:/app:ro                                                  \
        local/pfdcm /start-reload.sh

# Access documentation        
URL :4005/docs

#
# REST API Calls -- on the "client"
#
#
# SETUP
# First we setup swift and CUBE resources. These allow underlying tools
# of the system to associate a set of login details for a resource 
# with a keyname.
#
 
# Configure a swift access key -- needed for pypx/push operations
# When DICOM images have been "pulled" from a PACS, they first reside on the
# pfdcm filesystem. From here, they need to be pushed to CUBE's swift storage
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

# Check on the above by getting a list of swift resources...
# In the above call we created a resource called "megalodon"
# and should see that resource in the return of the call
curl -s -X 'GET' \
  'http://localhost:4005/api/v1/SMDB/swift/list/' \
  -H 'accept: application/json' | jq

# Now, get the detail again on the "megalodon" resource.
curl -s -X 'GET' \
  'http://localhost:4005/api/v1/SMDB/swift/megalodon/' \
  -H 'accept: application/json' | jq
  
# Similarly, we now configure a CUBE access key -- needed for
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

# Get a list of CUBE services -- we should see "megalodon" in the list
curl -s -X 'GET' \
  'http://localhost:4005/api/v1/SMDB/CUBE/list/' \
  -H 'accept: application/json' | jq

# Ask about the "megalodon" CUBE service -- this describes the information
# needed to log into CUBE
curl -s -X 'GET' \
  'http://localhost:4005/api/v1/SMDB/CUBE/megalodon/' \
  -H 'accept: application/json' | jq

#
# CONFIGURE PACS RELATED SERVICES
#
# Here we configure two services -- a listener based off xinetd that will
# intercept and handle data pushed from the PACS, and the actual PACS 
# detail as well.

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

# Let's check by listing available PACS services
curl -s -X 'GET' \
  'http://localhost:4005/api/v1/PACSservice/list/' \
  -H 'accept: application/json' | jq

# GET detail on 'orthanc'
curl -s -X 'GET' \
  'http://localhost:4005/api/v1/PACSservice/orthanc/' \
  -H 'accept: application/json' | jq

#
# NOW FOR THE GOOD STUFF!
#
# Perform a QUERY on say a PatientID...
# ... and for extra kicks, if you have done a 
#
#               pip install pypx 
#
# you can pipe the output of the REST call to a report module, px-report
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
                --reportHeaderStudyTags PatientName,PatientID,StudyDate \
                --reportBodySeriesTags SeriesDescription,SeriesInstanceUID

#
# RETRIEVE
#
# The model idea here needs some explanation. Basically, to keep things simple
# _one_ way of interacting with pfdcm is to reuse the `find/search`, but just
# give it downstream directives. So, if we want to pull all the data from the
# above we can use the same command, just add a {"then": "retrieve"} in the 
# payload.
#
# Of course, if we only want a single series, we can do the find on the
# SeriesInstanceUID and retrieve only those results.
#

# Retrieve only one SeriesInstanceUID -- 
# Ugh.... at time of writing this below is still a WIP... skip ahead, please.
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
    "PatientID": "",
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
    "SeriesInstanceUID": "1.3.12.2.1107.5.2.19.45479.2021061717465158664020277.0.0.0",
    "ProtocolName": "",
    "AcquisitionProtocolDescription": "",
    "AcquisitionProtocolName": "",
    "withFeedBack": true,
    "then": "retrieve",
    "thenArgs": "",
    "dblogbasepath": "/home/dicom/log",
    "json_response": true
  }
}' | jq

# What the heck, let's just retrieve all the info for this ID... This def
# works!
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

curl -s -X 'POST' \
  'http://localhost:4005/api/v1/PACS/thread/retrieve/' \
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
    "PatientID": "LILLA-9678",
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
}'

curl -s -X 'POST' \
  'http://localhost:4005/api/v1/PACS/exec/retrieve/' \
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
    "PatientID": "LILLA-9678",
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
}'


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

#
# Now, all the images will exist within the pfdcm container. If you
# ran the container with appropriate volume mapping, then files should be
# accessible in your host. 
#
# Here, we add these files to CUBE.
#
# First, we have to push to swift...
# remember way back... in the beginning? We setup a swift resource called
# 'megalodon' -- well, here is where we use it.
#
# Also the swiftSerivcesPACS : WIP2 is the "subdir" in the CUBE
#
#                      SERVICES/PACS/<swiftServicesPACS>
#
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

# Now, assuming all has gone well, the final step is to register the files
# in CUBE swift storage to CUBE itself... again, see the CUBE resource
# initialization we did in the beginning. Here is where we use it...
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
    "thenArgs": "{\"db\": \"/home/dicom/log\", \"CUBE\": \"megalodon\", \"swiftServicesPACS\": \"WIP2\", \"parseAllFilesWithSubStr\":   \"dcm\"}",
    "dblogbasepath": "/home/dicom/log",
    "json_response": false
  }
}' | jq

#
# And we're done! If all went well, the DICOM files from PACS will now be
# accessible to CUBE.
#
# _-30-_
#

