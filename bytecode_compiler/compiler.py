from llvmlite import ir, binding

def compile_bytecode(bytecode):
    """Generate LLVM IR code from bytecode."""
    # Initialize LLVM
    binding.initialize()
    binding.initialize_native_target()
    binding.initialize_native_asmprinter()  # Required for JIT compilation

    # Create a module
    module = ir.Module(name="bytecode_compiler")

    # Define data types
    i8 = ir.IntType(8)
    i256 = ir.IntType(256)
    i8ptr = ir.PointerType(i8)
    i256ptr = ir.PointerType(i256)

    # Define the function type
    func_type = ir.FunctionType(
        ir.VoidType(),      # Return type: void
        [i8ptr, i8ptr]      # Arguments: unsigned char* in, unsigned char* out
    )

    # Create the function
    function = ir.Function(module, func_type, name="function")

    # Name the arguments
    in_arg, out_arg = function.args
    in_arg.name = "in"
    out_arg.name = "out"

    # Create an entry block
    block = function.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)

    # Cast 'in' from i8* to i256*
    in_ptr = builder.bitcast(in_arg, i256ptr)
    
    # Cast 'out' from i8* to i256*
    out_ptr = builder.bitcast(out_arg, i256ptr)

    # Define constant indexes: 0 and 1
    zero = ir.Constant(ir.IntType(32), 0)
    one = ir.Constant(ir.IntType(32), 1)
    
    # Get pointer to in[0]
    in0_ptr = builder.gep(in_ptr, [zero], name='in0_ptr')
    
    # Get pointer to in[1]
    in1_ptr = builder.gep(in_ptr, [one], name='in1_ptr')
    
    # Get pointer to out[0]
    out0_ptr = builder.gep(out_ptr, [zero], name='out0_ptr')

    # Add the two numbers and store the result in out[0]
    in0 = builder.load(in0_ptr, name='in0')
    in1 = builder.load(in1_ptr, name='in1')
    sum = builder.add(in0, in1, name='sum')
    builder.store(sum, out0_ptr)
    
    # Subtract the two numbers and store the result in out[1]
    out1_ptr = builder.gep(out_ptr, [one], name='out1_ptr')
    diff = builder.sub(in0, in1, name='diff')
    builder.store(diff, out1_ptr)
    
    # Return
    builder.ret_void()

    return module