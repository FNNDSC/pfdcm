export PURPOSE="
    This script describes by way of demonstration various explicit examples of
    how to interact with the pfdcm API using curl.

    This script is considered 'low level' or a reference source of truth --
    c.f. the pfdcm.sh script that provides a convenience CLI which internally
    calls many of these same curl constructs.

    Calls in this script can be used to connect a PACS database to a ChRIS
    instance. By 'connect' is meant the set of actions to determine images of
    interest in a PACS and to ultimately send those same images to a ChRIS
    instance for subsequent image analysis.

    The set of operations, broadly, are:

        * query an associated PACS for information on patient STUDY and
          SERIES data;
        * query a PACS for images of interest and report on results in a
          variety of ways;
        * retrieve a set of images of interest;
        * push the retrieved images to CUBE swift storage;
        * register the pushed-into-swift images with CUBE;

    Each set of operations is present with as CLI using 'on-the-metal' curl
    calls.

    To use this script, simply:

      $ source \$PWD/workflow.sh

    MAKE SURE ANY ENV VARIABLES SET BY THIS ARE WHAT YOU WANT!!

    and then call the named functions, for example

      $ build
      $ launch_debug
      $ listen
      $ PACSservice_put
      $ PACSservice_detail
      $ query
      $ retrieve
      $ status_console
      $ push
      $ register

    or examine this script and copy/paste the curl CLI into your terminal
    (bash/zsh/fish).

    The list of functions are:


    NOTE:
        * This script should work across bash-type shells i.e. bash/zsh
          however, individual curl commands can be copy/pasted into a
          fish shell.

    Q/A LOG:
        * 07-Jan-2022 -> 08-Jan-2022
          Full test of each command/line against a ChRIS instance and orthanc
          server running within a local network.
"

###############################################################################
#_____________________________________________________________________________#
# E N V                                                                       #
#_____________________________________________________________________________#
# Set the following variables appropriately for your local setup.             #
###############################################################################

#
# swift storage environment
#
export SWIFTKEY=local
export SWIFTHOST=10.0.0.230
export SWIFTPORT=8080
export SWIFTLOGIN=chris:chris1234
export SWIFTSERVICEPACS=orthanc

#
# CUBE login details
#
export CUBEKEY=local
export CUBEURL=http://10.0.0.230:8000/api/v1/
export CUBEusername=chris
export CUBEuserpasswd=chris1234

#
# PACS details
#
# For ex a FUJI PACS
export AEC=CHRIS
export AET=CHRISV3
export PACSIP=134.174.12.21
export PACSPORT=104
export PACSNAME=PACSDCM
#
# For ex an orthanc service
#
export AEC=ORTHANC
export AET=CHRISLOCAL
export PACSIP=10.0.0.230
export PACSPORT=4242
export PACSNAME=orthanc
#
# pfdcm service
#
# In some envs, this MUST be an IP address!
export PFDCMURL=http://localhost:4005

# Patient Query detail
export MRN=4443508
export STUDYUID=1.2.840.113845.11.1000000001785349915.20130312110508.6351586
export SERIESUID=1.3.12.2.1107.5.2.19.45152.2013031212563759711672676.0.0.0
export ACCESSIONNUMBER=22681485

# Directory mounts etc
export DB=/home/dicom/log
export DATADIR=/home/dicom/data
export BASEMOUNT=/home/dicom

###############################################################################
#_____________________________________________________________________________#
# B U I L D                                                                   #
#_____________________________________________________________________________#
# Build the container image in a variety of difference contexts/use cases.    #
###############################################################################

build () {
# UID
# for fish:
# export UID=(id -u)
# for bash/zsh
export UID=$(id -u)
# Build (for fish shell syntax!)
docker build --build-arg UID=$UID -t local/pfdcm .
}

launch_quickndirty () {
# Quick 'n dirty run -- this is what you'll mostly do.
# Obviously change port mappings if needed (and in the Dockerfile)
docker run --rm -it                                                            \
        -p 4005:4005 -p 10402:11113 -p 11113:11113                             \
        local/pfdcm /start-reload.sh
}

