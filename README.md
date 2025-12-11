# Project 3: B-Tree Index File Manager

A command-line program to create and manage B-tree index files stored in a binary format.

## Description

This program implements a B-tree data structure with minimal degree 10, storing key-value pairs in index files. Each index file uses 512-byte blocks, with the first block containing the file header and subsequent blocks containing B-tree nodes.

## Features

- **Create** new index files
- **Insert** key-value pairs into the B-tree
- **Search** for keys in the index
- **Load** key-value pairs from CSV files
- **Print** all key-value pairs in sorted order
- **Extract** all key-value pairs to a CSV file

## File Format

### Header Block (Block 0)
- 8 bytes: Magic number "4348PRJ3"
- 8 bytes: Root node block ID (0 if tree is empty)
- 8 bytes: Next block ID for new nodes
- Remaining bytes: Unused

### Node Block Structure
- 8 bytes: Block ID of this node
- 8 bytes: Parent block ID (0 if root)
- 8 bytes: Number of keys currently in node
- 152 bytes: Array of 19 keys (8 bytes each)
- 152 bytes: Array of 19 values (8 bytes each)
- 160 bytes: Array of 20 child pointers (8 bytes each)
- Remaining bytes: Unused

All integers are stored as 8-byte big-endian values.

## Usage

### Create an index file
```bash
python3 project3.py create <index_file>
```

Example:
```bash
python3 project3.py create test.idx
```

### Insert a key-value pair
```bash
python3 project3.py insert <index_file> <key> <value>
```

Example:
```bash
python3 project3.py insert test.idx 15 100
```

### Search for a key
```bash
python3 project3.py search <index_file> <key>
```

Example:
```bash
python3 project3.py search test.idx 15
```

Output: `15,100`

### Load from CSV file
```bash
python3 project3.py load <index_file> <csv_file>
```

The CSV file should contain one key-value pair per line, separated by commas:
```
1,10
2,20
3,30
```

Example:
```bash
python3 project3.py load test.idx input.csv
```

### Print all key-value pairs
```bash
python3 project3.py print <index_file>
```

Example:
```bash
python3 project3.py print test.idx
```

Output: All key-value pairs printed to stdout, one per line in sorted order.

### Extract to CSV file
```bash
python3 project3.py extract <index_file> <csv_file>
```

Example:
```bash
python3 project3.py extract test.idx output.csv
```

## Error Handling

The program handles various error conditions:
- File does not exist
- File already exists (for create/extract)
- Invalid index file format
- Invalid command or arguments
- Key not found (for search)

All errors are printed to stderr and the program exits with status code 1.

## B-Tree Properties

- **Minimal degree**: 10
- **Maximum keys per node**: 19 (2t - 1)
- **Maximum children per node**: 20 (2t)
- **Minimum keys per non-root node**: 9 (t - 1)
- **Height**: Logarithmic in the number of keys

## Implementation Details

- All file operations use binary mode with big-endian byte order
- Never more than 3 nodes are kept in memory at a time (root, current node, child node during operations)
- New nodes are appended to the end of the file
- The file header is updated after each insertion to maintain the next block ID

## Requirements

- Python 3.x
- No external dependencies (uses only standard library)

## Example Workflow

```bash
# Create a new index file
python3 project3.py create myindex.idx

# Insert some key-value pairs
python3 project3.py insert myindex.idx 1 100
python3 project3.py insert myindex.idx 2 200
python3 project3.py insert myindex.idx 3 300

# Search for a key
python3 project3.py search myindex.idx 2
# Output: 2,200

# Print all pairs
python3 project3.py print myindex.idx
# Output:
# 1,100
# 2,200
# 3,300

# Extract to CSV
python3 project3.py extract myindex.idx output.csv
```

## Author

Project 3 - B-Tree Index File Manager

