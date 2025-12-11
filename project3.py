#!/usr/bin/env python3
"""
Project 3: B-Tree Index File Manager
A command-line program to create and manage B-tree index files.
"""

import sys
import os
import struct

# Constants
BLOCK_SIZE = 512
MAGIC_NUMBER = b'4348PRJ3'
MIN_DEGREE = 10
MAX_KEYS = 19  # 2*t - 1
MAX_CHILDREN = 20  # 2*t

# Node structure offsets within a block
NODE_BLOCK_ID_OFFSET = 0
NODE_PARENT_ID_OFFSET = 8
NODE_NUM_KEYS_OFFSET = 16
NODE_KEYS_OFFSET = 24
NODE_VALUES_OFFSET = 176  # 24 + 19*8
NODE_CHILDREN_OFFSET = 328  # 176 + 19*8


def int_to_bytes_big_endian(n):
    """Convert integer to 8-byte big-endian representation."""
    return n.to_bytes(8, byteorder='big')


def bytes_to_int_big_endian(b):
    """Convert 8-byte big-endian bytes to integer."""
    return int.from_bytes(b, byteorder='big')


def read_block(file, block_id):
    """Read a block from the file."""
    file.seek(block_id * BLOCK_SIZE)
    return file.read(BLOCK_SIZE)


def write_block(file, block_id, data):
    """Write a block to the file."""
    file.seek(block_id * BLOCK_SIZE)
    file.write(data)
    file.flush()


def read_header(file):
    """Read the header from the index file."""
    file.seek(0)
    header_data = file.read(BLOCK_SIZE)
    
    magic = header_data[0:8]
    if magic != MAGIC_NUMBER:
        return None
    
    root_block_id = bytes_to_int_big_endian(header_data[8:16])
    next_block_id = bytes_to_int_big_endian(header_data[16:24])
    
    return {
        'magic': magic,
        'root_block_id': root_block_id,
        'next_block_id': next_block_id
    }


def write_header(file, root_block_id, next_block_id):
    """Write the header to the index file."""
    header_data = bytearray(BLOCK_SIZE)
    header_data[0:8] = MAGIC_NUMBER
    header_data[8:16] = int_to_bytes_big_endian(root_block_id)
    header_data[16:24] = int_to_bytes_big_endian(next_block_id)
    write_block(file, 0, bytes(header_data))


def read_node(file, block_id):
    """Read a node from the file."""
    if block_id == 0:
        return None
    
    block_data = read_block(file, block_id)
    
    node_block_id = bytes_to_int_big_endian(block_data[NODE_BLOCK_ID_OFFSET:NODE_BLOCK_ID_OFFSET+8])
    parent_block_id = bytes_to_int_big_endian(block_data[NODE_PARENT_ID_OFFSET:NODE_PARENT_ID_OFFSET+8])
    num_keys = bytes_to_int_big_endian(block_data[NODE_NUM_KEYS_OFFSET:NODE_NUM_KEYS_OFFSET+8])
    
    keys = []
    for i in range(MAX_KEYS):
        offset = NODE_KEYS_OFFSET + i * 8
        key = bytes_to_int_big_endian(block_data[offset:offset+8])
        keys.append(key)
    
    values = []
    for i in range(MAX_KEYS):
        offset = NODE_VALUES_OFFSET + i * 8
        value = bytes_to_int_big_endian(block_data[offset:offset+8])
        values.append(value)
    
    children = []
    for i in range(MAX_CHILDREN):
        offset = NODE_CHILDREN_OFFSET + i * 8
        child = bytes_to_int_big_endian(block_data[offset:offset+8])
        children.append(child)
    
    return {
        'block_id': node_block_id,
        'parent_block_id': parent_block_id,
        'num_keys': num_keys,
        'keys': keys[:num_keys],
        'values': values[:num_keys],
        'children': children[:num_keys+1]
    }


