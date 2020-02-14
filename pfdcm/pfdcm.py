#!/usr/bin/env python3.5

import  sys

from    io              import  BytesIO as IO
from    http.server     import  BaseHTTPRequestHandler, HTTPServer
from    socketserver    import  ThreadingMixIn
from    webob           import  Response
import  cgi
import  json
import  urllib
import  ast
import  shutil
import  datetime
import  time
import  inspect
import  pprint

import  base64
import  uuid
import  tempfile
import  zipfile

import  threading
import  platform
import  socket
import  psutil
import  os
import  multiprocessing
import  subprocess
import  glob

import  pudb

import  pypx
import  pydicom as dicom
import  pfmisc
import  pfstorage

# pfstorage local dependencies
from    pfmisc._colors      import  Colors
from    pfmisc.debug        import  debug
from    pfmisc.C_snode      import  *
from    pfstate             import  S

# Global vars for sharing data between StoreHandler and HTTPServer
Gd_args             = {}
Gstr_name           = ""
Gstr_description    = ""
Gstr_version        = ""


# Horrible global var
G_b_httpResponse            = False

class D(S):
    """
    A derived 'pfstate' class that keeps system state.
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor
        """

        for k,v in kwargs.items():
            if k == 'args':     d_args          = v

        S.__init__(self, *args, **kwargs)
        if not S.b_init:
            d_specific  = \
                {
                    "swift": {
                        "auth_url":                 "http://%s:%s/auth/v1.0" % \
                                                    (d_args['ipSwift'], d_args['portSwift']),
                        "username":                 "chris:chris1234",
                        "key":                      "testing",
                        "container_name":           "users",
                        "auto_create_container":    True,
                        "file_storage":             "swift.storage.SwiftStorage"
                    },
                    'jobstatus': {
                        'state':            None
                    },

                    'xinetd': {
                        'servicePort':      '10402',
                        'tmpDir':           '/dicom/tmp',
                        'logDir':           '/dicom/log',
                        'dataDir':          '/dicom/data',
                        'file':             '/etc/xinetd.d/dicomlistener',
                        'patient_mapDir':   '/dicom/log/patient_map',
                        'study_mapDir':     '/dicom/log/study_map',
                        'series_mapDir':    '/dicom/log/series_map'
                    },

                    'bin': {
                        'storescu':         '/usr/bin/storescu',
                        'storescp':         '/usr/bin/storescp',
                        'findscu':          '/usr/bin/findscu',
                        'movescu':          '/usr/bin/movescu',
                        'echoscu':          '/usr/bin/echoscu',
                        'listener':         '/usr/local/bin/px-listen'    
                    },

                    'PACS':  {
                        'help' : {
                            'aet':              'AETITLE',
                            'aet_listener':     'AETITLE_LISTENER',
                            'aec':              'CALLEDAETITLE',
                            'server_ip':        '127.0.0.1',
                            'server_port':      '104'
                        }
                    }                    
                }
            S.d_state.update(d_specific)
            S.T.initFromDict(S.d_state)
            S.b_init    = True
            if len(S.T.cat('/this/debugToDir')):
                if not os.path.exists(S.T.cat('/this/debugToDir')):
                    os.makedirs(S.T.cat('/this/debugToDir'))

        self.dp.qprint(
            Colors.YELLOW + "\n\t\tInternal data tree:",
            level   = 1,
            syslog  = False)
        self.dp.qprint(
            C_snode.str_blockIndent(str(S.T), 3, 8),
            level   = 1,
            syslog  = False) 

