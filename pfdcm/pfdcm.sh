#!/bin/bash
#

SYNOPSIS='
    NAME

        pfdcm.sh

    SYNOPSIS

        pfdcm.sh        [-S|--saveToJSON <file>] [-I|--profile <file>]          \
                        [-u|--useDefaults]                                      \
                        [--no-proxy]                                            \
                        [-q] [-s] [-r] [-p] [-g]                                \
                        [--query] [--status] [--retrieve] [--push] [--register] \
                        [-j] [--json]                                           \
                        [-L|--listener <listenerToUse>]                         \
                        [--listenerSetupGet <listenerToUse>]                    \
                        [-T|--reportType <reportType>]                          \
                        [-C|--csvCLI <csvCLI>]                                  \
                        [-H|--reportHeaderTags <reportHeaderTags]               \
                        [-B|--reportBodyTags <reportBodyTags>]                  \
                        [-v|--verbosity <verbosity>]                            \
                        [-K|--multikey <dicomKey>]                              \
                        [-P|--profile <profileToUse>]                           \
                        [--pfdcmSwift <swiftKeyName>]                           \
                        [--pfdcmCUBE <CUBEKeyName>]                             \
                        [--pfdcmPACS <PACSKeyName]                              \
                        [--pfdcm <pfdcmKeyName>]                                \
                        [--PACSSetupShow]                                       \
                        [--cubeSetupShow]                                       \
                        [--swiftSetupShow]                                      \
                        [--pfdcmSetupShow]                                      \
                        #
                        # The following are only for setup:
                        # These are typically once-off and only for initial-
                        # ization typically by an admin
                        # YOU WILL PROBABLY NEVER USE THESE!!
                        #
                        [--serviceRoot <rootDirForServiceFiles>]                \
                        [-U|--URL] <pfdcmURL>                                   \
                        [-i] [--initServices]                                   \
                        # Define swift access
                        [--swiftSetupDo]                                        \
                        [--swiftSetupGet <swiftKeyName>]                        \
                        [--swiftKeyName <swiftKeyName]                          \
                        [--swiftIP <ip>]                                        \
                        [--swiftPort <port>]                                    \
                        [--swiftLogin <login>]                                  \
                        # Define CUBE access
                        [--cubeSetupDo]                                         \
                        [--cubeSetupGet <cubeKeyName>]                          \
                        [--cubeKeyName <cubeKeyName]                            \
                        [--cubeURL <url>]                                       \
                        [--cubeUserName <user>]                                 \
                        [--cubeUserPassword <password>]                         \
                        [--cubePACSservice <cubePACSservice>]                   \
                        # Define PACS access
                        [--PACSSetupDo]                                         \
                        [--PACSSetupGet <PACStoUse>]                            \
                        [-P|--PACS <PACStoUse>]                                 \
                        [--aet <AET>]                                           \
                        [--aetl <AET_listener>]                                 \
                        [--aec <AEC>]                                           \
                        [--serverIP <ip>]                                       \
                        [--serverPort <port>]                                   \
                        #
                        # End init
                        #
                        # You will most definitely use the tag expr below:

                        <TAG1a:Value1a,TAG2a:Value2a;TAG1b:Value1b;...>

    DESC

        A simple exemplar script that demonstrates how to setup the
        pfdcm infrastructure, and run/execute a *full* PACS Q/R
        with resultant images registered to a CUBE instance.

    ARGS

        [-S|--saveToJSON <file>] [-I|--profile <file>]
        Save all relevant internal variables to <file>.
        Initialize all relevant internal varibles from <file>. Note that
        by default, a file called "defaults.json" is parsed if it exists.

        [-u|--useDefaults|-d]
        If passed, read from defaults.json if it exists.

        [--pfdcmSwift <swiftKeyName>]
        [--pfdcmCUBE <CUBEKeyName>]
        [--pfdcmPACS <PACSKeyName]
        [--pfdcm <pfdcmKeyName>]
        [--pfdcmSetupShow]
        These define "key names", typically within a running pfdcm instance,
        to query for details on Swift, CUBE, PACS, and pfdcm itself. If pfdcm
        is already running, then there is no need to read from a setup file.
        The application can be told to use/consult its own internal state
        to resolve these. In this manner it is quite possible to have a single
        shell script pfdcm.sh be able to interact with multiple accessible
        services.

        The --pfdcmSetupShow will simply display the pfdcm.json setup file.

        <TAG1a:Value1a,TAG2a:Value2a,...;TAG1b:Value1b;...>
        A colon separated expression of groups. Each group defines a Query
        expression to pass to `pfdcm`, for example:

                "PatientID:123456,StudyDate:20200101;AccessionNumber:12345678"

        will perform two passes. In the first pass, the Query will be for:

        {
                "PatientID": "123456",
                "StudyDate": "20200101"
        }

        and in the second pass, the Query will be:

        {
                "AccessionNumber":  "12345678"
        }

        [-K <dicomKey>]
        An alternate mechanism for specifying a single <TAG>:<VALUE>, useful
        particularly for multiple pass operations.

        if, for example, the following is passed:

                "-K PatientID -- 1234567;4322547;5432645"

        then the <dicomKey> is repeatedly applied to each of the group
        arguments. This is a shorthand alternative to

            "PatientID:1234567;PatientID:4322537;PatientID:5432645"

        Note this is ONLY useful for cases when the group expression
        only has one DICOMtag of interest.

        SIDE EFFECT! To see *all* the data in a PACS, do

                            -K ":"  -- "all"

        or, alternatively, without the "-K"

                            -- ":all"

        THIS IS NOT RECOMMENDED IN PRODUCTION ENVIRONMENTS :-)

        [--serviceRoot <rootDirForServiceFiles>]
        The root directory of the service files. Default: /home/dicom

        [-U|--URL] <pfdcmURL>
        The URL of the pfdcm service. Typically "http://localhost:4005"

        [-i] [--initServices]
        If specified, restart the xinetd listener in pfdcm and set the PACS
        details.

        [-q] [--query]
        Call a foreground FIND on each passed QUERY group.

        [-r] [--retrieve]
        Call a backgrounded RETRIEVE on each passed QUERY group.

        [-p] [--push]
        Call a backgrounded PUSH on each passed QUERY group.

        [-g] [--register]
        Call a backgrounded REGISTER on each passed QUERY group.

        [-s] [--status]
        Call a STATUS on each passed QUERY group. This is a foreground
        operation.

        [-j] [--json]
        If specified, show the raw JSON return of any specified operation.

        [-T <reportType>]
        The report type to generate. One of "tabular", "rawText", "csv".

        [-C <csvCLI>]
        Special CLI flags for the csv report override.

        [-H <reportHeaderTags]
        Report header tag override list.

        [-B <reportBodyTags>]
        Report query body tag override list.

        [-v <verbosity>]
        Set the verbosity. A postive value will display some additional info.

        [-L|--listener <listenerToUse>]
        The `pfdcm` listener to use. Note, this will almost always be
        "default".

        [--listenerSetupGet <listenerKeyName>]
        Get information on the listener key <listenerKeyName>.

        [--swiftSetupDo] [--swiftSetupGet <swiftKeyName>] [--swiftSetupShow]
        [--swiftKeyName <swiftKeyName]
        [--swiftIP <ip>]
        [--swiftPort <port>]
        [--swiftLogin <login>]
        Using the "--swiftSetupDo" and appropriately set variables, define the
        details of swift storage for `pfdcm` to access with <swiftKeyName>.
        The --swiftSetupShow will show a list of all swift keys.

        [--cubeSetupDo] [--cubeSetupGet <cubeKeyName>] [--cubeSetupShow]
        [--cubeKeyName <cubeKeyName]
        [--cubeURL <url>]
        [--cubeUserName <user>]
        [--cubeUserPassword <password>]
        [--cubePACSservice <cubePACSservice>]
        Using the "--cubeSetupDo" and appropriately set variables, define the
        details of the CUBE instance for `pfdcm` to access with <cubeKeyName>.
        The --cubeSetupShow will show a list of all cube keys.

        [--PACSsetupDo] [--PACSSetupGet <PACStoUse>] [--PACSSetupShow]
        [-P|--PACS <PACStoUse>]
        [--aet <AET>]
        [--aetl <AET_listener>]
        [--aec <AEC>]
        [--serverIP <ip>]
        [--serverPort <port>]
        Using the "--PACSSetupDo" and appropriately set variables, define the
        details of the PACSserver for `pfdcm` to access via <PACStoUse>.
        The --PACSSetupShow will show a list of all PACS keys.

    EXAMPLES:

    * Setup and save
    pfdcm.sh    --saveToJSON defaults.json                                     \
                --URL http://localhost:4005                                    \
                --swiftKeyName local                                           \
                    --swiftIP 192.168.1.216                                    \
                    --swiftPort 8080                                           \
                    --swiftLogin chris:chris1234                               \
                --PACS orthanc                                                 \
                    --aet CHRISLOCAL                                           \
                    --aetl ORTHANC                                             \
                    --aec ORTHANC                                              \
                    --serverIP 192.168.1.189                                   \
                    --serverPort 4242                                          \
                --cubeKeyName local                                            \
                    --cubeURL http://192.168.1.216:8000/api/v1/                \
                    --cubeUserName chris                                       \
                    --cubePACSservice newPACS                                  \
                    --cubeUserPassword chris1234 --

    * Initialize from saved JSON setup
    pfdcm.sh --profile pfdcm.sh.json --

    * Initialize from defaults.json and restart services (the restart
    * is not needed for k8 deployments)
    pfdcm.sh -u -i --

    * Ask pfdcm for info on services:
    * NOTE: do not pass a "-u" since this might override CLI values.
    ** the listener
    pfdcm.sh --listenerSetupGet default  --
    ** the swift key "megalodon"
    pfdcm.sh --swiftSetupGet megalodon --
    ** the CUBE key "megalodon"
    pfdcm.sh --cubeSetupGet megalodon --
    ** the PACS service "orthanc"
    pfdcm.sh --PACSSetupGet orthanc --

    * Read defaults and set...
    ** swift info (key read from defaults.json)
    pfdcm.sh -u --swiftSetupDo  --
    ** CUBE (key read from defaults.json)
    pfdcm.sh -u --cubeSetupDo --
    ** the PACS service (key read from defaults.json)
    pfdcm.sh -u --PACSSetupDo --

    * Query MRNs on the PACS
    pfdcm.sh -u --query -- "PatientID:LILLA-9729"
                        - or -
    pfdcm.sh -u --query -K PatientID -- "LILLA-9729"
                        - or -
    pfdcm.sh -u --query -K PatientID -- "LILLA-9729;LILLA-9730;LILLA-9731"
                        - or -
    pfdcm.sh --pfdcmPACS PACSDCM --query -- "PatientID:LILLA-9729"

    * Status on MRNs in pfdcm
    pfdcm.sh -u --status -- "PatientID:LILLA-9729"
                         - or -
    pfdcm.sh -u --status -K PatientID -- "LILLA-9729"
                        - or -
    pfdcm.sh -u --status -K PatientID -- "LILLA-9729;LILLA-9730;LILLA-9731"
                        - or -
    pfdcm.sh --pfdcmPACS PACSDCM --status -- "PatientID:LILLA-9729"

    * Push MRNs to ChRIS swift storage
    pfdcm.sh -u --push -- "PatientID:LILLA-9729"
                        - or -
    pfdcm.sh -u --push -K PatientID -- "LILLA-9729"
                        - or -
    pfdcm.sh -u --push -K PatientID -- "LILLA-9729;LILLA-9730;LILLA-9731"
                        - or -
    pfdcm.sh --pfdcmPACS PACSDCM --push -- "PatientID:LILLA-9729"

    * Regsiter MRNs to ChRIS CUBE
    pfdcm.sh -u --register -- "PatientID:LILLA-9729"
                        - or -
    pfdcm.sh -u --register -K PatientID -- "LILLA-9729"
                        - or -
    pfdcm.sh -u --register -K PatientID -- "LILLA-9729;LILLA-9730;LILLA-9731"
                        - or -
    pfdcm.sh --pfdcmPACS PACSDCM --push -- "PatientID:LILLA-9729"

