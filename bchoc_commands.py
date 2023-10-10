import hashlib as hash
import uuid
import os
from stat import *
from datetime import datetime

# import defined error codes
import error_codes as erc
from block import Block 


def init_function(file_path):
    if os.path.exists(file_path):
        print("Blockchain file found with INITIAL block.")
        verify(file_path)
        erc.initial_block_error()

    timestamp = datetime.timestamp(datetime.now())
    null_bytes = b"\x00" * 32
    #case_id = uuid.UUID(int=0)
    case_id = "00000000-0000-0000-0000-000000000000"
    item_id = 0
    state = "INITIAL"
    data = "Initial block\0"
    data_length = 14

    initial_block = Block(null_bytes, timestamp, case_id, item_id, state, data_length, data)

    with open(file_path, 'wb') as file:
        file.write(initial_block.pack())

    print('Blockchain file not found. Created INITIAL block.')

    with open(file_path, 'rb') as file:
        header_vals = Block.HEADER_FORMAT.unpack(file.read(Block.HEADER_FORMAT.size))

    if b"INITIAL" not in header_vals[4]:
        erc.initial_block_error()

# Function to get rid of dashes in case ID and reverse it for endian formatting
def prep_case_id(case_id):
    case_id = case_id.replace("-", "")
    rev_case_id = ""

    for i in range(0, len(case_id), 2):
        rev_case_id = case_id[i]+case_id[i+1] + rev_case_id

    return(rev_case_id)

# Find the last block in the blockchain file with matching id
def find_block(file_path, item_id):
    
    return_block = None

    with open(file_path, "rb") as f:
        # Initialize a variable to store the previous block's hash
        # Loop through the file
        while True:
            # Read one block's worth of data
            header_data = f.read(Block.HEADER_SIZE)
            # If the data is less than a block's worth, we have reached the end of the file
            if len(header_data) < Block.HEADER_SIZE:
                break
            # Unpack the block data
            header_block = Block.unpack(header_data)

            # Read the block's data
            data = f.read(header_block.data_length)
            # Verify that the amount of data read matches the length specified in the header
            if len(data) != header_block.data_length:
                erc.invalid_block()

            # Verify the block's hash
            # if block.previous_hash != previous_hash:
            #     erc.invalid_block()
            # if block.block_hash != block.calculate_hash():
            #     erc.invalid_block()
            # Set the previous_hash variable to the current block's hash
            if int(item_id) == header_block.item_id:
                return_block = header_block

    return(return_block)

# Get the last hash in the blockchain
def get_previous_hash(file_path):
    previous_hash = b"\x00" * 32

    with open(file_path, "rb") as f:
        # Initialize a variable to store the previous block's hash
        # Loop through the file
        while True:
            # Read one block's worth of data
            header_data = f.read(Block.HEADER_SIZE)
            # If the data is less than a block's worth, we have reached the end of the file
            if len(header_data) < Block.HEADER_SIZE:
                break
            # Unpack the block data
            header_block = Block.unpack(header_data)

             # Read the block's data
            data = f.read(header_block.data_length)
            # Verify that the amount of data read matches the length specified in the header
            if len(data) != header_block.data_length:
                erc.invalid_block()

            # Verify the block's hash
            # if block.previous_hash != previous_hash:
            #     erc.invalid_block()
            # if block.block_hash != block.calculate_hash():
            #     erc.invalid_block()
            # Set the previous_hash variable to the current block's hash
            previous_hash = header_block.block_hash

    # Get the final block's hash
    final_block_hash = previous_hash
    return(final_block_hash)