launch_qndwithdb () {
# Quick 'n dirty run -- with volume mapping.
# Obviously change port mappings if needed (and in the Dockerfile)
docker run --rm -it                                                            \
        -p 4005:4005 -p 10402:11113 -p 11113:11113                             \
        -v /home/dicom:/home/dicom                                             \
        local/pfdcm /start-reload.sh
}

launch_debug () {
# Run with support for source debugging
docker run --rm -it                                                            \
        -p 4005:4005 -p 10402:11113 -p 11113:11113                             \
        -v /home/dicom:/home/dicom                                             \
        -v $PWD/pfdcm:/app:ro                                                  \
        local/pfdcm /start-reload.sh
}

# To access the API swagger documentation, point a brower at:
export swaggerURL=":4005/docs"

###############################################################################
#_____________________________________________________________________________#
# P A C S  s e t u p  a n d  S e r v i c e S t a r t                          #
#_____________________________________________________________________________#
###############################################################################
# Setup the information relevant to the PACS.                                 #
###############################################################################
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

listen () {
# Note this call has a slight delay...
curl -s -X 'POST'                                                             \
  "$PFDCMURL/api/v1/listener/initialize/"                                     \
  -H 'accept: application/json'                                               \
  -H 'Content-Type: application/json'                                         \
  -d '{
        "value": "default"
      }' | jq
}

PACSservice_put () {
# Now let pfdcm know what PACS service it will communicate with.
# Here, we configure an ORTHANC PACS (that in turn is suitably configured
# to speak with pfdcm). Circular comms, oh my!
# Oh, and obviously YMMV -- set your serverIP appropriately!
curl -s -X 'PUT'                                                              \
  "$PFDCMURL/api/v1/PACSservice/$PACSNAME/"                                   \
  -H 'accept: application/json'                                               \
  -H 'Content-Type: application/json'                                         \
  -d '{
        "info": {
          "aet":            "'$AET'",
          "aet_listener":   "'$AEC'",
          "aec":            "'$AEC'",
          "serverIP":       "'$PACSIP'",
          "serverPort":     "'$PACSPORT'"
        }
}' | jq
}

PACSservice_list () {
# Let's check by listing available PACS services
curl -s -X 'GET'                                                              \
  "$PFDCMURL/api/v1/PACSservice/list/"                                        \
  -H 'accept: application/json' | jq
}

PACSservice_detail () {
# GET detail on $PACSNAME
curl -s -X 'GET'                                                              \
  "$PFDCMURL/api/v1/PACSservice/$PACSNAME/"                                   \
  -H 'accept: application/json' | jq
}

###############################################################################
#_____________________________________________________________________________#
# S W I F T                                                                   #
#_____________________________________________________________________________#
###############################################################################
# First we setup swift and CUBE resources. These allow underlying tools       #
# of the system to associate a set of login details for a resource            #
# with a keyname.                                                             #
###############################################################################

swift_post () {
# Configure a swift access key -- needed for pypx/push operations
# When DICOM images have been "pulled" from a PACS, they first reside on the
# pfdcm filesystem. From here, they need to be pushed to CUBE's swift storage
# This call sets the data within a service file, `swift.json`.
curl -s -X 'POST'                                                             \
    "$PFDCMURL/api/v1/SMDB/swift/"                                            \
    -H 'accept: application/json'                                             \
    -H 'Content-Type: application/json'                                       \
    -d '{
    "swiftKeyName": {
      "value": "'$SWIFTKEY'"
    },
    "swiftInfo": {
      "ip":     "'$SWIFTHOST'",
      "port":   "'$SWIFTPORT'",
      "login":  "'$SWIFTLOGIN'"
    }
}' | jq
}

swift_list () {
# Check on the above by getting a list of swift resources...
# In the above call we created a resource called "$SWIFTKEY"
# and should see that resource in the return of the call
curl -s -X 'GET' \
  "$PFDCMURL/api/v1/SMDB/swift/list/"                                         \
  -H 'accept: application/json' | jq
}