class pfdcm(pfstorage.swiftStorage):
    """
    The pfdcm class that handles specific operations pertinent to 
    the DICOM service.
    """

    def __init__(self, *args, **kwargs):
        """
        The logic of this constructor reflects a bit from legacy design 
        patterns of `pfcon` -- specifically the passing of flags in a 
        single structure, and the <self.state> dictionary to try and
        organize the space of <self> variables a bit logically.
        """

        # pudb.set_trace()
        super().__init__(*args, **kwargs)

        if len(args) == 3:
            self.server     = args[2]
            if len(self.server.args['setPACS']):
                self.initPACS(setPACS = self.server.args['setPACS'])
                self.server.args['setPACS']     = ''
            if self.server.args['b_xinetd']:
                self.xinetd_everything_process()
                self.server.args['b_xinetd']    = False

    def initPACS(self, *args, **kwargs):
        """
        Call the internal 'set' on the '/PACS' path. 

        Typically this method is only called from the base constructor
        and handles the case when a PACS is set directly from the 
        calling command line.

        Side effects:
            - Add to the internal '/PACS' variable
            - Run the valueReplace on possible %HOST_IP
        """
        d_setPACS   = {}
        str_setPACS = ''

        for k, v in kwargs.items():
            if k == 'setPACS':  str_setPACS = v

        try:
            d_setPACS   = json.loads(str_setPACS)
        except:
            return {
                'status':   False,
                'msg':      'Invalid setPACS construct.'
            }

        # Process the setPACS
        self.s.internalctl_varprocess(d_meta = {
            'var':  '/PACS',
            'set':  d_setPACS
        })

        # finally process any valueReplace
        self.s.internalctl_varprocess(d_meta = {
            'var':  '%HOST_IP',
            'valueReplace': 'ENV'
        })

    def xinetd_fileCreate_process(self, *args, **kwargs):
        """
        Process behaviour related to the xinetd service.
        """

        # pudb.set_trace()

        T           = self.s.T
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
            T.cat('/bin/listener'),
            T.cat('/bin/storescp'),
            T.cat('/xinetd/tmpDir'),
            T.cat('/xinetd/logDir'),
            T.cat('/xinetd/dataDir'),
            T.cat('/xinetd/servicePort')
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

    def xinetd_fileInstall_process(self, *args, **kwargs):
        """
        Process behaviour related to the xinetd service.
        """

        b_status    = False
        T           = self.s.T
        d_create    = self.xinetd_fileCreate_process(*args, **kwargs)
        if d_create['status']:
           
            try:
                result = subprocess.run('sudo mv %s %s' % (d_create['file'],
                                                           T.cat('/xinetd/file')),
                            shell   = True,
                            stdout  = subprocess.PIPE,
                            stderr  = subprocess.PIPE
                            )
                b_status    = True
            except subprocess.CalledProcessError as err:
                self.dp.qprint(
                            'Execption caught: %s' % err, 
                            comms   = 'error',
                            level   = 3
                            )
                b_status    = False

            str_stdout  = result.stdout.decode('utf-8'),
            str_stderr  = result.stderr.decode('utf-8')
            if len(str_stderr):
                b_status    = False

        return {
            'status':   b_status,
            'stdout':   str_stdout,
            'stderr':   str_stderr
        }

    def xinetd_serviceDirs_process(self, *args, **kwargs):
        """
        Process behaviour related to the xinetd service.
        """

        b_status    = False
        T           = self.s.T
        d_create    = self.xinetd_fileCreate_process(*args, **kwargs)
        if d_create['status']:
            try:
                result = subprocess.run('sudo mkdir -p %s %s %s' % \
                                                          (
                                                           T.cat('/xinetd/tmpDir'),
                                                           T.cat('/xinetd/logDir'),
                                                           T.cat('/xinetd/dataDir')
                                                           ),
                            shell   = True,
                            stdout  = subprocess.PIPE,
                            stderr  = subprocess.PIPE
                            )
                b_status    = True
            except subprocess.CalledProcessError as err:
                self.dp.qprint(
                            'Execption caught: %s' % err, 
                            comms   = 'error',
                            level   = 3
                            )
                b_status    = False

            str_stdout  = result.stdout.decode('utf-8'),
            str_stderr  = result.stderr.decode('utf-8')
            if len(str_stderr):
                b_status    = False

        return {
            'dirs':     (
                            T.cat('/xinetd/tmpDir'),
                            T.cat('/xinetd/logDir'),
                            T.cat('/xinetd/dataDir')
                        ),
            'status':   b_status,
            'stdout':   str_stdout,
            'stderr':   str_stderr
        }

    def xinetd_service_process(self, *args, **kwargs):
        """
        Restart the xinet daemon
        """
        b_status    = False
        try:
            result = subprocess.run('sudo /etc/init.d/xinetd restart',
                        shell   = True,
                        stdout  = subprocess.PIPE,
                        stderr  = subprocess.PIPE
                        )
            b_status    = True
        except subprocess.CalledProcessError as err:
            self.dp.qprint(
                            'Execption caught: %s' % err, 
                            comms   = 'error',
                            level   = 3
                            )
            b_status    = False

        str_stdout  = result.stdout.decode('utf-8'),
        str_stderr  = result.stderr.decode('utf-8')
        if len(str_stderr):
            b_status    = False

        return {
            'status':   b_status,
            'stdout':   str_stdout,
            'stderr':   str_stderr
        }

    def xinetd_process(self, *args, **kwargs):
        """
        Process behaviour related to the xinetd service.
        """
        d_request       = {}
        d_meta          = {}
        # The return from this method
        d_ret           = {}
        for k,v in kwargs.items():
            if k == 'request':          d_request           = v

        d_meta          = d_request['meta']
        if 'object' in d_meta and 'do' in d_meta:
            if d_meta['object'] == 'file' and d_meta['do'] == 'create':
                d_ret = self.xinetd_fileCreate_process(*args, **kwargs)
            if d_meta['object'] == 'file' and d_meta['do'] == 'install':
                d_ret = self.xinetd_fileInstall_process(*args, **kwargs)
            if d_meta['object'] == 'service' and d_meta['do'] == 'restart':
                d_ret = self.xinetd_service_process(*args, **kwargs)
            if d_meta['object'] == 'service' and d_meta['do'] == 'mkdirs':
                d_ret = self.xinetd_serviceDirs_process(*args, **kwargs)
            if d_meta['object'] == 'service' and d_meta['do'] == 'everything':
                d_ret = self.xinetd_everything_process(*args, **kwargs)

        return {
            'status':   d_ret['status'],
            'd_ret':    d_ret
        }

    def df_print(self, adict):
        """
        Return a nicely formatted string representation of a dictionary
        """
        return self.pp.pformat(adict).strip()

    def xinetd_everything_process(self, *args, **kwargs):
        """
        Start the xinet service 
        """

        d_ret = {}

        self.dp.qprint('Creating service file...', comms = 'status')
        d_ret['fileCreate'] = self.xinetd_fileCreate_process()
        self.dp.qprint('d_ret["fileCreate"] =\n%s' %\
                self.df_print(d_ret['fileCreate']), comms = 'status' )

        self.dp.qprint('Installing service file...', comms = 'status')
        d_ret['fileInstall'] = self.xinetd_fileInstall_process()
        self.dp.qprint('d_ret["fileInstall"] =\n%s' %\
                self.df_print(d_ret['fileInstall']), comms = 'status' )

        self.dp.qprint('Making directories...', comms = 'status')
        d_ret['serviceDirs'] = self.xinetd_serviceDirs_process()
        self.dp.qprint('d_ret["serviceDirs"] =\n%s' %\
                self.df_print(d_ret['serviceDirs']), comms = 'status' )

        self.dp.qprint('Restarting xinetd...', comms = 'status')
        d_ret['service'] = self.xinetd_service_process()
        self.dp.qprint('d_ret["service"] =\n%s' %\
                self.df_print(d_ret['service']), comms = 'status' )

        return {
            'status':   d_ret['fileCreate']['status']   and \
                        d_ret['fileInstall']['status']  and \
                        d_ret['serviceDirs']['status']  and \
                        d_ret['service']['status'],
            'd_ret':    d_ret
        }

    def PACSinteract_checkStatus(self, *args, **kwargs):
        """
        Check on the status of a retrieve event.
        """
        b_status        = True
        d_request       = {}
        d_meta          = {}
        d_ret           = {}
        T               = self.s.T

        for k,v in kwargs.items():
            if k == 'request':          d_request           = v

        # pudb.set_trace()
        d_meta          = d_request['meta']
        if 'on' in d_meta:
            d_on        = d_meta['on']
            if 'series_uid' in d_on:
                str_seriesUID       = d_on['series_uid']
                str_seriesMapDir    = T.cat('/xinetd/series_mapDir')
                str_seriesMapFile   = '%s/%s.json' % (  str_seriesMapDir,
                                                        str_seriesUID )
                if os.path.exists(str_seriesMapFile):
                    with open(str_seriesMapFile, 'r') as f:
                        d_series        = json.load(f)
                        f.close()
                        str_PACSdir     = d_series[str_seriesUID]
                        str_doneFile    = '%s/series.info' % str_PACSdir
                        numDCMFiles     = len(glob.glob('%s/*dcm' % str_PACSdir))
                        if os.path.exists(str_doneFile):
                            d_ret       = {
                                'msg':              'Received all DICOM files.',
                                'numDCMfiles':      numDCMFiles,
                                'terminatorFile':   str_doneFile,
                                'DICOMdir':         str_PACSdir,
                                'seriesUID':        str_seriesUID,
                                'status':           True
                            }
                        else:
                            d_ret       = {
                                'msg':              'Some DICOM files pending.',
                                'numDCMfiles':      numDCMFiles,
                                'terminatorFile':   str_doneFile,
                                'DICOMdir':         str_PACSdir,
                                'seriesUID':        str_seriesUID,
                                'status':           False
                            }
                else:
                    d_ret       = {
                        'msg':      'Series map file %s not found' % str_seriesMapFile,
                        'status':   False
                    }
            else:
                d_ret       = {
                    'msg':      'series_uid was not specified in call',
                    'status':   False
                }

        return d_ret

    def internalDB_copySeries(self, *args, **kwargs):
        """
        For a passed series, copy from unpack location to a client
        specified destination. 

        PRECONDITIONS
        * The destination target must be on the same filesystem!
        """
        b_status        = False
        d_request       = {}
        d_meta          = {}
        d_ret           = {}
        for k,v in kwargs.items():
            if k == 'request':          d_request           = v

        # pudb.set_trace()
        d_meta          = d_request['meta']
        if 'to' in d_meta:
            d_ret           = self.PACSinteract_checkStatus(request = d_request)        
            str_targetBase  = d_meta['to']['path']
            str_targetDir   = os.path.join(str_targetBase, d_ret['seriesUID'])
            str_sourceDir   = d_ret['DICOMdir']
            str_copyMsg = 'Copying %s to %s...' % (str_sourceDir, str_targetDir)
            self.dp.qprint(str_copyMsg)
            try:
                shutil.copytree(str_sourceDir, str_targetDir)
                b_status    = True
                str_msg     = 'Success: ' + str_copyMsg
            except:
                b_status    = False
                str_msg     = 'Failed: ' + str_copyMsg

        str_timeStamp   = datetime.datetime.today().strftime('%Y%m%d%H%M%S.%f')

        return {
            'status':       b_status,
            'msg':          str_msg,
            'timestamp':    str_timeStamp    
        }

    def internalDB_DICOMtagsGet(self, *args, **kwargs):
        """
        Determine a JSON representation of the DICOM tags of
        a given target.

        PRECONDITIONS
        * The target must have been downloaded already
        """
        b_status        = False
        d_request       = {}
        d_meta          = {}
        d_ret           = {}
        d_dicom         = {}
        for k,v in kwargs.items():
            if k == 'request':          d_request           = v

        # pudb.set_trace()
        d_meta          = d_request['meta']
        if 'on' in d_meta:
            d_on        = d_meta['on']
            d_ret       = self.PACSinteract_checkStatus(request = d_request)
            if d_ret['status']:
                # Read the first DCM in target dir
                str_seriesUID       = d_on['series_uid']
                str_DICOMdir        = d_ret['DICOMdir']
                l_ls                = os.listdir(str_DICOMdir)
                ds                  = dicom.read_file(os.path.join(d_ret['DICOMdir'], l_ls[0]))
                for el in ds.dir():
                    if el != 'PixelData':
                        # if el == 'PatientName': pudb.set_trace()
                        try:
                            val = ds.data_element(el).value
                            if isinstance(val, (bytes, bytearray)):
                                val = val.decode()
                            val = str(val)
                            if isinstance(val, str):
                                d_dicom[el]     = val
                        except:
                            pass
                b_status            = True
        return {
            'status':       b_status,
            'd_dicom':      d_dicom
        }
                        
    def internalDB_process(self, *args, **kwargs):
        """
        Interaction with internal data -- i.e data that has already
        been pulled from the PACS and is located on the pfdcm filesystem.
        """

        b_status        = True
        d_query         = {}
        d_request       = {}
        d_meta          = {}
        str_path        = ''
        d_ret           = {}
        T               = C_stree()
        for k,v in kwargs.items():
            if k == 'request':          d_request           = v

        d_meta          = d_request['meta']
        if 'do' in d_meta:
            if 'on' in d_meta:
                d_on        = d_meta['on']
            if d_meta['do'] == 'DICOMtagsGet':
                d_ret       = self.internalDB_DICOMtagsGet(request = d_request)
                b_status    = d_ret['status']
            if d_meta['do'] == 'copy':
                d_ret       = self.internalDB_copySeries(request = d_request)
                b_status    = d_ret['status']
        else:
            return {
                'status':   False,
                'msg':      'No "do" directive specified.'
            }

        return {
                'status':       b_status,
                d_meta['do']:   d_ret
                }


    def PACSinteract_process(self, *args, **kwargs):
        """
        The PACS Q/R handler.
        """

        b_status        = True
        d_query         = {}
        d_request       = {}
        d_meta          = {}
        str_path        = ''
        d_ret           = {}
        tree            = self.s.T
        T               = C_stree()
        for k,v in kwargs.items():
            if k == 'request':          d_request           = v

        # pudb.set_trace()
        d_meta          = d_request['meta']
        if 'PACS' in d_meta:
            str_path    = '/PACS/' + d_meta['PACS']
            if tree.isdir(str_path):
                tree.copy(startPath     = str_path, destination = T)
                d_tree                  = dict(T.snode_root)
                d_service               = d_tree['PACS'][d_meta['PACS']]
            else:
                return {
                    'status':   False,
                    'msg':      'Invalid PACS specified.'
                }
            # pudb.set_trace()
            if 'do' in d_meta:
                if 'on' in d_meta:
                    d_on        = d_meta['on']
                if d_meta['do'] == 'query':
                    d_service['executable'] = tree.cat('/bin/findscu')
                    d_ret       = pypx.find({**d_service, **d_on})
                    if d_ret['status'] == 'error' or not len(d_ret['data']):
                        b_status        = False
                if d_meta['do'] == 'retrieve':
                    d_service['executable'] = tree.cat('/bin/movescu')
                    d_ret       = pypx.move({**d_service, **d_on})
                    if d_ret['status'] == 'error':
                        b_status        = False
                if d_meta['do'] == 'retrieveStatus':
                    d_ret       = self.PACSinteract_checkStatus(request = d_request)
                    b_status    = d_ret['status']
            else:
                return {
                    'status':   False,
                    'msg':      'No "do" directive specified.'
                }

        return {
                'status':       b_status,
                d_meta['do']:   d_ret
                }



