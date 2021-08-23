#!/bin/bash
#
#       A simple, dumb, hardcoded script to initialize some pfdcm
#       innards. Obviously this should at some future juncture be
#       a grown up script without hardcoded everything... :-)
#


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

#
# _-30-_
#