def write_node(file, node):
    """Write a node to the file."""
    block_data = bytearray(BLOCK_SIZE)
    
    # Write node metadata
    block_data[NODE_BLOCK_ID_OFFSET:NODE_BLOCK_ID_OFFSET+8] = int_to_bytes_big_endian(node['block_id'])
    block_data[NODE_PARENT_ID_OFFSET:NODE_PARENT_ID_OFFSET+8] = int_to_bytes_big_endian(node['parent_block_id'])
    block_data[NODE_NUM_KEYS_OFFSET:NODE_NUM_KEYS_OFFSET+8] = int_to_bytes_big_endian(node['num_keys'])
    
    # Write keys
    for i in range(MAX_KEYS):
        offset = NODE_KEYS_OFFSET + i * 8
        if i < len(node['keys']):
            block_data[offset:offset+8] = int_to_bytes_big_endian(node['keys'][i])
        else:
            block_data[offset:offset+8] = b'\x00' * 8
    
    # Write values
    for i in range(MAX_KEYS):
        offset = NODE_VALUES_OFFSET + i * 8
        if i < len(node['values']):
            block_data[offset:offset+8] = int_to_bytes_big_endian(node['values'][i])
        else:
            block_data[offset:offset+8] = b'\x00' * 8
    
    # Write children
    for i in range(MAX_CHILDREN):
        offset = NODE_CHILDREN_OFFSET + i * 8
        if i < len(node['children']):
            block_data[offset:offset+8] = int_to_bytes_big_endian(node['children'][i])
        else:
            block_data[offset:offset+8] = b'\x00' * 8
    
    write_block(file, node['block_id'], bytes(block_data))


def validate_index_file(filename):
    """Validate that a file is a valid index file."""
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(filename, 'rb') as f:
            header = read_header(f)
            if header is None:
                print(f"Error: '{filename}' is not a valid index file.", file=sys.stderr)
                sys.exit(1)
            return header
    except Exception as e:
        print(f"Error: Cannot read index file '{filename}': {e}", file=sys.stderr)
        sys.exit(1)


def create_index_file(filename):
    """Create a new index file."""
    if os.path.exists(filename):
        print(f"Error: File '{filename}' already exists.", file=sys.stderr)
        sys.exit(1)
    
    with open(filename, 'wb') as f:
        # Write empty header (root_block_id = 0, next_block_id = 1)
        write_header(f, 0, 1)


def search_node(file, block_id, key):
    """Search for a key in the B-tree starting from a given node."""
    if block_id == 0:
        return None
    
    node = read_node(file, block_id)
    if node is None:
        return None
    
    # Binary search for key in current node
    i = 0
    while i < node['num_keys'] and key > node['keys'][i]:
        i += 1
    
    # Found the key
    if i < node['num_keys'] and key == node['keys'][i]:
        return node['values'][i]
    
    # If leaf and not found, return None
    if len(node['children']) == 0 or node['children'][0] == 0:
        return None
    
    # Recurse to child
    child_id = node['children'][i] if i < len(node['children']) else 0
    if child_id == 0:
        return None
    
    return search_node(file, child_id, key)


def split_child(file, parent_block_id, child_index, next_block_id):
    """Split a full child node."""
    parent = read_node(file, parent_block_id)
    child_block_id = parent['children'][child_index]
    child = read_node(file, child_block_id)
    
    # Move middle key up to parent
    median_key = child['keys'][MIN_DEGREE - 1]
    median_value = child['values'][MIN_DEGREE - 1]
    
    # Check if child is internal (has children) or leaf
    is_internal = len(child['children']) > 0 and child['children'][0] != 0
    
    # Create new right sibling
    # Right node gets keys from index MIN_DEGREE to end (MIN_DEGREE-1 keys)
    new_child = {
        'block_id': next_block_id,
        'parent_block_id': parent_block_id,
        'num_keys': MIN_DEGREE - 1,
        'keys': child['keys'][MIN_DEGREE:],
        'values': child['values'][MIN_DEGREE:],
        'children': child['children'][MIN_DEGREE:] if is_internal else []
    }
    
    # Update child to be left sibling
    # Left node keeps keys from index 0 to MIN_DEGREE-1 (MIN_DEGREE-1 keys)
    child['num_keys'] = MIN_DEGREE - 1
    child['keys'] = child['keys'][:MIN_DEGREE - 1]
    child['values'] = child['values'][:MIN_DEGREE - 1]
    if is_internal:
        child['children'] = child['children'][:MIN_DEGREE]
    else:
        child['children'] = []
    
    # Insert median into parent
    parent['keys'].insert(child_index, median_key)
    parent['values'].insert(child_index, median_value)
    parent['children'].insert(child_index + 1, new_child['block_id'])
    parent['num_keys'] += 1
    
    write_node(file, child)
    write_node(file, new_child)
    
    # Update parent pointers of children moved to new_child (if internal)
    if is_internal:
        for grandchild_id in new_child['children']:
            if grandchild_id != 0:
                grandchild = read_node(file, grandchild_id)
                grandchild['parent_block_id'] = new_child['block_id']
                write_node(file, grandchild)
    
    write_node(file, parent)
    
    return next_block_id + 1