def add_new_block(file_path, case_id, item_id):
    
    if case_id is None or item_id is None:
        erc.incorrect_arguments()

    # Just create a new BCHOC File for now if Blockchain DNE but might have to handle differently 
    if not os.path.exists(file_path):
        init_function(file_path)

    preped_id = prep_case_id(case_id)
    # case_id_uuid = uuid.UUID(preped_id)

    prev_item_id = []
    previous_hash = b"\x00" * 32

    with open(file_path, "rb") as f:
        # Initialize a variable to store the previous block's hash
        # Loop through the file
        while True:
            # Read one block's worth of data
            header_data = f.read(Block.HEADER_SIZE)
            # If the data is less than a block's worth, we have reached the end of the file
            if len(header_data) < Block.HEADER_SIZE:
                break
            # Unpack the block data
            header = Block.unpack(header_data)

            # Read the block's data
            data = f.read(header.data_length)
            # Verify that the amount of data read matches the length specified in the header
            if len(data) != header.data_length:
                erc.invalid_block()

            # Verify the block's hash
            # if header.previous_hash != previous_hash:
            #     print("PREV HASH")
            #     print(header.previous_hash)
            #     print(previous_hash)
            #     erc.invalid_block()
            # if header.block_hash != header.calculate_hash():
            #     print("HEADER HASH")
            #     print(header.block_hash)
            #     print(header.calculate_hash())
            #     erc.invalid_block()
            
            # Add the block's item_id to the list
            prev_item_id.append(header.item_id)
            # Set the previous_hash variable to the current block's hash
            if "INITIAL" not in header.state: 
                previous_hash = header.block_hash

    # Get the final block's hash
    final_block_hash = previous_hash

    print("Case: ", case_id)
    # Check for duplicate item ids
    for i in range(len(item_id)):
        if int(item_id[i]) in prev_item_id:
            print("Item ID Cannot Match Previous Item ID")
            erc.duplicate_entry()
        else:
            timestamp_print = datetime.utcnow().isoformat("T")+"Z"
            state = "CHECKEDIN"
            timestamp = datetime.timestamp(datetime.now())
            data = ""
            data_length = len(data)
            
            # create a new block with the given data and previous hash
            new_block = Block(final_block_hash, timestamp, preped_id, item_id[i], state, data_length, data)

            # write the new block to the file
            with open(file_path, 'ab') as file:
                file.write(new_block.pack())

            final_block_hash = new_block.block_hash
            prev_item_id.append(item_id[i])

            print("Added Item: ", item_id[i])
            print(" Status: ", state)
            print(" Time of Action: ", timestamp_print)
             
def checkin(file_path, item_id):
    if item_id is None:
        erc.incorrect_arguments()

    # Just create a new BCHOC File for now if Blockchain DNE but might have to handle differently 
    if not os.path.exists(file_path):
        init_function(file_path)

    for id in item_id: 
        matching_block = find_block(file_path, id)

        if matching_block == None: 
            erc.item_not_found()
        else: 
            if "CHECKEDOUT" in matching_block.state:
                previous_hash = get_previous_hash(file_path)
                timestamp = datetime.timestamp(datetime.now())
                timestamp_print = datetime.utcnow().isoformat("T")+"Z"
                case_id = str(matching_block.case_id)
                state = "CHECKEDIN"
                data = ""
                data_length = len(data)
            
                # create a new block with the given data and previous hash
                new_block = Block(previous_hash, timestamp, case_id, id, state, data_length, data)

                # write the new block to the file
                with open(file_path, 'ab') as file:
                    file.write(new_block.pack())

                print("Case: ", case_id)
                print("Checked in item: ", id)
                print(" Status: ", state)
                print(" Time of Action: ", timestamp_print)
            else: 
                # Keep in mind this might need to handle all the other states as well
                print("Error: Cannot check out a checked out item. Must check it in first.")
                erc.state_is_incorrect() 
    
def checkout(file_path, item_id):
    if item_id is None:
        erc.incorrect_arguments()

    # Just create a new BCHOC File for now if Blockchain DNE but might have to handle differently 
    if not os.path.exists(file_path):
        init_function(file_path)

    for id in item_id: 
        matching_block = find_block(file_path, id)

        if matching_block == None: 
            erc.item_not_found()
        else: 
            if "CHECKEDIN" in matching_block.state:
                previous_hash = get_previous_hash(file_path)
                timestamp = datetime.timestamp(datetime.now())
                timestamp_print = datetime.utcnow().isoformat("T")+"Z"
                case_id = str(matching_block.case_id)
                state = "CHECKEDOUT"
                data = ""
                data_length = len(data)
            
                # create a new block with the given data and previous hash
                new_block = Block(previous_hash, timestamp, case_id, id, state, data_length, data)

                # write the new block to the file
                with open(file_path, 'ab') as file:
                    file.write(new_block.pack())

                print("Case: ", case_id)
                print("Checked out item: ", id)
                print(" Status: ", state)
                print(" Time of Action: ", timestamp_print)
            else: 
                # Keep in mind this might need to handle all the other states as well
                print("Error: Cannot check out a checked out item. Must check it in first.")
                erc.state_is_incorrect() 

