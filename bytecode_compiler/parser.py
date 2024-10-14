cmd2opcode = {
    "STOP": (0x00, False),
    "LOAD": (0x01, True),
    "STORE": (0x02, True),
    "POP": (0x03, False),
    "ADD": (0x04, False),
    "SUB": (0x05, False),
    "DUP": (0x06, False)
}

max_array_size = 256 # Number of values of the maximum index operand which is a single byte
word_size = 256 # 32 bytes

# Parse the assembly commands into bytecode
def parse_assembly(assembly):
    # Check there is only a signle STOP command
    if assembly.count("STOP") != 1:
        raise ValueError("There must be exactly one STOP command")
    
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
            if arg < 0 or arg >= max_array_size:
                raise ValueError(f"Argument {arg} on line {line_num} must be between 0 and {max_array_size - 1}")
            bytecode[-1].append(arg)
        else:
            if len(parts) != 1:
                raise ValueError(f"Command '{cmd}' on line {line_num} does not take an argument")
    return bytecode