#!/usr/bin/env python3

# Single entry point / dispatcher for simplified running of
#
## pfcon
#

import  argparse
import  os
import  subprocess

b_debug     = False
str_desc    = """

 NAME

    docker-entrypoint.py

 SYNOPSIS

    docker-entrypoint.py  [optional cmd args for pfdcm]


 DESCRIPTION

    'docker-entrypoint.py' is the main entrypoint for running pfdcm.

    It creates a service file and starts the xinetd daemon.

"""

def pfdcm_do(args, unknown):

    str_otherArgs   = ' '.join(unknown)

    if args.b_debug:
        str_CMD = "/usr/local/pfdcm/bin/pfdcm %s" % (str_otherArgs)
    else:
        str_CMD = "/usr/local/bin/pfdcm %s" % (str_otherArgs)
    return str_CMD

parser  = argparse.ArgumentParser(description = str_desc)

# Pattern of minimum required pfdcm args
parser.add_argument(
    '--debug',
    help    = 'if specified, use a debug entry point based on a source mapping',
    dest    = 'b_debug',
    action  = 'store_true',
    default = False
)

args, unknown   = parser.parse_known_args()

if __name__ == '__main__':
    try:
        fname   = 'pfcon_do(args, unknown)'
        str_cmd = eval(fname)
        os.system(str_cmd)
    except:
        print("Misunderstood container app... exiting.")
