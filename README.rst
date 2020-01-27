##################
pfdcm  v2.0.2.4
##################

.. image:: https://badge.fury.io/py/pfdcm.svg
    :target: https://badge.fury.io/py/pfdcm

.. image:: https://travis-ci.org/FNNDSC/pfdcm.svg?branch=master
    :target: https://travis-ci.org/FNNDSC/pfdcm

.. image:: https://img.shields.io/badge/python-3.5%2B-blue.svg
    :target: https://badge.fury.io/py/pfdcm

.. contents:: Table of Contents

********
Overview
********

This repository provides ``pfdcm`` -- a controlling service that speaks to a PACS and handles DICOM data management. 

pfdcm
=====

Most simply, ``pfdcm`` provides a REST-type interface to querying a PACS as well as managing DICOM data received from a PACS. The REST interface is conformant to the somewhat colloquial pf-* dialects that are spoken by various entities of the ChRIS family of services. Thus, there are JSON specified directives that follow a very specific pattern of syntax.

************
Installation
************

Since the system requires the installation of some system-level companion services, the recommend vector is via the docker mechanism.


Using the ``fnndsc/pfdcm`` dock
===============================

.. code-block:: bash

    docker pull fnndsc/pfdcm
    
and then run

.. code-block:: bash

    docker run --name pfdcm     \
                -v /home:/Users \
                --rm -ti        \
                fnndsc/pfdcm    \
                --forever --httpResponse

*****
Usage
*****

Command line arguments
======================

.. code-block:: html

        --msg '<JSON_formatted>'
        The action to perform. 

        [--type <storageBackendType>]
        The type of object storage. Currently this is 'swift'.

        [--ipSwift <swiftIP>]                            
        The IP interface of the object storage service. Default 'localhost'.

        [--portSwift <swiftPort>]
        The port of the object storage service. Defaults to '8080'.

        [--ipSelf <selfIP>]                            
        The IP interface of the pfstorage service for server mode. 
        Default 'localhost'.

        [--portSelf <selfPort>]
        The port of the pfstorage service for server mode. 
        Defaults to '4055'.

        [--httpResponse]
        Send return strings to client caller as HTTP formatted replies
        with content-type html.

        [--configFileLoad <file>]
        Load configuration information from the JSON formatted <file>.

        [--configFileSave <file>]
        Save configuration information to the JSON formatted <file>.

        [-x|--desc]                                     
        Provide an overview help page.

        [-y|--synopsis]
        Provide a synopsis help summary.

        [--version]
        Print internal version number and exit.

        [--debugToDir <dir>]
        A directory to contain various debugging output -- these are typically
        JSON object strings capturing internal state. If empty string (default)
        then no debugging outputs are captured/generated. If specified, then
        ``pfcon`` will check for dir existence and attempt to create if
        needed.

        [-v|--verbosity <level>]
        Set the verbosity level. "0" typically means no/minimal output. Allows for
        more fine tuned output control as opposed to '--quiet' that effectively
        silences everything.

        [--setPACS <JSONstring>]
        As part of the initialization of the system, set some information pertaining
        to a PACS. For example,

         --setPACS \\
                '{
                    "orthanc" : {
                        "server_ip": "%HOST_IP",
                        "aet": "CHIPS",
                        "aet_listener": "CHIPS",
                        "aec": "ORTHANC",
                        "server_port": "4242"
                    }
                }'

    EXAMPLES

    pfstorage                                               \
        --ipSwift localhost                                 \
        --portSwift 8080                                    \
        --ipSelf localhost                                  \
        --portSelf 4055                                     \
        --httpResponse                                      \
        --verbosity 1                                       \
        --debugToDir /tmp                                   \
        --type swift                                        \
        --server                                            \
        --forever 