swift_detail () {
# Now, get the detail again on the "$SWIFTKEY" resource.
curl -s -X 'GET' \
  "$PFDCMURL/api/v1/SMDB/swift/$SWIFTKEY/"                                    \
  -H 'accept: application/json' | jq
}

###############################################################################
#_____________________________________________________________________________#
# C U B E                                                                     #
#_____________________________________________________________________________#
###############################################################################
# Setup the information relevant to CUBE.                                     #
###############################################################################

cube_post () {
# Similarly, we now configure a CUBE access key -- needed for
# pypx/register operations
curl -s -X 'POST'                                                             \
  "$PFDCMURL/api/v1/SMDB/CUBE/"                                               \
  -H 'accept: application/json'                                               \
  -H 'Content-Type: application/json'                                         \
  -d '{
  "cubeKeyName": {
    "value": "'$CUBEKEY'"
  },
  "cubeInfo": {
    "url": "'$CUBEURL'",
    "username": "'$CUBEusername'",
    "password": "'$CUBEuserpasswd'"
  }
}' | jq
}

cube_list () {
# Get a list of CUBE services -- we should see "$CUBEKEY" in the list
curl -s -X 'GET' \
  "$PFDCMURL/api/v1/SMDB/CUBE/list/"                                          \
  -H 'accept: application/json' | jq
}

cube_detail () {
# Ask about the "$CUBEKEY" CUBE service -- this describes the information
# needed to log into CUBE
curl -s -X 'GET' \
  "$PFDCMURL/api/v1/SMDB/CUBE/$CUBEKEY/"                                      \
  -H 'accept: application/json' | jq
}

# In the calls below, the PACS can be accessed and images "searched" using
# any of the fields below in the PACSdirective JSON structure:
export PACSdirectiveJSON='
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
    "SeriesInstanceUID": "",
    "ProtocolName": "",
    "AcquisitionProtocolDescription": "",
    "AcquisitionProtocolName": "",
'

###############################################################################
#_____________________________________________________________________________#
# Q U E R Y                                                                   #
#_____________________________________________________________________________#
###############################################################################
# Query the PACS for information on a PatientID                               #
###############################################################################
# ... and for extra kicks, if you have done a
#
#               pip install pypx
#
# you can pipe the output of the REST call to a report module, px-report
# and get nicely formatted console reports
query () {
curl -s -X 'POST'                                                             \
  "$PFDCMURL/api/v1/PACS/sync/pypx/"                                          \
  -H 'accept: application/json'                                               \
  -H 'Content-Type: application/json'                                         \
  -d '{
  "PACSservice": {
    "value": "'$PACSNAME'"
  },
  "listenerService": {
    "value": "default"
  },
  "PACSdirective": {
    "PatientID": "'$MRN'",
    "withFeedBack": false,
    "then": "",
    "thenArgs": "",
    "dblogbasepath": "'$DB'",
    "json_response": true
  }
}'| jq '.pypx' |\
 px-report      --colorize dark                                             \
                --printReport csv                                           \
                --csvPrettify                                               \
                --csvPrintHeaders                                           \
                --reportHeaderStudyTags PatientName,PatientID,StudyDate     \
                --reportBodySeriesTags SeriesDescription,SeriesInstanceUID
}

# If you have a specific SeriesInstanceUID and StudyInstanceUID, you can
export STUDYINSTANCEUID=1.2.840.113845.11.1000000001785349915.20160826183157.8128736
export SERIESINSTANCEUID=1.3.12.2.1107.5.2.19.45152.2013031212563759711672676.0.0.0

