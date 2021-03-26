str_description = """
    This module contains logic pertinent to the xinet "subsystem"
    of the `pfdcm` service.
"""


from    fastapi             import  APIRouter, Query
from    fastapi.encoders    import  jsonable_encoder
from    pydantic            import  BaseModel, Field
from    typing              import  Optional, List, Dict

import  subprocess
from    models              import  listenerModel
import  logging
from    pflogf              import  FnndscLogFormatter
import  os
import  json
import  pudb
import  config

def noop():
    """
    A dummy function that does nothing.
    """
    return {
        'status':   True
    }

def internalObjects_getList() -> list:
    """
    Return a list of internal object names
    """
    return list(config.dbAPI.listenerService_listObjs())

def internalObject_get(objName : str) -> dict:
    """
    Return a dictionary representation of a single listenerService object
    """
    return dict(config.dbAPI.listenerService_info(objName))

def internalObject_getStatus(objName : str) -> dict:
    """
    Return a dictionary representation of a single listenerService object
    """
    return dict({'status': ListenerHandler.b_successfulInit})


def service_updateXinetd(
        objName                 : str,
        data                    : listenerModel.XinetdDBPutModel
) -> dict:
    """
    Create (or update) the xinetd component of a listener object
    """
    d_data          : dict  = jsonable_encoder(data.info)
    return dict(
                config.dbAPI.listenerService_initObjComponent(
                    objName, 'xinetd', d_data
                )
            )

def service_updateDcmtk(
        objName                 : str,
        data                    : listenerModel.DcmtkDBPutModel
) -> dict:
    """
    Create (or update) the xinetd component of a listener object
    """
    d_data          : dict  = jsonable_encoder(data.info)
    return dict(
                config.dbAPI.listenerService_initObjComponent(
                    objName, 'dcmtk', d_data
                )
            )

