#!/usr/bin/python3
import argparse
import os

# import defined error codes
import bchoc_commands as bhc

# Define command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("command")
parser.add_argument('-c') 
parser.add_argument('-i', action='append')
parser.add_argument('-n')
parser.add_argument('-y', '--why', dest='why')
parser.add_argument('-o', nargs='?', type=str)
parser.add_argument('-r', '--reverse', action="store_true", dest='reverse')

# Reading args
args = parser.parse_args()
commands = args.command

# source_file = "BCHOC_FILE_PATH"
source_file = os.environ.get('BCHOC_FILE_PATH')

if commands == "init":
    bhc.init_function(source_file)

if commands == "add":
    bhc.add_new_block(source_file, args.c, args.i)

if commands == "checkout":
    bhc.checkout(source_file, args.i)
    
if commands == "checkin":
    bhc.checkin(source_file, args.i)

if commands == "log":
    bhc.log(source_file, args.c, args.i, args.reverse, args.n)
    
if commands == "remove":
    bhc.remove(source_file, args.i, args.why, args.o)

if commands == "verify":
    bhc.verify(source_file)