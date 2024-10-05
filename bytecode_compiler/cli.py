import sys
from llvmlite import ir, binding
from bytecode_compiler.parser import parse_assembly, max_stack_size, word_size
from bytecode_compiler.compiler import compile_bytecode

def read_array_from_file(filename):
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
    if len(array) > max_stack_size:
        print(f"Error: The array in '{filename}' exceeds maximum stack size of {max_stack_size} elements.")
        sys.exit(1)
    # Pad the array with zeros if it's less than max_stack_size elements
    array.extend([0] * (max_stack_size - len(array)))
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

    # Convert 'in_array' and 'out_array' to byte arrays
    def int_list_to_bytearray(int_list):
        byte_array = bytearray()
        for val in int_list:
            # Convert 'val' to 32-byte big-endian representation
            bytes_val = val.to_bytes(32, byteorder='big', signed=False)
            byte_array.extend(bytes_val)
        return byte_array

    in_bytes = int_list_to_bytearray(in_array)
    out_bytes = int_list_to_bytearray(out_array)

    # Create ctypes buffers
    import ctypes

    in_buffer = ctypes.create_string_buffer(bytes(in_bytes), len(in_bytes))
    out_buffer = ctypes.create_string_buffer(bytes(out_bytes), len(out_bytes))

    # Compile the module
    llvm_ir = str(module)
    llvm_mod = binding.parse_assembly(llvm_ir)
    llvm_mod.verify()

    # Create a target machine
    target = binding.Target.from_default_triple()
    target_machine = target.create_target_machine()

    # Create an execution engine
    backing_mod = binding.parse_assembly("")
    engine = binding.create_mcjit_compiler(backing_mod, target_machine)

    # Add the module and compile
    engine.add_module(llvm_mod)
    engine.finalize_object()
    engine.run_static_constructors()

    # Get the function pointer
    func_ptr = engine.get_function_address("function")

    # Create a ctypes function
    from ctypes import CFUNCTYPE, c_void_p, c_uint8, POINTER

    func_type = CFUNCTYPE(None, POINTER(c_uint8), POINTER(c_uint8))
    cfunc = func_type(func_ptr)

    # Call the function
    in_ptr = ctypes.cast(ctypes.byref(in_buffer), POINTER(c_uint8))
    out_ptr = ctypes.cast(ctypes.byref(out_buffer), POINTER(c_uint8))
    cfunc(in_ptr, out_ptr)

    # Convert 'out_buffer' back to 'out_array'
    out_bytes = out_buffer.raw

    def bytearray_to_int_list(byte_array):
        int_list = []
        for i in range(0, len(byte_array), 32):
            bytes_val = byte_array[i:i+32]
            val = int.from_bytes(bytes_val, byteorder='big', signed=False)
            int_list.append(val)
        return int_list

    out_array = bytearray_to_int_list(out_bytes)

    # Print the generated LLVM IR
    print("Generated LLVM IR:")
    print(module)
    
    print("Bytecode:", bytecode)
    print("In array:", in_array)
    print("Out array:", out_array)

if __name__ == "__main__":
    main()