# Function to get rid of dashes in case ID and reverse it for endian formatting
def reverse_bytes(case_id):
    case_id = case_id.replace("-", "")
    rev_case_id = ""

    for i in range(0, len(case_id), 2):
        rev_case_id += case_id[i+1]+case_id[i]

    return(rev_case_id)

def log(file_path, case_id, item_id, reverse, num):
    
    # Just create a new BCHOC File for now if Blockchain DNE but might have to handle differently 
    if not os.path.exists(file_path):
        init_function(file_path)
    
    # create a list of all the blocks in the BC
    blockList = []


    #if case_id == None and item_id == None and reverse == False and num == None: 
    with open(file_path, "rb") as f:
        # Initialize a variable to store the previous block's hash
        # Loop through the file
        while True:
            # Read one block's worth of data
            block_header = f.read(Block.HEADER_SIZE)

            # If the data is less than a block's worth, we have reached the end of the file
            if len(block_header) < Block.HEADER_SIZE:
                break

            # Read the data associated with that block. DO NOT USE THIS DO NOT DELETE
            header = Block.unpack(block_header)

            f.read(header.data_length)

            # Unpack the block data
            block = Block.unpack(block_header)

            if block.block_hash != block.calculate_hash():
                erc.invalid_block()

            blockList.append(block)
            
    def filter_blocks_by_case_id(blocks, case_id):
        filtered_blocks = []
        for block in blocks:
            if reverse_bytes(str(block.case_id)) == case_id.replace("-", ""):
                filtered_blocks.append(block)
        return filtered_blocks
    def filter_blocks_by_item_id(blocks, item_id):
        filtered_blocks = []
        for block in blocks:
            for iid in item_id: 
                if block.item_id == int(iid):
                    filtered_blocks.append(block)
        return filtered_blocks
    

    if case_id != None :
        blockList = filter_blocks_by_case_id(blockList, case_id[::-1])
    if item_id != None :
        blockList = filter_blocks_by_item_id(blockList, item_id)

    if reverse == True:
        blockList = blockList[::-1]
    if num is None or len(blockList) <= int(num):
        for i in range (0, len(blockList)):
            block = blockList[i]
            block_case_id = prep_case_id(str(block.case_id))
            block_item_id = block.item_id
            #block_action = block.state

            block_action = ""
            for c in block.state:
                if(c.isalpha()):
                    block_action+=c

            time = block.timestamp
            dt = datetime.fromtimestamp(time)
            block_timestamp = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

            print("Case: ", uuid.UUID(block_case_id))
            print("Item: ", block_item_id)
            print("Action: ", block_action)
            print("Time: ", block_timestamp)
            if i < len(blockList) - 1:
                print()
                print()

    else:
        for i in range (0, int(num)):
            block = blockList[i]
            #block_case_id = (block.case_id.bytes).hex()
            block_case_id = prep_case_id(str(block.case_id))
            block_item_id = block.item_id
            #block_action = block.state

            block_action = ""
            for i in block.state:
                if(i.isalpha()):
                    block_action+=i

            time = block.timestamp
            dt = datetime.fromtimestamp(time)
            block_timestamp = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

            print("Case: ", uuid.UUID(block_case_id))
            print("Item: ", block_item_id)
            print("Action: ", block_action)
            print("Time: ", block_timestamp)
            print()

    return

