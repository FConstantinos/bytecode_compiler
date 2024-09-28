import sys
from llvmlite import ir, binding

def compile_bytecode(bytecode):
    pass

cmd2opcode = {
    "STOP": (0x00, False),
    "LOAD": (0x01, True),
    "STORE": (0x02, True),
    "POP": (0x03, False),
    "ADD": (0x04, False),
    "SUB": (0x05, False),
    "DUP": (0x06, False)
}

# Parse the assembly commands into bytecode
def parse_assembly(assembly):
    bytecode = []
    for line_num, line in enumerate(assembly.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue  # Skip empty lines and comments
        parts = line.split()
        cmd = parts[0].upper()
        if cmd not in cmd2opcode:
            raise ValueError(f"Unknown command '{cmd}' on line {line_num}")
        opcode, has_arg = cmd2opcode[cmd]
        bytecode.append([opcode])
        if has_arg:
            if len(parts) != 2:
                raise ValueError(f"Command '{cmd}' on line {line_num} requires an argument")
            try:
                arg = int(parts[1])
            except ValueError:
                raise ValueError(f"Invalid argument '{parts[1]}' for command '{cmd}' on line {line_num}")
            if arg < 0 or arg >= 256:
                raise ValueError(f"Argument {arg} on line {line_num} must be between 0 and 255")
            bytecode[-1].append(arg)
        else:
            if len(parts) != 1:
                raise ValueError(f"Command '{cmd}' on line {line_num} does not take an argument")
    return bytecode

def read_array_from_file(filename):
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
                array.append(value)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    if len(array) > 256:
        print(f"Error: The array in '{filename}' exceeds 256 elements.")
        sys.exit(1)
    # Pad the array with zeros if it's less than 256 elements
    array.extend([0] * (256 - len(array)))
    return array

def main():
    if len(sys.argv) != 4:
        print("Usage: bytecode-compiler <assembly_file> <in_array_file> <out_array_file>")
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
        out_array = read_array_from_file(out_array_file)
    except ValueError as e:
        print(f"Error reading array file: {e}")
        sys.exit(1)

    print("Bytecode:", bytecode)
    print("In array:", in_array)
    print("Out array:", out_array)

if __name__ == "__main__":
    main()