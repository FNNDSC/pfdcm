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
}'

# Config ORTHANC PACS
curl -X 'PUT' \
  'http://localhost:4005/api/v1/PACSservice/orthanc' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "info": {
    "aet": "ORTHANC",
    "aet_listener": "ORTHANC",
    "aec": "CHRISLOCAL",
    "serverIP": "192.168.1.189",
    "serverPort": "4242"
  }
}'


