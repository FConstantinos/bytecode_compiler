import llvmlite.binding as binding
from llvmlite import ir

def execute(in_array : list[int], out_array : list[int], module : ir.Module) -> tuple[list[int], list[int]]:
    """Execute the LLVM module with the given 'in' and 'out' arrays."""
    
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
    from ctypes import CFUNCTYPE, c_uint8, POINTER

    func_type = CFUNCTYPE(c_uint8, POINTER(c_uint8), POINTER(c_uint8))
    cfunc = func_type(func_ptr)

    # Call the function
    in_ptr = ctypes.cast(ctypes.byref(in_buffer), POINTER(c_uint8))
    out_ptr = ctypes.cast(ctypes.byref(out_buffer), POINTER(c_uint8))
    result = cfunc(in_ptr, out_ptr)

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
    
    return result, in_array, out_array