class ListenerHandler:

    # A class variable is used to track if the subsystem has been successfully
    # initialized.
    b_successfulInit    = False

    def __init__(self, *args, **kwargs):
        """
        Constructor

        This object is created in response to a POST request on `serviceInit`
        with the object name passed by the client. This name is encoded as
        a key word argument here, and used to associate this class with the
        appropriate Xinet object.

        """
        self.str_objName    = 'default'
        for k,v in kwargs.items():
            if k == 'xinetObj'  :   self.str_objName    = v

        self.verbosity          : int   = 1
        self.b_successfulInit   : bool  = True
        self.d_dcmtk            : dict  = {}
        self.d_xinetd           : dict  = {}

        if not self.str_objName in config.dbAPI.listenerService_listObjs():
            ListenerHandler.b_successfulInit    = False
        else:
            d_listenerObj   : dict = config.dbAPI.listenerService_info(
                                            self.str_objName
                                    )
            self.d_dcmtk    = d_listenerObj['dcmtk']['info']
            self.d_xinetd   = d_listenerObj['xinetd']['info']
            ListenerHandler.b_successfulInit    = True

        # logging
        self.log        = logging.getLogger(__name__)
        handler         = logging.StreamHandler()
        handler.setFormatter(FnndscLogFormatter())
        self.log.addHandler(handler)
        self.log.setLevel(logging.DEBUG)

    def job_run(self, str_cmd) -> dict:
        """
        Running some CLI process via python is cumbersome.

        The typical/easy path of

                            os.system(str_cmd)

        is deprecated and prone to  hidden complexity.  The preferred
        method is via subprocess, which has a  cumbersome  processing
        syntax. Still, this method runs the `str_cmd` and returns the
        stderr and stdout strings as well as a returncode.

        Providing  readtime  output of  both stdout and stderr  seems
        problematic. The approach here is to provide  realtime output
        on stdout and only provide stderr on process completion.

        This method was originally coded in the `pfdo_run` module.

        """
        d_ret           : dict = {
            'stdout':       "",
            'stderr':       "",
            'cwd':          "",
            'cmd':          "",
            'returncode':   0
        }
        str_stdoutLine  : str   = ""
        str_stdout      : str   = ""

        p = subprocess.Popen(
                    str_cmd.split(),
                    stdout      = subprocess.PIPE,
                    stderr      = subprocess.PIPE,
        )

        # Realtime output on stdout
        str_stdoutLine  = ""
        str_stdout      = ""
        while True:
            stdout      = p.stdout.readline()
            if p.poll() is not None:
                break
            if stdout:
                str_stdoutLine = stdout.decode()
                if int(self.verbosity):
                    self.log.info(str_stdoutLine)
                str_stdout      += str_stdoutLine
        d_ret['cmd']        = str_cmd
        d_ret['cwd']        = os.getcwd()
        d_ret['stdout']     = str_stdout
        d_ret['stderr']     = p.stderr.read().decode()
        d_ret['returncode'] = p.returncode
        if int(self.verbosity) and len(d_ret['stderr']):
            self.log.error('\nstderr: \n%s' % d_ret['stderr'])
        return d_ret

    def serviceFile_create(self, *args, **kwargs) -> dict:
        """
        Create the dicomlistener file.
        """

        # pudb.set_trace()
        b_status    = False
        str_file    = '/tmp/dicomlistener'
        str_xinetd  = """
        service dicomlistener
        {
            disable             = no
            socket_type         = stream
            wait                = no
            user                = root
            server              = %s
            server_args         = -e %s -t %s -l %s -d %s
            type                = UNLISTED
            port                = %s
            bind                = 0.0.0.0
        } """ % (
            self.d_dcmtk['listener'],
            self.d_dcmtk['storescp'],
            self.d_xinetd['tmpDir'],
            self.d_xinetd['logDir'],
            self.d_xinetd['dataDir'],
            self.d_xinetd['servicePort']
        )

        FILE    = open(str_file, 'w')
        try:
            FILE.write(str_xinetd)
            b_status    = True
        except:
            b_status    = False

        FILE.close()
        return {
            'status':           b_status,
            'fileContents':     str_xinetd,
            'file':             str_file
        }

    def serviceFile_install(self, d_prior, *args, **kwargs) -> dict:
        """
        Copy the created xinetd service file to the appropriate location.
        """

        b_status    : bool  = False
        d_install   : dict  = {}

        if d_prior['status']:
            d_install = self.job_run(
                'mv %s %s' % (d_prior['file'], self.d_xinetd['listener'])
            )
            if d_install['returncode'] == 0: b_status = True

        return {
            'status':   b_status,
            'install':  d_install,
            'prior':    d_prior
        }

    def DICOMdirs_create(self, d_prior, *args, **kwargs) -> dict:
        """
        Create directories in the container space to hold
        incoming DICOM data and logs.
        """

        b_status            : bool  = False
        d_DICOMdirs_create  : dict  = {}
        if d_prior['status']:
            d_DICOMdirs_create = self.job_run(
                    'mkdir -p %s %s %s' % \
                                (
                                 self.d_xinetd['tmpDir'],
                                 self.d_xinetd['logDir'],
                                 self.d_xinetd['dataDir']
                                )
            )
            if d_DICOMdirs_create['returncode'] == 0: b_status = True

        return {
            'dirs':     (
                                 self.d_xinetd['tmpDir'],
                                 self.d_xinetd['logDir'],
                                 self.d_xinetd['dataDir']
                        ),
            'status':               b_status,
            'DICOMdirs_create':     d_DICOMdirs_create,
            'prior':                d_prior
        }

    def restart(self, d_prior, *args, **kwargs) -> dict:
        """
        Restart the xinet daemon
        """
        b_status        : bool  = False
        d_xinetdrestart : dict  = {}

        if d_prior['status']:
            d_xinetdrestart = self.job_run(
                '/etc/init.d/xinetd restart'
            )
            if d_xinetdrestart['returncode'] == 0: b_status = True

        return {
            'status':           b_status,
            'xinetdrestart':    d_xinetdrestart,
            'prior':            d_prior
        }

    def subsystem_init(self, *args, **kwargs) -> dict:
        """
        Perform all the steps pertaining to starting/firing up the
        xinted service.
        """

        b_status    : bool  = False
        d_init      : dict  = {}
        str_message : str   = 'subsystem initialization message'

        if ListenerHandler.b_successfulInit:
            d_init          =   self.restart(
                                    self.DICOMdirs_create(
                                        self.serviceFile_install(
                                            self.serviceFile_create()
                                        )
                                    )
                                )
            b_status        = d_init['status']
            if b_status:
                str_message =                                               \
                        "Listener system '%s' active and ready."            \
                            % self.str_objName
            else:
                str_message =                                               \
                "Some error occured in listener system '%s' initialization."\
                            % self.str_objName
        else:
            str_message     =                                               \
                "The listener subsystem '%s' does not exist!"               \
                            % self.str_objName
        return {
            'status':       b_status,
            'listenerInit': d_init,
            'message':      str_message
        }

def obj_initialize(
            objToInitialize : listenerModel.ValueStr
) -> dict:
    """
    Controller logic triggered when an xinet system should be initialized.
    """

    d_ret   : dict  = {}
    listenerSystem  = ListenerHandler(xinetObj = objToInitialize.value)
    d_ret =  listenerSystem.subsystem_init()
    return d_ret