'

declare -i b_initDo=0
declare -i b_queryDo=0
declare -i b_retrieveDo=0
declare -i b_pushDo=0
declare -i b_registerDo=0
declare -i b_statuDos=0
declare -i b_JSONreport=0
declare -i b_showJSONsettings=0

declare -i b_saveToJSON=0
declare -i b_initFromJSON=0
declare -i b_noproxy=0

declare -i VERBOSITY=0

REPORTTYPE=tabular
LISTENER=default
CSVCLI="--csvPrettify --csvPrintHeaders"
REPORTHEADERTAGS=""
REPORTBODYTAGS=""
DICOMKEY=""
URL=http://localhost:4005

JSONFILE=defaults.json
declare -i b_listenerSetupGet=0

declare -i b_setupSwiftDo=0
declare -i b_setupSwiftGet=0
SWIFTKEYNAME=""
SWIFTIP=""
SWIFTPORT=""
SWIFTLOGIN=""

declare -i b_setupCUBEdo=0
declare -i b_setupCubeGet=0
CUBEKEYNAME=""
CUBEUSERNAME=""
CUBEUSERPASSWORD=""
CUBEPACSSERVICE=""

declare -i b_setupPACSDo=0
declare -i b_setupPACSGet=0
PACS=""
AET=""
AETL=""
AEC=""
PACSSERVERIP=""
PACSSERVERPORT=""

