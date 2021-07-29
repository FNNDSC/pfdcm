from    pydantic            import BaseModel, Field
from    models              import pacsSetupModel

str_designNotes = """
        This module simulates some external data base service, used
        to simulate keeping some state information in the system.

        Typical state includes information about PACS servers to
        interact with, as well as information pertaining to setting
        up the xinetd service etc (although the xinet service is
        best setup using docker, still...)

        The PFDB module returns model representations of data objects
        relevant to the functioning of the pfdcm service.

        In theory, no component of the `pfdcm` system will call on
        state variables or structures directly, but will only interact
        with this API.

        Internally, the "db" is a pfstate object. There can be
        typically only one such object per namespace, so the db
        "wrapper" returns from this object in a manner that
        does not require the caller to understand this internal
        organization.

"""
str_apologies = """

        Yes, dear reader, this is a module for keeping some type
        of "state" information in the system.

        Now, before you might go apoplectic at the idea that `pfdcm`
        is now keeping state, before you might fall backwards in
        righteous indignation, before you open you mouth (or twitch
        your fingers) with thoughts of, "config data should be constant
        over the lifetime of the process and should be set in the
        environment and parsed at startup!"... to you I say, gently,

        "Hold your horses."

        And, "I know. You are not wrong."

        I am, however, purposefully coding some concept of state which
        ideally should probably be contained in a separate module (like
        a MonogDB) for my own illustrative purposes.

        The `pfdcm` system is not meant to scale. It is not meant to
        ramp up over a multitude of environments. Strictly speaking
        it can be designed so that part of its operational behaviour
        is not coded as persistent state information (i.e. it can in
        fact be totally stateless). It can be fully specified at startup
        runtime with complete information to define its scope of
        behaviour.

        These are all true. However, I am choosing with eyes wide open
        to provide some rudimentary exemplar of one way in which state
        could in theory be kept in the system.

        The idea with this module is to _simulate_ an external DB and
        design the system around that. All calls to any state information
        are thus routed through this module and should, in theory, be
        easily updated in future to an actual separate DB.

"""

import  json
from    datetime    import datetime

import  pfstate
from    pfstate     import  S

import  pudb

class DBdata(S):
    """

    All state data, i.e. trackers of information:

        * PACS services available to the system
        * listener setup
        * others?

    are kept in this object

    """
    def __init__(self, *args, **kwargs):
        """
        An object to hold some generic/global-ish system state, in C_snode
        trees.

        Note that in C_snode trees, the paradigm for constructing a tree from
        a dictionary is interpreted to mean that any dictionary element is a
        tree branch and any dictionary value becomes a tree leaf at that branch.

        Thus, if storing a dictionary as a leaf is needed, then the model is to
        convert that dictionary to a JSON string and save that as a tree leaf.
        This protects the JSON dictionary from being expanded out to its own
        nested tree branch/leaf structure. Of course, remember then to interpret
        the JSON string back into a dictionary if needed by any access methods!
        """
        self.state_create(
        {
            'DB' :
            {
                'PACSservice':
                {
                    'default':
                    {
                        'json_created'   : json.dumps({'time' : '%s' % datetime.now()}),
                        'json_modified'  : json.dumps({'time' : '%s' % datetime.now()})
                    }
                },
                'listenerService':
                {
                    'default': {
                        'xinetd':
                        {
                            'json_created'   : json.dumps({'time' : '%s' % datetime.now()}),
                            'json_modified'  : json.dumps({'time' : '%s' % datetime.now()})
                        },
                        'dcmtk':
                        {
                            'json_created'   : json.dumps({'time' : '%s' % datetime.now()}),
                            'json_modified'  : json.dumps({'time' : '%s' % datetime.now()})
                        },
                    }
                }
            },
        },
        *args, **kwargs)


