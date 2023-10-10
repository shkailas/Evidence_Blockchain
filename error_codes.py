# File defining error codes used in the blockchain
import sys

def exit_with_code(code):
    sys.exit(code)

def initial_block_error():
    exit_with_code(0)

def item_not_found():
    exit_with_code(2)

def incorrect_arguments():
    exit_with_code(3)

def duplicate_entry():
    exit_with_code(4)

def state_is_incorrect():
    exit_with_code(5)

def invalid_block():
    exit_with_code(6)

def invalid_chain():
    exit_with_code(7)

def duplicate_hashes():
    exit_with_code(8)
