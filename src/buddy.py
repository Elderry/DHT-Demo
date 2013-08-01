#!/usr/local/bin/python2.7
# encoding: utf-8
'''
buddy -- Entry point for all buddies

buddy is a description

It defines classes_and_methods

@author:     Elderry
        
@copyright:  2013 organization_name. All rights reserved.
        
@license:    license

@contact:    Elderry@outlook.com
@deffield    updated: Updated
'''

import sys
import os

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2013-08-01'
__updated__ = '2013-08-01'

def main():
    '''Command line options.'''
    
    program_name = os.path.basename(sys.argv[0])
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by Elderry on %s.
  Copyright 2013 Elderry. All rights reserved.
  
  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0
  
  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        
        # Process arguments
        args = parser.parse_args()
        
        paths = args.paths
        
        for inpath in paths:
            ### do something with inpath ###
            print(inpath)
        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2