class DCMhandler(pfstorage.StoreHandler):
    """
    The DCM server comms handler -- this class derives from 
    the pfstorage.StoreHandler and handles the processing of
    CURL comms.

    In order to process pfdcm specific functionality, such as
    PACS setup and xinetd handling, this handler needs to 
    instantiate a pfdcm instance that in its turn creates the
    underlying storage class which is tasked with those 
    administrative tasks.

    """

    def __init__(self, *args, **kwargs):
        """
        Handler constructor
        """
        # pudb.set_trace()
        b_initStateOnly = False

        for k, v in kwargs.items():
            if k == 'initStateOnly':    b_initStateOnly = bool(v)

        # Initialize the static class state directly in the 
        # storage module
        pfstorage.swiftStorage.s = D(*args, **kwargs)

        self.__name__           = 'DCMhandler'
        self.b_useDebug         = False
        self.str_debugFile      = '/tmp/pacsretrieve.txt'
        self.b_quiet            = True

        self.dcm                = pfdcm(
                                    *args,
                                    **kwargs
                                )

        self.dp                 = pfmisc.debug(    
                                            verbosity   = 0,
                                            level       = -1,
                                            within      = self.__name__
                                            )
        self.pp                 = pprint.PrettyPrinter(indent=4)

        if not b_initStateOnly:
            super().__init__(*args, **kwargs)

    def xinetd_process(self, *args, **kwargs):
        """
        Process the listener behaviour
        """

        d_ret = self.dcm.xinetd_process(*args, **kwargs)
        return d_ret

    def PACSinteract_process(self, *args, **kwargs):
        """
        Process interactions with the PACS
        """

        d_ret = self.dcm.PACSinteract_process(*args, **kwargs)
        return d_ret

    def internalDB_process(self, *args, **kwargs):
        """
        Process interactions with the internal pulled DICOM sets
        """
        d_ret = self.dcm.internalDB_process(*args, **kwargs)
        return d_ret

    def internalctl_process(self, *args, **kwargs):
        """
        Process any internal state directives.
        """
        
        d_ret = self.dcm.s.internalctl_process(*args, **kwargs)
        return d_ret
