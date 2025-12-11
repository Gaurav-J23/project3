# Development Log

## Initial Commit - December 10, 2025 3:23 PM
- Project initialized
- Basic project structure created

## Project Completion - December 10, 2025 6:46 PM
- Implemented complete B-tree index file manager (project3.py)
- File I/O utilities for reading/writing 512-byte blocks with big-endian 8-byte integers
- B-tree node structure implementation (minimal degree 10, max 19 keys, 20 children)
- Header block operations (magic number, root block ID, next block ID tracking)
- Implemented all required commands:
  - `create`: Create new index files with proper header initialization
  - `insert`: Insert key-value pairs with B-tree insertion algorithm and node splitting
  - `search`: Search for keys in the B-tree structure
  - `load`: Load key-value pairs from CSV files
  - `print`: Print all key-value pairs in sorted order using in-order traversal
  - `extract`: Extract all key-value pairs to CSV files
- Implemented B-tree splitting logic for full nodes
- Added comprehensive error handling for all edge cases
- Created README.md with complete documentation including:
  - Project description and features
  - File format specification (header and node blocks)
  - Usage examples for all commands
  - B-tree properties and implementation details
- Tested implementation with existing test.idx file (99 key-value pairs)
- Verified all commands work correctly including edge cases
- Implementation maintains constraint of never having more than 3 nodes in memory