def remove(file_path, item_id, reason, owner):
    # Just create a new BCHOC File for now if Blockchain DNE but might have to handle differently 
    if not os.path.exists(file_path):
        init_function(file_path)

    if reason == None or item_id == None:
        erc.incorrect_arguments()

    if reason not in ["RELEASED", "DISPOSED", "DESTROYED"]:
        erc.incorrect_arguments()

    if reason == "RELEASED" and owner == None:
        erc.incorrect_arguments()
    
    for id in item_id: 
        matching_block = find_block(file_path, id)

        if matching_block == None: 
            erc.item_not_found()
        else: 
            if "CHECKEDIN" in matching_block.state:
                previous_hash = get_previous_hash(file_path)
                timestamp = datetime.timestamp(datetime.now())
                timestamp_print = datetime.utcnow().isoformat("T")+"Z"
                case_id = str(matching_block.case_id)
                state = reason
                if state == "RELEASED":
                    data = owner + "\0"
                else: 
                    data = ""
                data_length = len(data)
            
                # create a new block with the given data and previous hash
                new_block = Block(previous_hash, timestamp, case_id, id, state, data_length, data)

                # write the new block to the file
                with open(file_path, 'ab') as file:
                    file.write(new_block.pack())

                print("Case: ", case_id)
                print("Removed item: ", id)
                print(" Status: ", state)
                if state == "RELEASED":
                    print(" Owner info: ", owner)
                print(" Time of Action: ", timestamp_print)
            else: 
                # Keep in mind this might need to handle all the other states as well
                print("Error: Cannot remove a checked out item.")
                erc.state_is_incorrect() 

def block_status(block):
    if "CHECKEDIN" in block.state: 
        return "Add"
    elif "CHECKEDOUT" in block.state:
        return "Checkout"
    else:
        for status in ["RELEASED", "DISPOSED", "DESTROYED"]:
            if status in block.state:
                return "Remove"
    return ""

def verify(file_path):


    with open(file_path, "rb") as f:

        header_blocks = []
        previous_hash = b'\x00' * 32

        initial_header = f.read(Block.HEADER_SIZE)

        if len(initial_header) < Block.HEADER_SIZE:
            erc.invalid_block()

        header_block = Block.unpack(initial_header)

        if header_block.previous_hash != previous_hash:
            print("Invalid inital previous hash")
            erc.invalid_block()
        
        if str(header_block.case_id) != "00000000-0000-0000-0000-000000000000":
            print("Invalid inital case id")
            erc.invalid_block()

        if header_block.item_id != 0:
            print("Invalid inital item id")
            erc.invalid_block()

        if "INITIAL" not in header_block.state:
            print("Invalid inital state")
            erc.invalid_block()

        # Read the block's data
        data = f.read(header_block.data_length)
        # Verify that the amount of data read matches the length specified in the header
        if len(data) != header_block.data_length:
            print("Invalid initial data length")
            erc.invalid_block()
        # Verify the block's hash
        if data != b'Initial block\x00':
            print("Invalid initial data")
            erc.invalid_block()

        previous_hash = header_block.block_hash

        while True:
            # Read one block's worth of data
            header_data = f.read(Block.HEADER_SIZE)
            # If the data is less than a block's worth, we have reached the end of the file
            if len(header_data) < Block.HEADER_SIZE:
                break
            # Unpack the block data
            header_block = Block.unpack(header_data)

            for block in header_blocks: 
                if block.item_id == header_block.item_id:
                    print(block.item_id)
                    print(header_block.item_id)
                    print("ITEM ID repeat")
                    erc.invalid_block()

            header_blocks.append(header_block)

            # Read the block's data
            data = f.read(header_block.data_length)
            # Verify that the amount of data read matches the length specified in the header
            if len(data) != header_block.data_length:
                print("Invalid data length")
                erc.invalid_block()

            # Verify the block's hash
            # if header_block.previous_hash != previous_hash:
            #     print(header_block.previous_hash)
            #     print(previous_hash)
            #     #print("Invalid inital previous hash")
            #     erc.invalid_block()
            if header_block.block_hash != header_block.calculate_hash():
                print("Invalid block hash")
                erc.invalid_block()
            # Set the previous_hash variable to the current block's hash
            previous_hash = header_block.block_hash