declare -i b_pfdcmSetupShow=0
declare -i b_PACSSetupShow=0
declare -i b_cubeSetupShow=0
declare -i b_swiftSetupShow=0
declare -i b_pfdcmSWIFT=0
declare -i b_pfdcmPACS=0
declare -i b_pfdcmCUBE=0
declare -i b_pfdcm=0
PFDCMSWIFT=local
PFDCMPACS=orthanc
PFDCMCUBE=local
PFDCM=local

DBROOT=/home/dicom

declare -i b_showSearch=0

# PRECONDITIONS
# o A pull on the current `pfdcm`
# o Building the docker image, and executing with
EXECpfdcm="
#
# If you'd like to debug, vol map the source into the container
#
# Please don't blindly copy-paste this command unless you know
# what it all does!
#
docker run --rm -it -d --name pfdcm                                 \\
        -p 4005:4005 -p 5555:5555 -p 10502:10502 -p 11113:11113     \\
        -v $DBROOT:$DBROOT  \\
        -v $PWD/pfdcm:/app:ro \\
        local/pfdcm /start-reload.sh
"

while :; do
    case $1 in
        -h|-\?|-x|--help)
            printf "%s" "$SYNOPSIS"
            exit 1                                          ;;
        --no-proxy)             b_noproxy=1                 ;;
        -i|--initServices)      b_initDo=1                  ;;
        -u|-d|--useDefaults)    b_useDefaults=1
                                b_initFromJSON=1            ;;
        -Q)                     b_showSearch=1              ;;
        -q|--query)             b_queryDo=1                 ;;
        -r|--retrieve)          b_retrieveDo=1              ;;
        -p|--push)              b_pushDo=1                  ;;
        -g|--register)          b_registerDo=1              ;;
        -s|--status)            b_statusDo=1                ;;
        -j|--json)              b_JSONreport=1              ;;
        -K|--multikey)          DICOMKEY=$2                 ;;
        -L|--listener)          LISTENER=$2                 ;;
        --listenerSetupGet)     LISTENER=$2
                                b_listenerSetupGet=1        ;;
        -T|--reportType)        REPORTTYPE=$2               ;;
        -C|--csvCLI)            CSVCLI=$2                   ;;
        -H|--reportHeaderTags)  REPORTHEADERTAGS=$2         ;;
        -B|--reportBodyTags)    REPORTBODYTAGS=$2           ;;
        -U|--URL)               URL=$2                      ;;
        -v|--verbosity)         VERBOSITY=$2                ;;
        -S|--saveToJSON)        b_saveToJSON=1
                                JSONFILE=$2                 ;;
        -I|--profile)           b_initFromJSON=1
                                JSONFILE=$2                 ;;
        --pfdcmSWIFT)           b_pfdcmSWIFT=1
                                PFDCMSWIFT=$2               ;;
        --serviceRoot)          DBROOT=$2                   ;;
        --swiftSetupDo)         b_setupSwiftDo=1            ;;
        --swiftSetupShow)       b_swiftSetupShow=1          ;;
        --swiftSetupGet)        b_setupSwiftGet=1
                                PFDCMSWIFT=$2               ;;
        --swiftKeyName)         SWIFTKEYNAME=$2             ;;
        --swiftIP)              SWIFTIP=$2                  ;;
        --swiftPort)            SWIFTPORT=$2                ;;
        --swiftLogin)           SWIFTLOGIN=$2               ;;
        --pfdcmCUBE)            b_pfdcmCUBE=1
                                PFDCMCUBE=$2                ;;
        --cubeSetupDo)          b_setupCUBEdo=1             ;;
        --cubeSetupShow)        b_cubeSetupShow=1           ;;
        --cubeSetupGet)         b_setupCubeGet=1
                                PFDCMCUBE=$2                ;;
        --cubeKeyName)          CUBEKEYNAME=$2              ;;
        --cubeURL)              CUBEURL=$2                  ;;
        --cubeUserName)         CUBEUSERNAME=$2             ;;
        --cubeUserPassword)     CUBEUSERPASSWORD=$2         ;;
        --cubePACSservice)      CUBEPACSSERVICE=$2          ;;
        -P|--PACS)              PACS=$2                     ;;
        --pfdcmPACS)            b_pfdcmPACS=1
                                PFDCMPACS=$2                ;;
        --PACSSetupDo)          b_setupPACSDo=1             ;;
        --PACSSetupShow)        b_PACSSetupShow=1           ;;
        --PACSSetupGet)         b_setupPACSGet=1
                                PACS=$2                     ;;
        --aet)                  AET=$2                      ;;
        --aetl)                 AETL=$2                     ;;
        --aec)                  AEC=$2                      ;;
        --serverIP)             PACSSERVERIP=$2             ;;
        --serverPort)           PACSSERVERPORT=$2           ;;
        --pfdcm)                b_pfdcm=1
                                PFDCM=$2                    ;;
        --pfdcmSetupShow)       b_pfdcmSetupShow=1          ;;
        --) # End of all options
            shift
            break                                           ;;
    esac
    shift
