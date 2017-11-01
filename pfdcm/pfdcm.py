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

# pfcon local dependencies
from    ._colors        import  Colors
from    .debug          import  debug
from   .C_snode         import *


# Horrible global var
G_b_httpResponse            = False

Gd_internalvar  = {
    'self': {
        'name':             'pfdcm',
        'version':          'undefined',
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
        'storescu':         '/usr/local/bin/storescu',
        'storescp':         '/usr/local/bin/storescp',
        'findscu':          '/usr/local/bin/findscu',
        'movescu':          '/usr/local/bin/movescu',
        'echoscu':          '/usr/local/bin/echoscu',
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

Gd_tree         = C_stree()

class StoreHandler(BaseHTTPRequestHandler):

    b_quiet     = False

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
        self.internalctl_varprocess(d_meta = {
            'var':  '/PACS',
            'set':  d_setPACS
        })

        # finally process any valueReplace
        self.internalctl_varprocess(d_meta = {
            'var':  '%HOST_IP',
            'valueReplace': 'ENV'
        })

    def __init__(self, *args, **kwargs):
        """
        """
        self.__name__   = 'StoreHandler'
        self.pp         = pprint.PrettyPrinter(indent=4)

        # pudb.set_trace()

        if len(args) == 3:
            self.server     = args[2]
            if len(self.server.args['setPACS']):
                self.initPACS(setPACS = self.server.args['setPACS'])
                self.server.args['setPACS'] = ''

        b_test      = False
        b_xinetd    = False
        for k,v in kwargs.items():
            if k == 'test':     b_test      = v
            if k == 'xinetd':   b_xinetd    = v

        if not b_test and not b_xinetd:
            BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

        if b_xinetd:
            self.xinetd_everything_process()

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

        self.qprint('Creating service file...', comms = 'status')
        d_ret['fileCreate'] = self.xinetd_fileCreate_process()
        self.qprint('d_ret["fileCreate"] =\n%s' %\
                self.df_print(d_ret['fileCreate']), comms = 'status' )

        self.qprint('Installing service file...', comms = 'status')
        d_ret['fileInstall'] = self.xinetd_fileInstall_process()
        self.qprint('d_ret["fileInstall"] =\n%s' %\
                self.df_print(d_ret['fileInstall']), comms = 'status' )

        self.qprint('Making directories...', comms = 'status')
        d_ret['serviceDirs'] = self.xinetd_serviceDirs_process()
        self.qprint('d_ret["serviceDirs"] =\n%s' %\
                self.df_print(d_ret['serviceDirs']), comms = 'status' )

        self.qprint('Restarting xinetd...', comms = 'status')
        d_ret['service'] = self.xinetd_service_process()
        self.qprint('d_ret["service"] =\n%s' %\
                self.df_print(d_ret['service']), comms = 'status' )

        return {
            'status':   d_ret['fileCreate']['status']   and \
                        d_ret['fileInstall']['status']  and \
                        d_ret['serviceDirs']['status']  and \
                        d_ret['service']['status'],
            'd_ret':    d_ret
        }

    def qprint(self, msg, **kwargs):
        """
        Simple print function with verbosity control.
        """
        str_comms  = ""
        for k,v in kwargs.items():
            if k == 'comms':    str_comms  = v

        str_caller  = inspect.stack()[1][3]

        if not StoreHandler.b_quiet:
            if str_comms == 'status':   print(Colors.PURPLE,    end="")
            if str_comms == 'error':    print(Colors.RED,       end="")
            if str_comms == "tx":       print(Colors.YELLOW + "<----")
            if str_comms == "rx":       print(Colors.GREEN  + "---->")
            print('%s' % datetime.datetime.now() + " | "  + os.path.basename(__file__) + ':' + self.__name__ + "." + str_caller + '() | ', end="")
            print(msg)
            if str_comms == "tx":       print(Colors.YELLOW + "<----")
            if str_comms == "rx":       print(Colors.GREEN  + "---->")
            print(Colors.NO_COLOUR, end="")

    def log_message(self, format, *args):
        """
        This silences the server from spewing to stdout!
        """
        return

    def do_GET(self):

        d_server            = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(self.path).query))
        d_meta              = ast.literal_eval(d_server['meta'])

        d_msg               = {'action': d_server['action'], 'meta': d_meta}
        d_ret               = {}
        self.qprint(self.path, comms = 'rx')

        return d_ret

    def form_get(self, str_verb, data):
        """
        Returns a form from cgi.FieldStorage
        """
        return cgi.FieldStorage(
            IO(data),
            headers = self.headers,
            environ =
            {
                'REQUEST_METHOD':   str_verb,
                'CONTENT_TYPE':     self.headers['Content-Type'],
            }
        )

    def internalctl_varprocess(self, *args, **kwargs):
        """

        get/set a specific variable as parsed from the meta JSON.

        :param args:
        :param kwargs:
        :return:
        """

        l_fileChanged   = []
        hits            = 0

        def fileContentsReplaceAtPath(str_path, **kwargs):
            nonlocal    hits
            nonlocal    l_fileChanged
            b_status        = True
            str_target      = ''
            str_value       = ''
            self.qprint('In dir = %s, hits = %d' % (str_path, hits))
            for k, v in kwargs.items():
                if k == 'target':   str_target  = v
                if k == 'value':    str_value   = v
            for str_hit in Gd_tree.lsf(str_path):
                str_content = Gd_tree.cat(str_hit)
                self.qprint('%20s: %20s' % (str_hit, str_content))
                if str_content  == str_target:
                    self.qprint('%20s: %20s' % (str_hit, str_value))
                    Gd_tree.touch(str_hit, str_value)
                    b_status    = True
                    hits        = hits + 1
                    l_fileChanged.append(str_path + '/' + str_hit)

            return {
                    'status':           b_status,
                    'l_fileChanged':    l_fileChanged
                    }

        global Gd_internalvar
        global Gd_tree
        d_meta      = {}
        d_ret       = {}
        str_var     = ''
        b_status    = False
        b_tree      = False

        for k,v in kwargs.items():
            if k == 'd_meta':   d_meta  = v

        str_var     = d_meta['var']

        T           = C_stree()
        # pudb.set_trace()
        if d_meta:
            if 'get' in d_meta.keys():
                if Gd_tree.isdir(str_var):
                    Gd_tree.copy(startPath = str_var, destination = T)
                    d_ret                   = dict(T.snode_root)
                else:
                    d_ret[str_var]          = Gd_tree.cat(str_var)
                b_status                = True

            if 'set' in d_meta.keys():
                b_tree          = False
                # pudb.set_trace()
                try:
                    d_set       = json.loads(d_meta['set'])
                except:
                    str_set     = json.dumps(d_meta['set'])
                    d_set       = json.loads(str_set)
                    if isinstance(d_set, dict):
                        b_tree  = True
                if b_tree:
                    D       = C_stree()
                    D.initFromDict(d_set)
                    for topDir in D.lstr_lsnode():
                        D.copy(startPath = '/'+topDir, destination = Gd_tree, pathDiskRoot = str_var)
                    d_ret           = d_set
                else:
                    Gd_tree.touch(str_var, d_meta['set'])
                    d_ret[str_var]          = Gd_tree.cat(str_var)
                b_status                = True

            if 'valueReplace' in d_meta.keys():
                # Find all the values in the internalctl tree
                # and replace the value corresponding to 'var' with
                # the field of 'valueReplace'
                # pudb.set_trace()
                str_target      = d_meta['var']
                str_value       = d_meta['valueReplace']
                if str_value    == 'ENV':
                    if str_target.strip('%') in os.environ:
                        str_value   = os.environ[str_target.strip('%')]
                d_ret = Gd_tree.treeExplore(
                        f       = fileContentsReplaceAtPath, 
                        target  = str_target, 
                        value   = str_value
                        )
                b_status        = d_ret['status']
                d_ret['hits']   = hits

        return {'d_ret':    d_ret,
                'status':   b_status}

    def internalctl_process(self, *args, **kwargs):
        """

        Process the 'internalctl' action.

             {  "action": "internalctl",
                     "meta": {
                            "var":      "/tree/path",
                            "set":     "<someValue>"
                     }
             }

             {  "action": "internalctl",
                     "meta": {
                            "var":      "/tree/path",
                            "get":      "currentPath"
                     }
             }

        :param args:
        :param kwargs:
        :return:
        """

        d_request           = {}
        b_status            = False
        d_ret               = {
            'status':   b_status
        }

        for k,v in kwargs.items():
            if k == 'request':   d_request   = v
        if d_request:
            d_meta  = d_request['meta']
            d_ret   = self.internalctl_varprocess(d_meta = d_meta)
        return d_ret


    def xinetd_fileCreate_process(self, *args, **kwargs):
        """
        Process behaviour related to the xinetd service.
        """

        # pudb.set_trace()

        b_status    = False
        str_file    = '/tmp/dicomlistener'
        str_stdout  = ""
        str_stderr  = ""
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
            Gd_tree.cat('/bin/listener'),
            Gd_tree.cat('/bin/storescp'),
            Gd_tree.cat('/xinetd/tmpDir'),
            Gd_tree.cat('/xinetd/logDir'),
            Gd_tree.cat('/xinetd/dataDir'),
            Gd_tree.cat('/xinetd/servicePort')
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
        d_create    = self.xinetd_fileCreate_process(*args, **kwargs)
        if d_create['status']:
           
            try:
                result = subprocess.run('sudo mv %s %s' % (d_create['file'],
                                                           Gd_tree.cat('/xinetd/file')),
                            shell   = True,
                            stdout  = subprocess.PIPE,
                            stderr  = subprocess.PIPE
                            )
                b_status    = True
            except subprocess.CalledProcessError as err:
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
        d_create    = self.xinetd_fileCreate_process(*args, **kwargs)
        if d_create['status']:
            try:
                result = subprocess.run('sudo mkdir -p %s %s %s' % \
                                                          (
                                                           Gd_tree.cat('/xinetd/tmpDir'),
                                                           Gd_tree.cat('/xinetd/logDir'),
                                                           Gd_tree.cat('/xinetd/dataDir')
                                                           ),
                            shell   = True,
                            stdout  = subprocess.PIPE,
                            stderr  = subprocess.PIPE
                            )
                b_status    = True
            except subprocess.CalledProcessError as err:
                b_status    = False

            str_stdout  = result.stdout.decode('utf-8'),
            str_stderr  = result.stderr.decode('utf-8')
            if len(str_stderr):
                b_status    = False

        return {
            'dirs':     (
                            Gd_tree.cat('/xinetd/tmpDir'),
                            Gd_tree.cat('/xinetd/logDir'),
                            Gd_tree.cat('/xinetd/dataDir')
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

        # pudb.set_trace()
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

    def PACSinteract_checkStatus(self, *args, **kwargs):
        """
        Check on the status of a retrieve event.
        """
        global  Gd_tree
        b_status        = True
        d_request       = {}
        d_meta          = {}
        d_ret           = {}
        for k,v in kwargs.items():
            if k == 'request':          d_request           = v

        # pudb.set_trace()
        d_meta          = d_request['meta']
        if 'on' in d_meta:
            d_on        = d_meta['on']
            if 'series_uid' in d_on:
                str_seriesUID       = d_on['series_uid']
                str_seriesMapDir    = Gd_tree.cat('/xinetd/series_mapDir')
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

    def PACSinteract_copySeries(self, *args, **kwargs):
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
            self.qprint(str_copyMsg)
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
        T               = C_stree()
        for k,v in kwargs.items():
            if k == 'request':          d_request           = v

        # pudb.set_trace()
        d_meta          = d_request['meta']
        if 'PACS' in d_meta:
            str_path    = '/PACS/' + d_meta['PACS']
            if Gd_tree.isdir(str_path):
                Gd_tree.copy(startPath  = str_path, destination = T)
                d_tree                  = dict(T.snode_root)
                d_service               = d_tree['PACS'][d_meta['PACS']]
            else:
                return {
                    'status':   False,
                    'msg':      'Invalid PACS specified.'
                }
            if 'do' in d_meta:
                if 'on' in d_meta:
                    d_on        = d_meta['on']
                if d_meta['do'] == 'query':
                    d_service['executable'] = Gd_tree.cat('/bin/findscu')
                    d_ret       = pypx.find({**d_service, **d_on})
                    if d_ret['status'] == 'error' or not len(d_ret['data']):
                        b_status        = False
                if d_meta['do'] == 'retrieve':
                    d_service['executable'] = Gd_tree.cat('/bin/movescu')
                    d_ret       = pypx.move({**d_service, **d_on})
                    if d_ret['status'] == 'error':
                        b_status        = False
                if d_meta['do'] == 'retrieveStatus':
                    d_ret       = self.PACSinteract_checkStatus(request = d_request)
                    b_status    = d_ret['status']
                if d_meta['do'] == 'copy':
                    d_ret       = self.PACSinteract_copySeries(request = d_request)
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

    def hello_process(self, *args, **kwargs):
        """

        The 'hello' action is merely to 'speak' with the server. The server
        can return current date/time, echo back a string, query the startup
        command line args, etc.

        This method is a simple means of checking if the server is "up" and
        running.

        :param args:
        :param kwargs:
        :return:
        """
        global Gd_internalvar

        self.qprint("hello_process()", comms = 'status')
        b_status            = False
        d_ret               = {}
        d_request           = {}
        d_remote            = {}
        for k, v in kwargs.items():
            if k == 'request':      d_request   = v

        d_meta  = d_request['meta']
        if 'askAbout' in d_meta.keys():
            str_askAbout    = d_meta['askAbout']
            d_ret['name']       = Gd_internalvar['self']['name']
            d_ret['version']    = Gd_internalvar['self']['version']
            if str_askAbout == 'timestamp':
                str_timeStamp   = datetime.datetime.today().strftime('%Y%m%d%H%M%S.%f')
                d_ret['timestamp']              = {}
                d_ret['timestamp']['now']       = str_timeStamp
                b_status                        = True
            if str_askAbout == 'sysinfo':
                d_ret['sysinfo']                = {}
                d_ret['sysinfo']['system']      = platform.system()
                d_ret['sysinfo']['machine']     = platform.machine()
                d_ret['sysinfo']['platform']    = platform.platform()
                d_ret['sysinfo']['uname']       = platform.uname()
                d_ret['sysinfo']['version']     = platform.version()
                d_ret['sysinfo']['memory']      = psutil.virtual_memory()
                d_ret['sysinfo']['cpucount']    = multiprocessing.cpu_count()
                d_ret['sysinfo']['loadavg']     = os.getloadavg()
                d_ret['sysinfo']['cpu_percent'] = psutil.cpu_percent()
                d_ret['sysinfo']['hostname']    = socket.gethostname()
                d_ret['sysinfo']['inet']        = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
                b_status                        = True
            if str_askAbout == 'echoBack':
                d_ret['echoBack']               = {}
                d_ret['echoBack']['msg']        = d_meta['echoBack']
                b_status                        = True

        return { 'd_ret':       d_ret,
                 'd_remote':    d_remote,
                 'status':      b_status}

    def key_dereference(self, *args, **kwargs):
        """
        Given the 'coordinate' JSON payload, deference the 'key' and return
        its value in a dictionary.

        {   
            'status', <status>,
            key': <val>
        }

        """
        self.qprint("key_dereference()", comms = 'status')
        
        b_status    = False
        d_request   = {}
        str_key     = ''
        for k,v in kwargs.items():
            if k == 'request':      d_request   = v

        # self.qprint("d_request = %s" % d_request)

        if 'meta-store' in d_request:
            d_metaStore     = d_request['meta-store']
            if 'meta' in d_metaStore:
                str_storeMeta   = d_metaStore['meta']
                str_storeKey    = d_metaStore['key']
                if str_storeKey in d_request[str_storeMeta].keys():
                    str_key     = d_request[str_storeMeta][str_storeKey]
                    b_status    = True
                    self.qprint("key = %s" % str_key, comms = 'status')
        return {
            'status':   b_status,
            'key':      str_key
        }

    def status_process(self, *args, **kwargs):
        """
        Simply returns to caller the 'info' dictionary structure for a give remote
        key store.

        JSON query:

        pfurl --verb POST --raw --http 10.17.24.163:5005/api/v1/cmd --httpResponseBodyParse --jsonwrapper 'payload' --msg '
        {   "action":           "status",
            "threadAction":     false,
            "meta": {
                "remote": {
                        "key":          "simpledsapp-1"
                }
            }
        }'

        """
        self.qprint("status_process()", comms = 'status')
        d_request                   = {}
        d_meta                      = {}
        d_jobOperation              = {}
        b_status                    = False

        for k,v in kwargs.items():
            if k == 'request':      d_request   = v
        
        d_meta      = d_request['meta']
        str_keyID   = d_meta['remote']['key']

        d_jobOperation      = self.jobOperation_do(     key     = str_keyID,
                                                        action  = 'getInfo',
                                                        op      = 'all')
        self.qprint('d_status = %s' % self.pp.pformat(d_jobOperation).strip(), comms = 'status')

        return {
            'status':       d_jobOperation['status'],
            'jobOperation': d_jobOperation
        }


    def do_POST(self, *args, **kwargs):
        """
        Main dispatching method for coordination service.

        The following actions are available:

            * hello
            * coordinate
            * status
            * servicectl

        :param kwargs:
        :return:
        """

        d_msg       = {}
        d_done      = {}
        b_threaded  = False

        # Parse the form data posted
        self.qprint(str(self.headers), comms = 'rx')

        length              = self.headers['content-length']
        data                = self.rfile.read(int(length))
        form                = self.form_get('POST', data)
        d_form              = {}
        d_ret               = {
            'msg':      'In do_POST',
            'status':   True,
            'formsize': sys.getsizeof(form)
        }

        self.qprint('data length = %d' % len(data),   comms = 'status')
        self.qprint('form length = %d' % len(form), comms = 'status')

        if len(form):
            self.qprint("Unpacking multi-part form message...", comms = 'status')
            for key in form:
                self.qprint("\tUnpacking field '%s..." % key, comms = 'status')
                d_form[key]     = form.getvalue(key)
            d_msg               = json.loads((d_form['d_msg']))
        else:
            self.qprint("Parsing JSON data...", comms = 'status')
            d_data              = json.loads(data.decode())
            d_msg               = d_data['payload']

        self.qprint('d_msg = %s' % self.pp.pformat(d_msg).strip(), comms = 'status')

        if 'action' in d_msg:
            self.qprint("verb: %s detected." % d_msg['action'], comms = 'status')
            str_method      = '%s_process' % d_msg['action']
            self.qprint("method to call: %s(request = d_msg) " % str_method, comms = 'status')
            d_done          = {'status': False}
            try:
                pf_method   = getattr(self, str_method)
            except  AttributeError:
                raise NotImplementedError("Class `{}` does not implement `{}`".format(self.__class__.__name__, pf_method))
            
            if 'threadAction' in d_msg:
                b_threaded  = int(d_msg['threadAction'])

            if not b_threaded:
                d_done      = pf_method(request = d_msg)
                self.qprint(self.pp.pformat(d_done).strip(), comms = 'tx')
                d_ret       = d_done
            else:
                t_process   = threading.Thread( target  = pf_method,
                                                args    = (),
                                                kwargs  = {'request': d_msg})
                t_process.start()
                time.sleep(0.1)

        self.ret_client(d_ret)
        return d_ret

    def do_POST_serverctl(self, d_meta):
        """
        """
        d_ctl               = d_meta['ctl']
        self.qprint('Processing server ctl...', comms = 'status')
        self.qprint(d_meta, comms = 'rx')
        if 'serverCmd' in d_ctl:
            if d_ctl['serverCmd'] == 'quit':
                self.qprint('Shutting down server', comms = 'status')
                d_ret = {
                    'msg':      'Server shut down',
                    'status':   True
                }
                self.qprint(d_ret, comms = 'tx')
                self.ret_client(d_ret)
                os._exit(0)

    def ret_client(self, d_ret):
        """
        Simply "writes" the d_ret using json and the client wfile.

        :param d_ret:
        :return:
        """
        if not G_b_httpResponse:
            self.wfile.write(json.dumps(d_ret).encode())
        else:
            self.wfile.write(str(Response(json.dumps(d_ret))).encode())


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """
    Handle requests in a separate thread.
    """

    def col2_print(self, str_left, str_right):
        print(Colors.WHITE +
              ('%*s' % (self.LC, str_left)), end='')
        print(Colors.LIGHT_BLUE +
              ('%*s' % (self.RC, str_right)) + Colors.NO_COLOUR)

    def __init__(self, *args, **kwargs):
        """

        Holder for constructor of class -- allows for explicit setting
        of member 'self' variables.

        :return:
        """
        global Gd_internalvar
        global Gd_tree
        HTTPServer.__init__(self, *args, **kwargs)
        self.LC             = 40
        self.RC             = 40
        self.args           = None
        self.str_desc       = 'pfdcm'
        self.str_name       = self.str_desc
        self.str_version    = ''

        self.dp             = debug(verbosity=0, level=-1)

    def leaf_process(self, **kwargs):
        """
        Process the global Gd_tree and perform possible env substitutions.
        """
        global Gd_tree
        str_path    = ''
        str_target  = ''
        str_newVal  = ''

        for k,v in kwargs.items():
            if k == 'where':    str_path    = v
            if k == 'replace':  str_target  = v
            if k == 'newVal':   str_newVal  = v

        str_parent, str_file    = os.path.split(str_path)
        str_pwd                 = Gd_tree.cwd()
        if Gd_tree.cd(str_parent)['status']:
            str_origVal     = Gd_tree.cat(str_file)
            str_replacement = str_origVal.replace(str_target, str_newVal)
            Gd_tree.touch(str_path, str_replacement)
        Gd_tree.cd(str_pwd)

    def setup(self, **kwargs):
        global G_b_httpResponse
        global Gd_tree
        str_defIP       = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
        str_defIPpman   = str_defIP
        str_defIPpfioh  = str_defIP

        if 'HOST_IP' in os.environ:
            str_defIP       = os.environ['HOST_IP']
            str_defIPpman   = os.environ['HOST_IP']
            str_defIPpfioh  = os.environ['HOST_IP']

        if 'PFDCM_PORT_5015_TCP_ADDR' in os.environ:
            str_defIPpfioh  = os.environ['PFDCM_PORT_5155_TCP_ADDR']

        for k,v in kwargs.items():
            if k == 'args': self.args           = v
            if k == 'desc': self.str_desc       = v
            if k == 'ver':  self.str_version    = v

        G_b_httpResponse = self.args['b_httpResponse']
        print(self.str_desc)

        Gd_internalvar['self']['name']                  = self.str_name
        Gd_internalvar['self']['version']               = self.str_version

        self.col2_print("Listening on address:",    self.args['ip'])
        self.col2_print("Listening on port:",       self.args['port'])
        self.col2_print("Server listen forever:",   self.args['b_forever'])
        self.col2_print("Return HTTP responses:",   G_b_httpResponse)

        Gd_tree.initFromDict(Gd_internalvar)

        # self.leaf_process(  where   = '/service/host/compute/addr', 
        #                     replace = '%PMAN_IP', 
        #                     newVal  = str_defIPpman)

        print(Colors.YELLOW + "\n\t\tInternal data tree:")
        print(C_snode.str_blockIndent(str(Gd_tree), 3, 8))

        print(Colors.LIGHT_GREEN + "\n\n\tWaiting for incoming data..." + Colors.NO_COLOUR)