def insert_non_full(file, block_id, key, value, next_block_id):
    """Insert into a non-full node."""
    node = read_node(file, block_id)
    
    i = node['num_keys'] - 1
    
    # If leaf node
    if len(node['children']) == 0 or (len(node['children']) > 0 and node['children'][0] == 0):
        # Insert key in sorted position
        while i >= 0 and key < node['keys'][i]:
            i -= 1
        
        i += 1  # Position to insert at
        node['keys'].insert(i, key)
        node['values'].insert(i, value)
        node['num_keys'] += 1
        write_node(file, node)
        return next_block_id
    else:
        # Find child to insert into
        i = 0
        while i < node['num_keys'] and key > node['keys'][i]:
            i += 1
        
        child_id = node['children'][i] if i < len(node['children']) else 0
        if child_id == 0:
            # Need to create new leaf child
            new_child = {
                'block_id': next_block_id,
                'parent_block_id': block_id,
                'num_keys': 1,
                'keys': [key],
                'values': [value],
                'children': []
            }
            if i >= len(node['children']):
                node['children'].append(next_block_id)
            else:
                node['children'][i] = next_block_id
            write_node(file, new_child)
            write_node(file, node)
            return next_block_id + 1
        
        child = read_node(file, child_id)
        if child['num_keys'] == MAX_KEYS:
            # Split child - this will add a key to parent, so we need to re-read parent
            next_block_id = split_child(file, block_id, i, next_block_id)
            # Re-read parent to get updated keys after split
            node = read_node(file, block_id)
            # Determine which child to go to after split
            if key > node['keys'][i]:
                i += 1
            child_id = node['children'][i] if i < len(node['children']) else 0
        
        return insert_non_full(file, child_id, key, value, next_block_id)


def insert_key_value(filename, key, value):
    """Insert a key-value pair into the B-tree."""
    header = validate_index_file(filename)
    
    key = int(key)
    value = int(value)
    
    with open(filename, 'r+b') as f:
        root_block_id = header['root_block_id']
        next_block_id = header['next_block_id']
        
        if root_block_id == 0:
            # Tree is empty, create root
            root_node = {
                'block_id': next_block_id,
                'parent_block_id': 0,
                'num_keys': 1,
                'keys': [key],
                'values': [value],
                'children': []
            }
            write_node(f, root_node)
            next_block_id += 1
            write_header(f, root_node['block_id'], next_block_id)
        else:
            root = read_node(f, root_block_id)
            if root['num_keys'] == MAX_KEYS:
                # Root is full, need to split
                old_root_id = root_block_id
                new_root = {
                    'block_id': next_block_id,
                    'parent_block_id': 0,
                    'num_keys': 0,
                    'keys': [],
                    'values': [],
                    'children': [old_root_id]
                }
                write_node(f, new_root)
                next_block_id += 1
                
                # Update old root's parent
                root['parent_block_id'] = new_root['block_id']
                write_node(f, root)
                
                # Split old root
                next_block_id = split_child(f, new_root['block_id'], 0, next_block_id)
                
                # Update header
                write_header(f, new_root['block_id'], next_block_id)
                root_block_id = new_root['block_id']
            
            # Insert into root - use updated next_block_id, not stale header value
            next_block_id = insert_non_full(f, root_block_id, key, value, next_block_id)
            
            # Update header with new next_block_id
            header = read_header(f)
            if next_block_id > header['next_block_id']:
                write_header(f, header['root_block_id'], next_block_id)


def search_key(filename, key):
    """Search for a key in the B-tree."""
    header = validate_index_file(filename)
    
    key = int(key)
    
    with open(filename, 'rb') as f:
        root_block_id = header['root_block_id']
        if root_block_id == 0:
            print(f"Error: Key {key} not found.", file=sys.stderr)
            sys.exit(1)
        
        value = search_node(f, root_block_id, key)
        if value is None:
            print(f"Error: Key {key} not found.", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"{key} {value}")


