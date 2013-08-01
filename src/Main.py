#!/usr/local/bin/python2.7
# encoding: utf-8

'''
Entry point here
'''

from argparse import ArgumentParser

def main():

    try:
        # Setup argument parser
        parser = ArgumentParser()
        
        # Process arguments
        args = parser.parse_args()
        
    except KeyboardInterrupt:
        print('Exiting...')
        print('Thanks for using')
        return 0

main()