done
listEXPR=$*

PFDCMJSON=${DBROOT}/services/pfdcm.json
if (( b_useDefaults )) ; then
    JSONFILE=defaults.json
fi

if (( b_JSONreturn )) ; then
        JSON=true
else
        JSON=false
fi

function vprint {
        MESSAGE=$1
        FILTER=$2
        if (( VERBOSITY > 0 )) ; then
            if (( ${#FILTER} )) ; then
                echo "$MESSAGE" | jq
            else
                echo "$MESSAGE"
            fi
        fi
}

function reportify {
    BODYTAGOVERRIDE=$1
    if (( ${#BODYTAGOVERRIDE} )) ; then
        if (( ${#REPORTBODYTAGS} )) ; then
            REPORTBODYTAGS="$REPORTBODYTAGS,$BODYTAGOVERRIDE"
        else
            REPORTBODYTAGS="$BODYTAGOVERRIDE"
        fi
    fi
    REPORT="px-report   --colorize dark \
                        --printReport $REPORTTYPE \
                        $CSVCLI"
    if [[ $REPORTTYPE == "csv" ]] ; then
        if (( ! ${#REPORTHEADERTAGS} )) ; then
            REPORTHEADERTAGS="PatientName,PatientID,StudyDate"
        fi
    fi
    if (( ${#REPORTHEADERTAGS} )) ; then
        REPORT="$REPORT --reportHeaderStudyTags $REPORTHEADERTAGS"
    fi
    if (( ${#REPORTBODYTAGS} )) ; then
        REPORT="$REPORT --reportBodySeriesTags $REPORTBODYTAGS"
    fi
    if (( b_JSONreport )) ; then
        REPORT="jq"
    fi
    echo $REPORT
}

function preamble {
    JSON=$(jo -p PACSservice=$(jo value=$PACS) listenerService=$(jo value=$LISTENER))
    echo $JSON
}

function curlH {
    echo "-H 'accept: application/json' -H 'Content-Type: application/json'"
}

function curlPOST {
    execType=$1
    JSON="$2"
    echo "curl -s -X 'POST' ${URL}/api/v1/PACS/${execType}/pypx/ $(curlH) -d '$JSON'"
}

function CURL {
    VERB=$1
    ROUTE=$2
    JSON="$3"
    NOPROXY=""
    if (( b_noproxy )) ; then
        NOPROXY="env http_proxy='' "
    fi
    if (( ${#JSON} )) ; then
        echo "$NOPROXY curl -s -X $VERB ${URL}/api/v1/$ROUTE $(curlH) -d '$JSON'"
    else
        echo "$NOPROXY curl -s -X $VERB ${URL}/api/v1/$ROUTE $(curlH)"
    fi
}

function evaljq {
    CMD=$1
    eval "$CMD" | jq
    if (( $? )) ; then
        MSG1="An error in parsing the command was detected!"
        MSG2="Is the pfdcm container running?\n$EXECpfdcm\n"
        MSG3="Alternatively, try the command again, this time using '--no-proxy'"
        if [[ -e $(which tput) ]] ; then
            tput setaf 1; echo "$MSG1"
            echo ""
            tput setaf 2; echo -e "$MSG2\n$MSG3"
            exit 1
        else
            echo "$MSG1"
            echo ""
            echo -e "$MSG2\n$MSG3"
        fi
    fi
}

#
# If specified, read various settings from the profile JSON
#
if (( b_initFromJSON )) ; then
    vprint "Reading from $JSONFILE..."
    SWIFTKEYNAME=$(     jq '.swift.info.swiftKeyName.value'     $JSONFILE | tr -d '"')
    SWIFTIP=$(          jq '.swift.info.swiftInfo.ip'           $JSONFILE | tr -d '"')
    SWIFTPORT=$(        jq '.swift.info.swiftInfo.port'         $JSONFILE | tr -d '"')
    SWIFTLOGIN=$(       jq '.swift.info.swiftInfo.login'        $JSONFILE | tr -d '"')
    CUBEKEYNAME=$(      jq '.CUBE.info.cubeKeyName.value'       $JSONFILE | tr -d '"')
    CUBEURL=$(          jq '.CUBE.info.cubeInfo.url'            $JSONFILE | tr -d '"')
    CUBEUSERNAME=$(     jq '.CUBE.info.cubeInfo.username'       $JSONFILE | tr -d '"')
    CUBEUSERPASSWORD=$( jq '.CUBE.info.cubeInfo.password'       $JSONFILE | tr -d '"')
    CUBEPACSSERVICE=$(  jq '.CUBE.cubePACSservice'              $JSONFILE | tr -d '"')
    PACS=$(             jq '.PACS.name'                         $JSONFILE | tr -d '"')
    AET=$(              jq '.PACS.info.aet'                     $JSONFILE | tr -d '"')
    AETL=$(             jq '.PACS.info.aet_listener'            $JSONFILE | tr -d '"')
    AEC=$(              jq '.PACS.info.aec'                     $JSONFILE | tr -d '"')
    PACSSERVERIP=$(     jq '.PACS.info.serverIP'                $JSONFILE | tr -d '"')
    PACSSERVERPORT=$(   jq '.PACS.info.serverPort'              $JSONFILE | tr -d '"')
    URL=$(              jq '.pfdcm.info.url'                    $JSONFILE | tr -d '"')
    b_showJSONsettings=1
fi

if ((b_pfdcm || PFDCM == "local" )) ; then
    vprint "Reading from $PFDCMJSON..."
    URL=$(     jq '.services.'$PFDCM'.info.url'     $PFDCMJSON | tr -d '"')
fi

if (( b_pfdcmSWIFT || PFDCMSWIFT == "local")) ; then
    cmd=$(CURL GET SMDB/swift/${PFDCMSWIFT}/)
    vprint "$cmd"
    jSWIFT=$(eval $cmd)
    vprint "$jSWIFT"
    SWIFTKEYNAME=$PFDCMSWIFT
    SWIFTIP=$(          jq '.swiftInfo.ip'      <<< $jSWIFT | tr -d '"')
    SWIFTPORT=$(        jq '.swiftInfo.port'    <<< $jSWIFT | tr -d '"')
    SWIFTLOGIN=$(       jq '.swiftInfo.login'   <<< $jSWIFT | tr -d '"')
fi

if ((b_pfdcmCUBE || PFDCMCUBE == "local" )) ; then
    cmd=$(CURL GET SMDB/CUBE/${PFDCMCUBE}/)
    vprint "$cmd"
    jCUBE=$(eval $cmd)
    vprint "$jCUBE"
    CUBEKEYNAME=$PFDCMCUBE
    CUBEURL=$(         jq '.cubeInfo.url'       <<< $jCUBE | tr -d '"')
    CUBEUSERNAME=$(    jq '.cubeInfo.username'  <<< $jCUBE | tr -d '"')
    CUBEUSERPASSWORD=$(jq '.cubeInfo.password'  <<< $jCUBE | tr -d '"')
fi

if (( b_pfdcmPACS )) ; then
    cmd=$(CURL GET PACSservice/${PFDCMPACS}/)
    vprint "$cmd"
    jPACS=$(eval $cmd)
    vprint "$jPACS"
    PACS=$PFDCMPACS
    AET=$(              jq '.info.aet'          <<< $jPACS | tr -d '"')
    AETL=$(             jq '.info.aet_listener' <<< $jPACS | tr -d '"')
    PACSSERVERIP=$(     jq '.info.serverIP'     <<< $jPACS | tr -d '"')
    PACSSERVERPORT=$(   jq '.info.serverPort'   <<< $jPACS | tr -d '"')
fi

vprint "SWIFTKEYNAME        = $SWIFTKEYNAME"
vprint "SWIFTIP             = $SWIFTIP"
vprint "SWIFTLOGIN          = $SWIFTLOGIN"
vprint "CUBEKEYNAME         = $CUBEKEYNAME"
vprint "CUBEURL             = $CUBEURL"
vprint "CUBEUSERNAME        = $CUBEUSERNAME"
vprint "CUBEUSERPASSWORD    = $CUBEUSERPASSWORD"
vprint "PACS                = $PACS"
vprint "AET                 = $AET"
vprint "AETL                = $AETL"
vprint "PACSSERVERIP        = $PACSSERVERIP"
vprint "PACSSERVERPORT      = $PACSSERVERPORT"
vprint "PFDCMURL            = $URL"


if ((b_pfdcmSetupShow)) ; then
    cmd="cat $PFDCMJSON"
    vprint "$cmd"
    evaljq "$cmd"
fi

if ((b_swiftSetupShow)) ; then
    cmd=$(CURL GET SMDB/swift/list/)
    vprint "$cmd"
    evaljq "$cmd"
fi

setupSWIFTGet="
pfdcm.sh  --swiftSetupGet megalodon --
"
if (( b_setupSwiftGet )) ; then
    cmd=$(CURL GET SMDB/swift/$SWIFTKEYNAME/)
    vprint "$cmd"
    evaljq "$cmd"
fi

setupSWIFTDo="
pfdcm.sh       --swiftSetupDo                       \
               --swiftKeyName megalodon             \
               --swiftIP 192.168.1.200              \
               --swiftPort 8080                     \
               --swiftLogin chris:chris1234 --
"
function setupSwiftDo {
    returnJSON=$1
    JSON=$(jo -p swiftKeyName=$(jo value=$SWIFTKEYNAME) \
                 swiftInfo=$(jo ip=$SWIFTIP port=$SWIFTPORT login=$SWIFTLOGIN))
    if (( ${#returnJSON} )) ; then
        JSONSWIFT=$(jq '. += {"info" : '"$JSON"'}' <<< {})
        JSONSWIFT=$(jq '. += {"swift" :'"$JSONSWIFT"'}' <<< {})
        echo "$JSONSWIFT"
    else
        CMD=$(CURL POST SMDB/swift/ "$JSON")
        evaljq "$CMD"
    fi
}
if (( b_setupSwiftDo )) ; then
    setupSwiftDo
fi


if ((b_cubeSetupShow)) ; then
    cmd=$(CURL GET SMDB/CUBE/list/)
    vprint "$cmd"
    evaljq "$cmd"
fi

setupCUBEGet="
pfdcm.sh  --cubeSetupGet megalodon --
"
if (( b_setupCubeGet )) ; then
    cmd=$(CURL GET SMDB/CUBE/$CUBEKEYNAME/)
    vprint "$cmd"
    evaljq "$cmd"
fi

setupCUBEdo="
pfdcm.sh       --cubeSetupDo                                    \
               --cubeKeyName megalodon                          \
               --cubeURL http://192.168.1.216:8000/api/vi/      \
               --cubeUserName chris                             \
               --cubeUserPassword chris:chris1234 --
"
function setupCUBEdo {
    returnJSON=$1
    JSON=$(jo -p cubeKeyName=$(jo value=$CUBEKEYNAME) \
                 cubeInfo=$(jo url=$CUBEURL username=$CUBEUSERNAME password=$CUBEUSERPASSWORD))
    if (( ${#returnJSON} )) ; then
        JSONCUBE=$(jq '. += {"info" : '"$JSON"'}' <<< {})
        JSONCUBE=$(jq '. += {"CUBE" : '"$JSONCUBE"'}' <<< {})
        JSONCUBE=$(jq '.CUBE += {"cubePACSservice" : "'"$CUBEPACSSERVICE"'"}' <<< $JSONCUBE)
        echo "$JSONCUBE"
    else
        CMD=$(CURL POST SMDB/CUBE/ "$JSON")
        evaljq "$CMD"
    fi
}
if (( b_setupCUBEdo )) ; then
    setupCUBEdo
fi

if ((b_PACSSetupShow)) ; then
    cmd=$(CURL GET PACSservice/list/)
    vprint "$cmd"
    evaljq "$cmd"
fi


setupPACSGet="
pfdcm.sh  --PACSSetupGet orthanc --
"
if (( b_setupPACSGet )) ; then
    cmd=$(CURL GET PACSservice/$PACS/)
    vprint "$cmd"
    evaljq "$cmd"
fi

setupPACSdo="
pfdcm.sh       --PACSSetupDo                                    \
               --PACS orthanc                                   \
               --aet CHRISLOCAL                                 \
               --aetl ORTHANC                                   \
               --aec ORTHANC                                    \
               --serverIP 192.168.1.189                         \
               --serverPort 4242 --
"
function setupPACSdo {
    returnJSON=$1
    JSON=$(jo -p info=$(jo  aet=$AET                            \
                            aet_listener=$AETL                  \
                            aec=$AEC                            \
                            serverIP=$PACSSERVERIP -- -s serverPort=$PACSSERVERPORT))
    if (( ${#returnJSON} )) ; then
        JSONPACS=$(jq '. += {"PACS" : '"$JSON"'}' <<< {})
        PACSname=$(jq '.PACS += {"name" : "'"$PACS"'"}' <<< $JSONPACS)
        echo "$PACSname"
    else
        CMD=$(CURL PUT PACSservice/$PACS/ "$JSON")
        evaljq "$CMD"
    fi
}
if (( b_setupPACSDo )) ; then
    setupPACSdo
fi

function setupPFDCMdo {
    returnJSON=$1
    if (( ${#returnJSON} )) ; then
        JSON=$(jo -p pfdcm=$(jo info=$(jo url=$URL)))
        echo "$JSON"
    fi
}

if (( b_listenerSetupGet )) ; then
    cmd=$(CURL GET listener/$LISTENER/)
    vprint "$cmd"
    evaljq "$cmd"
fi

#
# Save settings to a profile JSON file. This is also used when initialzing
# from a profile as a sanity-check. During profile initialization a dummy
# settings file is created and compared to the original. If initialization
# was successful, there should be differences between the original profile
# and the dummy file.
#
if (( b_saveToJSON || b_showJSONsettings )) ; then
    if (( b_showJSONsettings )) ; then
        # If we have initialized from JSON, we create a test/dummy
        # JSON setup file from the current set of internal values
        # that have been initialized, and show this created file
        # contents. These should be identical to the original
        # JSON settings file
        ORIGJSON=$JSONFILE
        JSONFILE=/tmp/show-$JSONFILE
    fi
    jSWIFT=$(setupSwiftDo JSON)
    jCUBE=$(setupCUBEdo JSON)
    jPACS=$(setupPACSdo JSON)
    jPFDCM=$(setupPFDCMdo JSON)
    echo "$jSWIFT"  > /tmp/$$.swift.json
    echo "$jCUBE"   > /tmp/$$.cube.json
    echo "$jPACS"   > /tmp/$$.pacs.json
    echo "$jPFDCM"  > /tmp/$$.pfdcm.json
    JSONSETUP=$(jq -s '.[0] * .[1] * .[2] * .[3]'       \
                /tmp/$$.swift.json /tmp/$$.cube.json    \
                /tmp/$$.pacs.json /tmp/$$.pfdcm.json)
    rm /tmp/$$.swift.json /tmp/$$.cube.json /tmp/$$.pacs.json /tmp/$$.pfdcm.json
    echo "$JSONSETUP" > $JSONFILE
    if (( VERBOSITY > 0 )) ; then
        jq . <<< "$JSONSETUP"
    fi
    if (( b_showJSONsettings )) ; then
        diff $ORIGJSON $JSONFILE
        if (( ! $? )) ; then
            vprint "Settings parsed successfully."
        fi
        rm $JSONFILE
    fi
fi

#
# Re-initialize parts of pfdcm if necessary.
#
# This is typically needed when any code changes are made and the server
# dynamically does a "hot" load.
#
if (( b_initDo )) ; then
    jPACS=$(setupPACSdo JSON)
    PACSPOST=$(jq '.PACS' <<< $jPACS)
    PACSPOST=$(jq 'del(.name)' <<< $PACSPOST)
    CMD=$(CURL PUT "PACSservice/$PACS/" "$PACSPOST")
    vprint "$CMD"
    evaljq "$CMD"
    CMD=$(CURL POST listener/initialize/ '{"value" : "default"}')
    vprint "$CMD"
    evaljq "$CMD"
fi
#
# The core engine. Loop over the expression list and call the desired
# pfdcm directive.
#
PAYLOAD=$(preamble)
declare -i loop=1
for EXPR in ${listEXPR//;/ } ; do
    if (( ${#EXPR} )) ; then
        sub=""
        INVALID=0
        VALID=1
        for PAIR in ${EXPR//,/ } ; do
            if (( ${#DICOMKEY} )) ; then
                PAIR="$DICOMKEY:$PAIR"
            fi
            eval $(echo $PAIR | awk -F\: '{printf("sub=\"$sub -s %s=%s\" ", $1, $2)}')
        done
        BODY=$(eval jo -p -- "$sub" "dblogbasepath=$DBROOT/log json_response=true" 2>/dev/null)
        if grep -q ":" <<< "$PAIR"; then VALID=1 ; else INVALID=1 ; fi
        if grep -q "=" <<< "$PAIR"; then INVALID=1 ; fi
        if [[ "$PAIR" != "*all" ]] ; then
            if [[ $? != "0" || $INVALID == "1" ]] ; then
                echo "Some error seems to have occurred in processing the query parameter."
                echo "Please verify it is of form <DIICOMTag>:<Value>, for example:"
                echo ""
                echo -e "\t\t\"PatientID:1234566\""
                echo ""
                echo "and not"
                echo ""
                echo -e "\t\t\"--PatientID:1234566\""
                echo -e "\tthis is WRONG! Don't say \"--PatientID\"!".
                echo ""
                echo "nor"
                echo ""
                echo -e "\t\t\"PatientID 1234566\""
                echo -e "    this is WRONG! Use a colon : not a [space]!".
                echo -e " (in fact don't use spaces at all in the expression)".
                echo ""
                echo "Exiting to system with code 1."
                exit 1
            fi
        fi
        printf -v EXPR "[ %03d ] %s" $loop "$EXPR"
        JSON=$(jq '. += {"PACSdirective" : '"$BODY"'}' <<< $(preamble))
        if (( b_queryDo )) ; then
                CURLcmd=$(CURL POST PACS/sync/pypx/ "$JSON")
                vprint "$CURLcmd"
                if (( b_showSearch )) ; then echo "$EXPR" ; fi
                eval "$CURLcmd" | jq '.pypx' | $(reportify)
        fi
        if (( b_statusDo )) ; then
                JSON=$(jq '.PACSdirective += {
                    "then": "status",
                    "json_response": true}' <<< $JSON)
                CURLcmd=$(CURL POST PACS/sync/pypx/ "$JSON")
                vprint "$CURLcmd"
                if (( b_showSearch )) ; then echo "$EXPR" ; fi
                eval "$CURLcmd" | jq '.pypx' | $(reportify seriesStatus)
        fi
        if (( b_retrieveDo )) ; then
                JSON=$(jq '.PACSdirective += {
                    "then": "retrieve",
                    "json_response": true}' <<< $JSON)
                CURLcmd=$(CURL POST PACS/thread/pypx/  "$JSON")
                vprint "$CURLcmd"
                if (( b_showSearch )) ; then echo "$EXPR" ; fi
                evaljq "$CURLcmd"
        fi
        if (( b_pushDo )) ; then
                JSON=$(jq '.PACSdirective += {
                    "then": "push",
                    "thenArgs": "{\"db\": \"'$DBROOT'/log\", \"swift\": \"'$SWIFTKEYNAME'\", \"swiftServicesPACS\": \"'$PACS'\", \"swiftPackEachDICOM\":   true}",
                    "json_response": true}' <<< $JSON)
                CURLcmd=$(CURL POST PACS/thread/pypx/ "$JSON")
                vprint "$CURLcmd"
                if (( b_showSearch )) ; then echo "$EXPR" ; fi
                evaljq "$CURLcmd"
        fi
        if (( b_registerDo )) ; then
                JSON=$(jq '.PACSdirective += {
                    "then": "register",
                    "thenArgs": "{\"db\": \"'$DBROOT'/log\", \"CUBE\": \"'$CUBEKEYNAME'\", \"swiftServicesPACS\": \"'$PACS'\", \"parseAllFilesWithSubStr\":   \"dcm\"}",
                    "json_response": true}' <<< $JSON)
                CURLcmd=$(CURL POST PACS/thread/pypx/ "$JSON")
                vprint "$CURLcmd"
                if (( b_showSearch )) ; then echo "$EXPR" ; fi
                evaljq "$CURLcmd"
        fi
    fi
    ((loop++))
done

#
# _-30-_
#

