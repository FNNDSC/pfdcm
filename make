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

   ESC(){ echo -en "\033";}                            # escape character
 CLEAR(){ echo -en "\033c";}                           # the same as 'tput clear'
 CIVIS(){ echo -en "\033[?25l";}                       # the same as 'tput civis'
 CNORM(){ echo -en "\033[?12l\033[?25h";}              # the same as 'tput cnorm'
  TPUT(){ echo -en "\033[${1};${2}H";}                 # the same as 'tput cup'
COLPUT(){ echo -en "\033[${1}G";}                      # put text in the same line as the specified column
  MARK(){ echo -en "\033[7m";}                         # the same as 'tput smso'
UNMARK(){ echo -en "\033[27m";}                        # the same as 'tput rmso'
  DRAW(){ echo -en "\033%";echo -en "\033(0";}        # switch to 'garbage' mode
 WRITE(){ echo -en "\033(B";}                          # return to normal mode from 'garbage' on the screen
  BLUE(){ echo -en "\033c\033[0;1m\033[37;44m\033[J";} # reset screen, set background to blue and font to white

# Foreground
RED='\033[0;31m'
NC='\033[m' # No Color
Black='\033[0;30m'     
DarkGray='\033[1;30m'
Red='\033[0;31m'     
LightRed='\033[1;31m'
Green='\033[0;32m'     
LightGreen='\033[1;32m'
Brown='\033[0;33m'     
Yellow='\033[1;33m'
Blue='\033[0;34m'     
LightBlue='\033[1;34m'
Purple='\033[0;35m'     
LightPurple='\033[1;35m'
Cyan='\033[0;36m'     
LightCyan='\033[1;36m'
LightGray='\033[0;37m'     
White='\033[1;37m'

# Background
NC='\033[m' # No Color
BlackBG='\033[0;40m'     
DarkGrayBG='\033[1;40m'
RedBG='\033[0;41m'     
LightRedBG='\033[1;41m'
GreenBG='\033[0;42m'     
LightGreenBG='\033[1;42m'
BrownBG='\033[0;43m'     
YellowBG='\033[1;43m'
BlueBG='\033[0;44m'     
LightBlueBG='\033[1;44m'
PurpleBG='\033[0;45m'     
LightPurpleBG='\033[1;45m'
CyanBG='\033[0;46m'     
LightCyanBG='\033[1;46m'
LightGrayBG='\033[0;47m'     
WhiteBG='\033[1;47m'


declare -i STEP=0
declare -i b_restart=0
declare -i b_host=0
RESTART=""
HERE=$(pwd)
echo "Starting script in dir $HERE"
CREPO=local
if (( $# == 1 )) ; then
    CREPO=$1
fi
export CREPO=$CREPO

declare -a A_CONTAINER=(
    "pfdcm"
)

function title {
    declare -i b_date=0
    local OPTIND
    while getopts "d:" opt; do
        case $opt in 
            d) b_date=$OPTARG ;;
        esac
    done
    shift $(($OPTIND - 1))

    STEP=$(expr $STEP + 1 )
    MSG="$1"
    MSG2="$2"
    TITLE=$(echo " $STEP.0: $MSG ")
    LEN=$(echo "$TITLE" | awk -F\| {'printf("%s", length($1));'})
    if ! (( LEN % 2 )) ; then
        TITLE="$TITLE "
    fi
    MSG=$(echo -e "$TITLE" | awk -F\| {'printf("%*s%*s\n", 39+length($1)/2, $1, 40-length($1)/2, "");'})
    if (( ${#MSG2} )) ; then
        TITLE2=$(echo " $MSG2 ")
        LEN2=$(echo "$TITLE2" | awk -F\| {'printf("%s", length($1));'})
        MSG2=$(echo -e "$TITLE2" | awk -F\| {'printf("%*s%*s\n", 39+length($1)/2, $1, 40-length($1)/2, "");'})
    fi
    printf "\n"
    DATE=$(date)
    DRAW
    if (( b_date )) ; then
        printf "${LightBlue}lqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqk\nx"
        WRITE
        printf "%-30s" "$DATE"
        DRAW 
        printf "x\n"
        printf "${Yellow}tqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqvqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqk\n"
    else
        printf "${Yellow}lqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqk\n"
    fi
    printf "x"
    WRITE
    printf "${LightPurple}$MSG${Yellow}"
    if (( ${#MSG2} )) ; then
        DRAW
        printf "x\nx"
        WRITE
        printf "${LightPurple}$MSG2${Yellow}"
    fi
    DRAW
    printf "x\n"
    printf "${Yellow}tqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqu\n"
    WRITE
    printf "${NC}"
}

function windowBottom {
    # printf "a b c d f e f g h i j k l m n o p q r s t u v w x y z]\n"
    DRAW
    # printf "a b c d f e f g h i j k l m n o p q r s t u v w x y z]\n"
    printf "${Yellow}"
    printf "mwqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqv${Brown}qk\n"
    # printf "mqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqj\n"
    printf "${Brown}"
    printf " mqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqj\n"
    WRITE
    printf "${NC}"
}

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
