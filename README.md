# Bytecode Compiler

A simple compiler that reads assembly instructions and 'in'/'out' arrays, then outputs the generated llvm code and the result of the execution.
The language it parses are operations on a stack.

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

## Supported Operations

|Opcode  |Operation   |Operands                        |Behavior    |
|--------|------------|--------------------------------|------------|
|0x00    |STOP        |none                            |stop execution (any operations after that are ignored)  |
|0x01    |LOAD        |1 byte - index into in array    |pushes the word at in[i] onto the stack |
|0x02    |STORE       |1 byte - index into out array   |stores the top word on the stack into out[i]    |
|0x03    |POP         |none                            |pops the top word on the stack  |
|0x04    |ADD         |none                            |pops the top two words on the stack, sums them, and pushes the result   |
|0x05    |SUB         |none                            |pops the top two words on the stack, subtracts them, and pushes the result  |
|0x06    |DUP         |none                            |pushes a copy of the top word on the stack  |

## Testing

To run the tests:
```
python -m unittest discover -s tests
```