def load_csv(filename, csv_filename):
    """Load key-value pairs from a CSV file."""
    if not os.path.exists(csv_filename):
        print(f"Error: File '{csv_filename}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    with open(csv_filename, 'r') as csv_file:
        for line in csv_file:
            line = line.strip()
            if not line:
                continue
            parts = line.split(',')
            if len(parts) != 2:
                continue
            key, value = parts[0].strip(), parts[1].strip()
            insert_key_value(filename, key, value)


def print_all_keys_values(filename):
    """Print all key-value pairs in sorted order."""
    header = validate_index_file(filename)
    
    def inorder_traversal(file, block_id):
        """In-order traversal to print all keys."""
        if block_id == 0:
            return
        
        node = read_node(file, block_id)
        is_leaf = (len(node['children']) == 0 or node['children'][0] == 0)
        
        for i in range(node['num_keys']):
            if not is_leaf and i < len(node['children']) and node['children'][i] != 0:
                inorder_traversal(file, node['children'][i])
            print(f"{node['keys'][i]} {node['values'][i]}")
        
        if not is_leaf and len(node['children']) > node['num_keys'] and node['children'][node['num_keys']] != 0:
            inorder_traversal(file, node['children'][node['num_keys']])
    
    with open(filename, 'rb') as f:
        root_block_id = header['root_block_id']
        if root_block_id == 0:
            return
        inorder_traversal(f, root_block_id)


def extract_to_csv(filename, output_csv):
    """Extract all key-value pairs to a CSV file."""
    if os.path.exists(output_csv):
        print(f"Error: File '{output_csv}' already exists.", file=sys.stderr)
        sys.exit(1)
    
    header = validate_index_file(filename)
    
    def inorder_traversal(file, block_id, results):
        """In-order traversal to collect all keys."""
        if block_id == 0:
            return
        
        node = read_node(file, block_id)
        is_leaf = (len(node['children']) == 0 or node['children'][0] == 0)
        
        for i in range(node['num_keys']):
            if not is_leaf and i < len(node['children']) and node['children'][i] != 0:
                inorder_traversal(file, node['children'][i], results)
            results.append((node['keys'][i], node['values'][i]))
        
        if not is_leaf and len(node['children']) > node['num_keys'] and node['children'][node['num_keys']] != 0:
            inorder_traversal(file, node['children'][node['num_keys']], results)
    
    with open(filename, 'rb') as f:
        root_block_id = header['root_block_id']
        results = []
        if root_block_id != 0:
            inorder_traversal(f, root_block_id, results)
    
    with open(output_csv, 'w') as out_file:
        for key, value in results:
            out_file.write(f"{key},{value}\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: project3 <command> [arguments...]", file=sys.stderr)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'create':
        if len(sys.argv) != 3:
            print("Usage: project3 create <index_file>", file=sys.stderr)
            sys.exit(1)
        create_index_file(sys.argv[2])
    
    elif command == 'insert':
        if len(sys.argv) != 5:
            print("Usage: project3 insert <index_file> <key> <value>", file=sys.stderr)
            sys.exit(1)
        insert_key_value(sys.argv[2], sys.argv[3], sys.argv[4])
    
    elif command == 'search':
        if len(sys.argv) != 4:
            print("Usage: project3 search <index_file> <key>", file=sys.stderr)
            sys.exit(1)
        search_key(sys.argv[2], sys.argv[3])
    
    elif command == 'load':
        if len(sys.argv) != 4:
            print("Usage: project3 load <index_file> <csv_file>", file=sys.stderr)
            sys.exit(1)
        load_csv(sys.argv[2], sys.argv[3])
    
    elif command == 'print':
        if len(sys.argv) != 3:
            print("Usage: project3 print <index_file>", file=sys.stderr)
            sys.exit(1)
        print_all_keys_values(sys.argv[2])
    
    elif command == 'extract':
        if len(sys.argv) != 4:
            print("Usage: project3 extract <index_file> <csv_file>", file=sys.stderr)
            sys.exit(1)
        extract_to_csv(sys.argv[2], sys.argv[3])
    
    else:
        print(f"Error: Unknown command '{command}'", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

