str_description = """

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

        In this first case, the state is maintained by a separate
        entity that is external to `pfdcm`, albeit a class object
        and not a service.

        Still, it is hoped that this could at least provide a relatively
        painless base from which to replace the `pfstate` with something
        like a MonogDB at some future point.

"""


from    datetime    import datetime

import  pfstate
from    pfstate     import  S

class Xinetd(S):
    """
    A derived 'pfstate' class that keeps some state information relevant
    to some data module. In this case, information pertinent to the
    xinetd setup in this container.

    See https://github.com/FNNDSC/pfstate for more information.
    """

    def __init__(self, *args, **kwargs):
        """
        An object to hold some generic/global-ish system state, in C_snode
        trees.
        """
        self.state_create(
        {
            'timestamp':            {
                'now':              '%s' % datetime.now()
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
        },
        *args, **kwargs)

Xinetd_db           = Xinetd(
        name        = 'xinetd internals',
        desc        = 'information relevant to the creation and behaviour of the xinetd service'
)
