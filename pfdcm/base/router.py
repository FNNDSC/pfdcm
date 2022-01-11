str_description = """
    This module is somewhat pedantic, somewhat historical,
    and could be argued not especially useful. Nonetheless
    it remains here as an example.

    Primarily this module and routes serve as a 'hello' or
    'health check' on the service. Calling

                    :4005/api/v1/hello/

    will return some miscellaneous about the system on which
    the service is running, as well as some miscellaneous
    "about" type information.

    NB!
    For reasons that were not fully debugged nor deemed necessary
    to spend inordinate amount of time debugging, certain fields in the
    read_hello() route seemed to cause swagger errors.

    Specifically the version() and loadavg() calls were noted to
    either result in strange compile errors or by fact of their
    inclusion resulted in swagger errors.

    In the interest of restoring doc swagger these problematic
    fields have been noted in code comments for possible later
    debugging.

"""


from fastapi    import APIRouter, Query
from pydantic   import BaseModel, Field
from typing     import Optional, List, Tuple

# /hello dependencies
# these modules provide some information on the host
# system/environment
import platform
import psutil
import multiprocessing
import os
import socket

class ValueStr(BaseModel):
    value:              str         = ""

def helloRouter_create(
        name:       str,
        about:      str,
        version:    str,
        tags:       List[str] = None
    ) -> APIRouter:
    """
    Example on how to create some predefined routes (hello and about)
    which produces data that can be set per-instance and is constant
    within an instance.

    The traditional (and more legible) paradigm is to create one router
    at the module level which is imported by the client app, as
    demonstrated in ../routes/dicom.py

    This code here demonstrates how to create a router factory/constructor
    function which creates router instances, escaping the singleton pattern.
    Thus, data can be defined by the module of the router's client instead
    of being hard-coded here in the router endpoint definitions.
    """
    # ========== ========== ========== ==========
    # DEFINE RESPONSE DATA MODELS
    # ========== ========== ========== ==========

    # rename variables
    # https://bugs.python.org/issue43380
    # We want to create the AboutModel class in the scope of this function
    # so that its constant response can be generated in the interactive docs

    if tags is None:
        tags = ['pfdcm environmental detail']

    about_name      = name
    about_about     = about
    about_version   = version

    class AboutModel(BaseModel):
        name:       str = Field(about_name,     title='Name of application')
        about:      str = Field(about_about,    title='About this application')
        version:    str = Field(about_version,  title='Version string')

    about_model = AboutModel()

    class SysInfoModel(BaseModel):
        """
        For the most part, copied from
        https://github.com/FNNDSC/pfcon/blob/87f5da953be7c2cc80542bef0e67727dda1b4958/pfcon/pfcon.py#L601-611

        Provides information about the environment in which the service
        is currently running.
        """
        system:         str         =                                       \
        Field(  platform.system(),
                title       = 'Operating system')

        machine:        str         =                                       \
        Field(  platform.machine(),
                title       = 'Computer architecture')

        uname:          List[str]   =                                       \
        Field(  list(platform.uname()),
                title       = 'uname output',
                description = 'Uname output, converted from object to list')

        platform:       str =                                               \
        Field(  platform.platform(),
                title       = 'Kernel name')

        # NB: Not working?
        version:        str =                                               \
        Field(  ...,
                title       = 'Platform version')

        # NB: Not working?
        memory:         List =                                              \
        Field(  ...,
                title       = 'Details about virtual memory',
                description = "Actually a NamedTuple but I'm not typing it out")

        cpucount:       int =                                               \
        Field(  multiprocessing.cpu_count(),
                title       = 'Number of CPU cores')

        # NB: Not working?
        loadavg: tuple      =                                               \
        Field(  ...,
                title       = 'System load',
                description = 'Average system load over last 1, 5, and 15 minutes')

        cpu_percent:    float =                                             \
        Field(  ...,
                title       = 'Current CPU usage percent', le=100.0)

        hostname:       str =                                               \
        Field(  socket.gethostname(),
                title       = 'Hostname')

        inet:           str =                                               \
        Field(  socket.gethostbyname(socket.gethostname()),
                title       = 'Local IP address')


    # TypedDict not supported yet in Python 3.8
    # https://pydantic-docs.helpmanual.io/usage/types/#typeddict
    class EchoModel(BaseModel):
        """
        Simply echo back whatever is POSTed to this API endpoing
        """
        msg: str

    class HelloModel(BaseModel):
        """
        The model describing the relevant "hello" data
        """
        name:       str             = about_model.name
        version:    str             = about_model.version
        sysinfo:    SysInfoModel    = \
        SysInfoModel(
            uname       = ['Linux'],
            memory      = [],
            cpu_percent = 0.0,
            loadavg     = (0.0, 0.0, 0.0),
            version     = ""
        )
        echoBack:   Optional[EchoModel]

    # ========== ========== ========== ==========
    # DEFINE ROUTES
    # ========== ========== ========== ==========
    router = APIRouter()

    @router.get(
        '/about/',
        tags            = tags,
        response_model  = AboutModel
    )
    async def read_about():
        """
        A description of this service.
        """
        return about_model

    @router.get(
        '/hello/',
        tags            = tags,
        response_model  = HelloModel
    )
    async def read_hello(
        echoBack: Optional[str] = Query(
            None,
            description = 'something to print back verbatim')
    ):
        """
        Produce some information like the OG pfcon
        """
        d_ret = {
            'sysinfo': {}
        }
        d_ret['sysinfo']['system']      = platform.system()
        d_ret['sysinfo']['machine']     = platform.machine()
        d_ret['sysinfo']['uname']       = platform.uname()
        d_ret['sysinfo']['platform']    = platform.platform()
        d_ret['sysinfo']['version']     = platform.version()
        d_ret['sysinfo']['memory']      = psutil.virtual_memory()
        d_ret['sysinfo']['cpucount']    = multiprocessing.cpu_count()
        d_ret['sysinfo']['loadavg']     = os.getloadavg()
        d_ret['sysinfo']['cpu_percent'] = psutil.cpu_percent()
        d_ret['sysinfo']['hostname']    = socket.gethostname()
        d_ret['sysinfo']['inet']        = socket.gethostbyname(socket.gethostname())
        sysinfo = SysInfoModel(**d_ret['sysinfo'])

        if echoBack:
            echo = EchoModel(msg = echoBack)
            return HelloModel(
                echoBack    = echo,
                sysinfo     = sysinfo
            )

        return HelloModel(
            sysinfo     = sysinfo
        )

    return router
