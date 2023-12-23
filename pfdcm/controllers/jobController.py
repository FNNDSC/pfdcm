str_description = """
    This module provides some very simple shell-based job running
    methods.
"""


import  subprocess
import  os
import  pudb
import  json
import  time
from    pathlib     import Path
import  uuid

class jobber:

    def __init__(self, d_args : dict):
        """Constructor for the jobber class.

        Args:
            d_args (dict): a dictionary of "arguments" (parameters) for the
                           object.
        """
        self.args   = d_args.copy()
        self.transmissionCmd:Path   = Path('somefile.cmd')
        self.configPath:Path        = Path('/tmp')
        if not 'verbosity'      in self.args.keys(): self.args['verbosity']     = 0
        if not 'noJobLogging'   in self.args.keys(): self.args['noJobLogging']  = False

    def dict2JSONcli(self, d_dict : dict) -> str:
        """convert a dictionary into a cli conformant json string.

        an input dictionary of

            {
                'key1': 'value1',
                'key2': 'value2'
            }

        is converted to a string:

            "{\"key1\":\"value1\",\"key2\":\"value2\"}"

        args:
            d_dict (dict): a python dictionary to convert

        returns:
            str: cli equivalent string.
        """

        str_json    = json.dumps(d_dict)
        str_json    = str_json.replace('"', r'\"')
        return str_json

    def dict2cli(self, d_dict : dict) -> str:
        """convert a dictionary into a cli conformant json string.

        an input dictionary of

            {
                'key1': 'value1',
                'key2': 'value2',
                'key3': true,
                'key4': false
            }

        is converted to a string:

            "--key1 value1 --key2 value2 --key3"

        args:
            d_dict (dict): a python dictionary to convert

        returns:
            str: cli equivalent string.
        """
        str_cli     : str = ""
        for k,v in d_dict.items():
            if type(v) == bool:
                if v:
                    str_cli += '--%s ' % k
            elif len(v):
                str_cli += '--%s %s ' % (k, v)
        return str_cli

    def job_run(self, str_cmd: str):
        """
        running some cli process via python is cumbersome. the typical/easy
        path of

                            os.system(str_cmd)

        is deprecated and prone to hidden complexity. The preferred
        method is via subprocess, which has a cumbersome processing
        syntax. Still, this method runs the `str_cmd` and returns the
        stderr and stdout strings as well as a returncode.
        Providing readtime output of both stdout and stderr seems
        problematic. The approach here is to provide realtime
        output on stdout and only provide stderr on process completion.
        """
        d_ret       : dict = {
            'stdout':       "",
            'stderr':       "",
            'cmd':          "",
            'cwd':          "",
            'returncode':   0
        }
        str_stdoutline  : str   = ""
        str_stdout      : str   = ""

        p = subprocess.Popen(
                    str_cmd.split(),
                    stdout      = subprocess.PIPE,
                    stderr      = subprocess.PIPE,
        )

        # realtime output on stdout
        while True:
            stdout      = p.stdout.readline()
            if p.poll() is not None:
                break
            if stdout:
                str_stdoutline = stdout.decode()
                if int(self.args['verbosity']):
                    print(str_stdoutline, end = '')
                str_stdout      += str_stdoutline
        d_ret['cmd']        = str_cmd
        d_ret['cwd']        = os.getcwd()
        d_ret['stdout']     = str_stdout
        d_ret['stderr']     = p.stderr.read().decode()
        d_ret['returncode'] = p.returncode
        if int(self.args['verbosity']) and len(d_ret['stderr']):
            print('\nstderr: \n%s' % d_ret['stderr'])
        return d_ret

    def job_runbg(self, str_cmd : str) -> dict:
        """run a job in the background.

        after much (probably unecessary pain) the best solution seemed to
        be:
            * create a shell script on the fs that contains the
              <str_cmd> and a "&"
            * run the shell script in subprocess.popen

        args:
            str_cmd (str): cli string to run

        returns:
            dict: a dictionary of exec state
        """

        def txscript_content(message:str) -> str:
            str_script:str  = ""
            str_script      = f"""#!/bin/bash

            {message}
            """
            str_script = ''.join(str_script.split(r'\r'))
            return str_script

        def txscript_save(str_content) -> None:
            with open(self.transmissionCmd, "w") as f:
                f.write(f'%s' % str_content)
            self.transmissionCmd.chmod(0o755)

        def execstr_build(input:Path) -> str:
            """ the configPath might have spaces, esp on non-Linux systems """
            ret:str             = ""
            t_parts:tuple       = input.parts
            ret                 = '/'.join(['"{0}"'.format(arg) if ' ' in arg else arg for arg in t_parts])
            return ret

        baseFileName:str    = f"job-{uuid.uuid4().hex}"
        self.transmissionCmd = self.configPath / Path(baseFileName + "_tx.cmd")
        d_ret:dict          = {
            'uid'       : "",
            'cmd'       : "",
            'cwd'       : "",
            'script'    : self.transmissionCmd
        }
        # pudb.set_trace()
        str_cmd    += " &"
        txscript_save(txscript_content(str_cmd))
        execCmd:str = execstr_build(self.transmissionCmd)
        process     = subprocess.Popen(
                        execCmd.split(),
                        stdout              = subprocess.PIPE,
                        stderr              = subprocess.PIPE,
                        close_fds           = True
                    )
        #self.transmissionCmd.unlink()
        d_ret['uid']        = str(os.getuid())
        d_ret['cmd']        = str_cmd
        d_ret['cwd']        = os.getcwd()
        return d_ret

    def job_stdwrite(self, d_job : dict, str_outputDir : str, str_prefix : str = "") -> dict:
        """
        Capture the d_job entries to respective files.
        """
        if not self.args['noJobLogging']:
            for key in d_job.keys():
                with open(
                    '%s/%s%s' % (str_outputDir, str_prefix, key), "w"
                ) as f:
                    f.write(str(d_job[key]))
                    f.close()
        return {
            'status': True
        }
