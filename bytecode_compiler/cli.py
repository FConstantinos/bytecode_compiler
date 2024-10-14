import sys
from bytecode_compiler.parser import parse_assembly, max_array_size, word_size
from bytecode_compiler.compiler import compile_bytecode
from bytecode_compiler.execution import execute

def read_array_from_file(filename : str) -> list:
    """Read an array of integers from a file, up to max_stack_size elements."""
    array = []
    try:
        with open(filename, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue  # Skip comments and empty lines
                try:
                    value = int(line)
                except ValueError:
                    raise ValueError(f"Invalid integer '{line}' on line {line_num} in '{filename}'")
                if value < 0 or value >= 2**word_size:
                    raise ValueError(f"Integer {value} on line {line_num} in '{filename}' must be between 0 and 2^{word_size - 1}")
                array.append(value)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    if len(array) > max_array_size:
        print(f"Error: The array in '{filename}' exceeds maximum stack size of {max_array_size} elements.")
        sys.exit(1)
    # Pad the array with zeros if it's less than max_stack_size elements
    array.extend([0] * (max_array_size - len(array)))
    return array

def main():
    if len(sys.argv) != 4:
        print("Usage: bytecode-compiler <assembly_file> <in_array_file> <out_array_file> <stack_size>")
        sys.exit(1)
    assembly_file = sys.argv[1]
    in_array_file = sys.argv[2]
    out_array_file = sys.argv[3]
    
    # Read assembly instructions
    try:
        with open(assembly_file, 'r') as f:
            assembly_code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{assembly_file}' not found.")
        sys.exit(1)

    try:
        bytecode = parse_assembly(assembly_code)
    except ValueError as e:
        print(f"Error parsing assembly file: {e}")
        sys.exit(1)

    # Read 'in' and 'out' arrays
    try:
        in_array = read_array_from_file(in_array_file)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error reading 'in' array: {e}")
        sys.exit(1)

    try:
        out_array = read_array_from_file(out_array_file)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error reading 'out' array: {e}")
        sys.exit(1)

    # Generate the LLVM module
    module = compile_bytecode(bytecode)

    # Execute the module
    result, in_array, out_array = execute(in_array, out_array, module)
    
    # Print the generated LLVM IR
    print("Generated LLVM IR:")
    print(module)
    
    print("Bytecode:", bytecode)
    print("In array:", in_array)
    print("Out array:", out_array)
    print("Result:", result)

if __name__ == "__main__":
    main()