query_single () {
curl -s -X 'POST'                                                             \
  "$PFDCMURL/api/v1/PACS/sync/pypx/"                                          \
  -H 'accept: application/json'                                               \
  -H 'Content-Type: application/json'                                         \
  -d '{
  "PACSservice": {
    "value": "'$PACSNAME'"
  },
  "listenerService": {
    "value": "default"
  },
  "PACSdirective": {
    "PatientID": "'$MRN'",
    "StudyInstanceUID": "'$STUDYINSTANCEUID'",
    "SeriesInstanceUID": "'$SERIESINSTANCEUID'",
    "withFeedBack": false,
    "then": "",
    "thenArgs": "",
    "dblogbasepath": "'$DB'",
    "json_response": true
  }
}'| jq '.pypx' |\
 px-report      --colorize dark                                             \
                --printReport csv                                           \
                --csvPrettify                                               \
                --csvPrintHeaders                                           \
                --reportHeaderStudyTags PatientName,PatientID,StudyDate     \
                --reportBodySeriesTags SeriesDescription,SeriesInstanceUID
}

###############################################################################
#_____________________________________________________________________________#
# R E T R I E V E                                                             #
#_____________________________________________________________________________#
###############################################################################
# Retrieve PatientID images from the PACS                                     #
###############################################################################
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
#
# NB!
#
# o For orthanc, make SURE that the orthanc instance is configured for this
#   listener IP address!
#
# o Some other PACS might need a StudyInstanceUID in addition to the
#   SeriesInstanceUID (for e.g. a FUJI PACS).

retrieve_single () {
curl -s -X 'POST'                                                             \
  "$PFDCMURL/api/v1/PACS/thread/pypx/"                                        \
  -H 'accept: application/json'                                               \
  -H 'Content-Type: application/json'                                         \
  -d '{
  "PACSservice": {
    "value": "'$PACSNAME'"
  },
  "listenerService": {
    "value": "default"
  },
  "PACSdirective": {
    "SeriesInstanceUID": "'$SERIESUID'",
    "withFeedBack": true,
    "then": "retrieve",
    "thenArgs": "",
    "dblogbasepath": "'$DB'",
    "json_response": true
  }
}' | jq
}

retrieve () {
# What the heck, let's just retrieve all the info for this ID... This def
# works!
curl -s -X 'POST'                                                           \
  "$PFDCMURL/api/v1/PACS/thread/pypx/"                                      \
  -H 'accept: application/json'                                             \
  -H 'Content-Type: application/json'                                       \
  -d '{
  "PACSservice": {
    "value": "'$PACSNAME'"
  },
  "listenerService": {
    "value": "default"
  },
  "PACSdirective": {
    "PatientID": "'$MRN'",
    "withFeedBack": false,
    "then": "retrieve",
    "thenArgs": "",
    "dblogbasepath": "'$DB'",
    "json_response": true
  }
}' | jq
}

###############################################################################
#_____________________________________________________________________________#
# S T A T U S                                                                 #
#_____________________________________________________________________________#
###############################################################################
# Retrieve status information for images pulled from the PACS                 #
###############################################################################

satus_raw () {
# Request the STATUS
# ... raw JSON response!
curl -s -X 'POST'                                                             \
  "$PFDCMURL/api/v1/PACS/sync/pypx/"                                          \
  -H 'accept: application/json'                                               \
  -H 'Content-Type: application/json'                                         \
  -d '{
  "PACSservice": {
    "value": "'$PACSNAME'"
  },
  "listenerService": {
    "value": "default"
  },
  "PACSdirective": {
    "PatientID": "'$MRN'",
    "withFeedBack": false,
    "then": "status",
    "thenArgs": "",
    "dblogbasepath": "'$DB'",
    "json_response": true
  }
}' | jq
}

status_console () {
# Request the STATUS
# ... with a slightly more human friendly formatted reply
curl -s -X 'POST'                                                             \
  "$PFDCMURL/api/v1/PACS/sync/pypx/"                                          \
  -H 'accept: application/json'                                               \
  -H 'Content-Type: application/json'                                         \
  -d '{
  "PACSservice": {
    "value": "'$PACSNAME'"
  },
  "listenerService": {
    "value": "default"
  },
  "PACSdirective": {
    "PatientID": "'$MRN'",
    "withFeedBack": false,
    "then": "status",
    "thenArgs": "",
    "dblogbasepath": "'$DB'",
    "json_response": true
  }
}' | jq '.pypx' |\
px-report       --seriesSpecial seriesStatus                                   \
                --printReport tabular                                          \
                --colorize dark                                                \
                --reportBodySeriesTags seriesStatus
}

