# Bytecode Compiler

A simple compiler that reads assembly instructions and 'in'/'out' arrays, then outputs the generated llvm code

## Installation

```bash
pip install .
```

## Usage
```bash
bytecode-compiler <assembly_file> <in_array_file> <out_array_file>
```

### Example
```bash
bytecode-compiler examples/addition/program.asm examples/addition/in examples/addition/out
```