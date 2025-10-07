# Lightweight Matrix Library (LML)

## Overview

**Lightweight Matrix Library (LML)** is a collection of functions designed for efficient manipulation and operation on matrices. This library is specifically tailored for embedded systems, offering functionality for generating matrices, retrieving data, performing matrix operations, editing matrices, and various miscellaneous functions.

## Usage

### Using the Library

1. **Include Header File**: 
   - To access the library's functions and data structures in your C program, include the `lml.h` header file.
   ```c
   #include "lml.h"
   ```

2. **Link Against the Library**: 
   - Make sure to include the include and lib folders in the same directory as your C code, then compile with LML.
   ```bash
   gcc -o your_program your_program.c -Llib -llml
   ```

3. **Run Your Program**: 
   - After successfully compiling your program, execute the generated executable.
   ```bash
   ./your_program
   ```

### Modifying the Library

1. **Modify the Source and Header Files**:
   - Make necessary changes to the source files (`lml.c`) and header file (`lml.h`) according to your requirements.

2. **Compile the Library**:
   - Utilize the provided Makefile to compile the library into various formats, including:
     - `lib/liblml.a` (static library)
     - `lib/liblml.dll` (dynamic library for Windows)
     - `lib/liblml.so` (shared object library for Linux)

3. **Test Your Changes**:
   - Thoroughly test your modifications to ensure they meet the desired functionality and do not introduce any regressions.

4. **Submit a Pull Request**:
   - Once satisfied with your changes and after comprehensive testing, submit a pull request to contribute your modifications to the repository.

## Documentation

The documentation for the functions and structures provided by the Lightweight Matrix Library (LML) can be found within the comments in the `include/lml.h` file. Each function and structure is documented with descriptions of their usage, parameters, and return values.

## Contributions

Any contributions or issues related to the Lightweight Matrix Library are welcome. Your feedback is greatly appreciated!