class PFdb():
    """
    An object that is meant to simulate interaction with some external
    (idiosyncratic) data base.

    Actual data is kept in the DBdata object, and this class
    provides a python API to manipulate data objects and
    and returns models of the objects where appropriate.

    The actual objects that contain data are never directly accessed
    by non db services.

    """

    # The DB object is stored directly in the class definition
    # and not in a per-object instance basis. There is afterall
    # only one DB per pfdcm session
    dobj_DB             = None

    # The core parts of the PACS server object
    # d_PACSserverCore        : dict = dict(pacsSetupModel.PACSsetupCore)
    d_PACSserverCore        : dict  = {
                        'aet':              'AETITLE',
                        'aet_listener':     'AETITLE_LISTENER',
                        'aec':              'CALLEDAETITLE',
                        'serverIP':         'SERVER_IP',
                        'serverPort':       'SERVER_PORT'
    }

    d_PACSserverCoreError    : dict  = {
                        'aet':              'error: AETITLE',
                        'aet_listener':     'error: AETITLE_LISTENER',
                        'aec':              'error: CALLEDAETITLE',
                        'serverIP':         'error: SERVER_IP',
                        'serverPort':       'error: SERVER_PORT'
    }

    # Data pertaining to the xinetd listener
    d_xinetdCore            : dict  = {
                        'servicePort':      '10502',
                        'appPort':          '11113',
                        'intraCallPause':   '2',
                        'tmpDir':           '/tmp/data',
                        'logDir':           '/home/dicom',
                        'dataDir':          '/home/dicom',
                        'listener':         '/etc/xinetd.d/dicomlistener',
                        'patient_mapDir':   '/home/dicom/log/patient_map',
                        'study_mapDir':     '/home/dicom/log/study_map',
                        'series_mapDir':    '/home/dicom/log/series_map'
    }

    # Data relevant to dcmtk
    d_dcmtkCore             : dict = {
                        'storescu':         '/usr/bin/storescu',
                        'storescp':         '/usr/bin/storescp',
                        'findscu':          '/usr/bin/findscu',
                        'movescu':          '/usr/bin/movescu',
                        'echoscu':          '/usr/bin/echoscu',
                        'receiver':         '/usr/local/bin/storescp.sh'
    }

    def __init__(self, *args, **kwargs):
        """
        Constructor -- creates default data structures.
        """
        self.str_loginName  = ''
        self.str_passwd     = ''

        for k,v in kwargs.items():
            if k == 'login' :   self.str_loginName  = v
            if k == 'passwd':   self.str_passwd     = v

        # Create the basic DB
        PFdb.dobj_DB    = DBdata(*args, **dict(kwargs, useGlobalState = True))

        # Now add the default PACS details
        PFdb.dobj_DB.T.touch(
            '/DB/PACSservice/default/info',
            PFdb.d_PACSserverCore
        )

        # and the listener service details:
        # xinetd
        PFdb.dobj_DB.T.touch(
            '/DB/listenerService/default/xinetd/info',
            PFdb.d_xinetdCore
        )

        # dcmtk
        PFdb.dobj_DB.T.touch(
            '/DB/listenerService/default/dcmtk/info',
            PFdb.d_dcmtkCore
        )

    def PACSservice_listObjs(self) -> list:
        """
        Return a list of the internal PACS services available.
        """
        return list(PFdb.dobj_DB.T.lstr_lsnode('/DB/PACSservice'))

    def listenerService_listObjs(self) -> list:
        """
        Return a list of the internal listener services available.
        """
        return list(PFdb.dobj_DB.T.lstr_lsnode('/DB/listenerService'))

    def PACSservice_initObj(self,
            str_objName : str,
            d_data      : dict) -> dict:
        """
        Add (or update) information about a new (or existing) PACS server
        to the service.
        """
        str_message     : str   = ""
        if str_objName not in self.PACSservice_listObjs():
            PFdb.dobj_DB.T.mkdir('/DB/PACSservice/%s'   % str_objName)
            PFdb.dobj_DB.T.touch(
                    '/DB/PACSservice/%s/json_created'   % str_objName,
                    json.dumps({'time' : '%s' % datetime.now()})
            )
            str_message     = "New object '%s' created" % str_objName
        else:
            str_message     = "Existing object '%s' modified" % str_objName

        PFdb.dobj_DB.T.touch('/DB/PACSservice/%s/info' % str_objName, d_data)
        PFdb.dobj_DB.T.touch(
                '/DB/PACSservice/%s/json_modified'      % str_objName,
                json.dumps({'time' : '%s' % datetime.now()})
        )
        return {
            'info'          : PFdb.dobj_DB.T.cat(
                                '/DB/PACSservice/%s/info'           % str_objName
                            ),
            'time_created'  : json.loads(PFdb.dobj_DB.T.cat(
                                '/DB/PACSservice/%s/json_created'   % str_objName)
                            ),
            'time_modified' : json.loads(PFdb.dobj_DB.T.cat(
                                '/DB/PACSservice/%s/json_modified'  % str_objName)
                            ),
            'message'       : str_message
        }

    def listenerService_initObjComponent(self,
            str_objName     : str,
            str_component   : str,
            d_data          : dict) -> dict:
        """
        Add (or update) xinetd information about a new (or existing) listener service
        """
        str_message     : str   = ""
        d_dataDef       : dict  = {}
        if str_objName not in self.listenerService_listObjs():
            for str_part in ['xinetd', 'dcmtk']:
                if str_part == 'xinetd':
                    d_dataDef   = PFdb.d_xinetdCore
                else:
                    d_dataDef   = PFdb.d_dcmtkCore
                PFdb.dobj_DB.T.mkdir('/DB/listenerService/%s/%s'            % \
                                    (str_objName, str_part))
                for str_file in ['json_created', 'json_modified']:
                    PFdb.dobj_DB.T.touch(
                            '/DB/listenerService/%s/%s/%s'                  % \
                            (str_objName, str_part, str_file),
                            json.dumps({'time' : '%s' % datetime.now()})
                    )
                PFdb.dobj_DB.T.touch('/DB/listenerService/%s/%s/info'       % \
                            (str_objName, str_part), d_dataDef)
                str_message     = "New %s data for '%s' created"            % \
                                    (str_component, str_objName)
        else:
            str_message     = "Existing %s data for '%s' modified"          % \
                                (str_component, str_objName)

        PFdb.dobj_DB.T.touch('/DB/listenerService/%s/%s/info'               % \
                            (str_objName, str_component), d_data)
        PFdb.dobj_DB.T.touch(
                '/DB/listenerService/%s/%s/json_modified'                   % \
                (str_objName, str_component),
                json.dumps({'time' : '%s' % datetime.now()})
        )
        return {
            'info'          : PFdb.dobj_DB.T.cat(
                                '/DB/listenerService/%s/%s/info'            % \
                                (str_objName, str_component)
                            ),
            'time_created'  : json.loads(PFdb.dobj_DB.T.cat(
                                '/DB/listenerService/%s/%s/json_created'    % \
                                (str_objName, str_component))
                            ),
            'time_modified' : json.loads(PFdb.dobj_DB.T.cat(
                                '/DB/listenerService/%s/%s/json_modified'  % \
                                (str_objName, str_component))
                            ),
            'message'       : str_message
        }

    def PACSservice_portUpdate(self, str_objName : str, str_newPort : str):
        """
        Modify the port of a given PACS server object. The object is assumed
        to exist.
        """
        d_info      :   dict = {}
        d_ret       :   dict = {
            'info'          : PFdb.d_PACSserverCoreError,
            'time_created'  : {'time'   : 'not applicable'},
            'time_modified' : {'time'   : 'not applicable'},
            'message'       : "Specified object to modify was not found!"
        }
        if str_objName in self.PACSservice_listObjs():
            d_info  = PFdb.dobj_DB.T.cat(
                                    '/DB/PACSservice/%s/info'           % str_objName
                )
            d_info['server_port']   = str_newPort
            d_ret   = self.PACSservice_initObj(str_objName, d_info)
        return d_ret

    def PACSservice_info(self, str_objName) -> dict:
        """
        Return a model conforming representation of a given
        PACS server object
        """
        if str_objName in self.PACSservice_listObjs():
            return {
                'info'          : PFdb.dobj_DB.T.cat(
                                    '/DB/PACSservice/%s/info'           % str_objName
                                ),
                'time_created'  : json.loads(PFdb.dobj_DB.T.cat(
                                    '/DB/PACSservice/%s/json_created'   % str_objName)
                                ),
                'time_modified' : json.loads(PFdb.dobj_DB.T.cat(
                                    '/DB/PACSservice/%s/json_modified'  % str_objName)
                                ),
                'message'       : "Service information for '%s'"        % str_objName
            }

    def listenerService_treeGet(self, str_objName):
        if str_objName in self.listenerService_listObjs():
            return PFdb.dobj_DB


    def listenerService_info(self, str_objName) -> dict:
        """
        Return a model conforming representation of a given
        listen service object
        """
        if str_objName in self.listenerService_listObjs():
            return {
                'xinetd'        : {
                    'info'          : PFdb.dobj_DB.T.cat(
                            '/DB/listenerService/%s/xinetd/info'                % str_objName
                                    ),
                    'time_created'  : json.loads(PFdb.dobj_DB.T.cat(
                            '/DB/listenerService/%s/xinetd/json_created'        % str_objName)
                                    ),
                    'time_modified' : json.loads(PFdb.dobj_DB.T.cat(
                            '/DB/listenerService/%s/xinetd/json_modified'       % str_objName)
                                    ),
                    'message'       : "xinetd service information for '%s'"     % str_objName
                },
                'dcmtk'         : {
                    'info'          : PFdb.dobj_DB.T.cat(
                            '/DB/listenerService/%s/dcmtk/info'                 % str_objName
                                    ),
                    'time_created'  : json.loads(PFdb.dobj_DB.T.cat(
                            '/DB/listenerService/%s/dcmtk/json_created'         % str_objName)
                                    ),
                    'time_modified' : json.loads(PFdb.dobj_DB.T.cat(
                            '/DB/listenerService/%s/dcmtk/json_modified'        % str_objName)
                                    ),
                    'message'       : "dcmtk information for '%s'"              % str_objName
                },
            }