###############################################################################
#_____________________________________________________________________________#
# P U S H                                                                     #
#_____________________________________________________________________________#
###############################################################################
# Push images that have been retrieved to the local FS to                     #
# CUBE swift storage                                                          #
###############################################################################
#
# If you're following along and have executed a retrieve, the images pertinent
# to the directive search space will exist within the pfdcm container. If you
# ran the container with appropriate volume mapping, then files should be
# accessible in your host.
#
# The next step is to PUSH these local FS files to CUBE swift storage. Within
# the swift storage, objects are named in a fashion that mimics a file system
# directory structure:
#
#                      SERVICES/PACS/$SWIFTSERVICEPACS
#

push_single () {
# Push just a single series...
curl -s -X 'POST'                                                           \
  "$PFDCMURL/api/v1/PACS/thread/pypx/"                                      \
  -H 'accept: application/json'                                             \
  -H 'Content-Type: application/json'                                       \
  -d '{
  "PACSservice": {
    "value": "'$PACSNAME'"
  },
  "listenerService": {
    "value": "default"
  },
  "PACSdirective": {
    "SeriesInstanceUID": "'$SERIESUID'",
    "withFeedBack": false,
    "then": "push",
    "thenArgs": "{\"db\": \"'$DB'\", \"swift\": \"'$SWIFTKEY'\", \"swiftServicesPACS\": \"'$SWIFTSERVICEPACS'\", \"swiftPackEachDICOM\":   true}",
    "dblogbasepath": "'$DB'",
    "json_response": true
  }
}' | jq
}

push () {
# Push everything for a PatientID...
curl -s -X 'POST'                                                           \
  "$PFDCMURL/api/v1/PACS/thread/pypx/"                                      \
  -H 'accept: application/json'                                             \
  -H 'Content-Type: application/json'                                       \
  -d '{
  "PACSservice": {
    "value": "'$PACSNAME'"
  },
  "listenerService": {
    "value": "default"
  },
  "PACSdirective": {
    "PatientID": "'$MRN'",
    "withFeedBack": false,
    "then": "push",
    "thenArgs": "{\"db\": \"'$DB'\", \"swift\": \"'$SWIFTKEY'\", \"swiftServicesPACS\": \"'$SWIFTSERVICEPACS'\", \"swiftPackEachDICOM\":   true}",
    "dblogbasepath": "'$DB'",
    "json_response": true
  }
}' | jq
}

###############################################################################
#_____________________________________________________________________________#
# R E G I S T E R                                                             #
#_____________________________________________________________________________#
###############################################################################
# Register images that are in swift storage to a CUBE database                #
###############################################################################
#
# Now, assuming all has gone well, the final step is to register the files
# in CUBE swift storage to CUBE itself...

register () {
curl -s -X 'POST' \
  "$PFDCMURL/api/v1/PACS/thread/pypx/"                                      \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "PACSservice": {
    "value": "'$PACSNAME'"
  },
  "listenerService": {
    "value": "default"
  },
  "PACSdirective": {
    "SeriesInstanceUID": "'$SERIESUID'",
    "withFeedBack": false,
    "then": "register",
    "thenArgs": "{\"db\": \"'$DB'\", \"CUBE\": \"'$CUBEKEY'\", \"swiftServicesPACS\": \"'$SWIFTSERVICEPACS'\", \"parseAllFilesWithSubStr\":   \"dcm\"}",
    "dblogbasepath": "/home/dicom/log",
    "json_response": true
  }
}' | jq
}

# Remember to check on the registration progress using a STATUS call.

#
# And we're done! If all went well, the DICOM files from PACS will now be
# accessible to CUBE.
#
# _-30-_
#