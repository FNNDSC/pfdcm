#!/bin/bash
#
# NAME
#
#   make
#
# SYNPOSIS
#
#   make [-h <IP>]
#
# DESC
# 
#   'make' is the main entry point for instantiating an FNNDSC pfdcm
#   container.
#
#

source ./decorate.sh 
declare -i STEP=0
declare -i b_restart=0
declare -i b_host=0
RESTART=""
HERE=$(pwd)
echo "Starting script in dir $HERE"

CREPO=fnndsc
if (( $# == 1 )) ; then
    CREPO=$1
fi
export CREPO=$CREPO
export TAG=

declare -a A_CONTAINER=(
    "pfdcm"
)

if [[ -f .env ]] ; then
    source .env 
fi

while getopts "r:h:" opt; do
    case $opt in 
        r) b_restart=1
           RESTART=$OPTARG      ;;
        h) b_host=1
           LISTENER=$OPTARG     ;;
    esac
done
shift $(($OPTIND - 1))

title -d 1 "Using <$CREPO> containers..."
if [[ $CREPO == "fnndsc" ]] ; then
    echo "Pulling latest version of all containers..."
    for CONTAINER in ${A_CONTAINER[@]} ; do
        echo ""
        CMD="docker pull ${CREPO}/$CONTAINER"
        echo -e "\t\t\t${White}$CMD${NC}"
        echo $sep
        echo $CMD | sh
        echo $sep
    done
fi
windowBottom

if (( b_restart )) ; then
    docker-compose stop ${RESTART}_service && docker compose rm -f ${RESTART}_service
    docker-compose run --service-ports ${RESTART}_service
else
    title -d 1 "Will use following container(s):"
    for CONTAINER in ${A_CONTAINER[@]} ; do
        if [[ $CONTAINER != "chris_dev_backend" ]] ; then
            CMD="docker run ${CREPO}/$CONTAINER --version"
            printf "${White}%30s\t\t" "${CREPO}/$CONTAINER"
            Ver=$(echo $CMD | sh | grep Version)
            echo -e "$Green$Ver"
        fi
    done
    windowBottom

    title -d 1 "Shutting down any running pfdcm containers... "
    docker-compose stop
    docker-compose rm -vf
    for CONTAINER in ${A_CONTAINER[@]} ; do
        printf "%30s" "$CONTAINER"
        docker ps -a                                                        |\
            grep $CONTAINER                                                 |\
            awk '{printf("docker stop %s && docker rm -vf %s\n", $1, $1);}' |\
            sh >/dev/null
        printf "${Green}%20s${NC}\n" "done"
    done
    windowBottom

    title -d 1 "Starting pfdcm using " " ./docker-compose.yml"
    # export HOST_IP=$(ip route | grep -v docker | awk '{if(NF==11) print $9}')
    # echo "Exporting HOST_IP=$HOST_IP as environment var..."
    echo "docker-compose up" | sh -v
    windowBottom
fi
