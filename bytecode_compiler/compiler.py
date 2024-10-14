from llvmlite import ir, binding
from bytecode_compiler.utils import i8, i32, i8ptr, i256ptr, genFun
from bytecode_compiler.stack import genStack

def initBinding():
    """Initialize LLVM."""
    
    # Initialize the new binding context
    binding.initialize()
    binding.initialize_native_target()
    binding.initialize_native_asmprinter()  # Required for JIT compilation

def compile_bytecode(bytecode : list[list[int]]) -> ir.Module:
    """Generate LLVM IR code from bytecode."""
    
    # Initialize LLVM
    initBinding()
    
    # Create a module
    module = ir.Module(name="bytecode_compiler")
    
    # Define a global variable to act as an error flag
    error_flag = ir.GlobalVariable(module, ir.IntType(1), name="error_flag")
    error_flag.initializer = ir.Constant(ir.IntType(1), 0)
    
    # Define the function type
    function = genFun(module, "function", i8, [i8ptr, i8ptr])

    # Get the arguments (and name them)
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

    # Generate the stack
    stack, peek_func, push_func, pop_func = genStack(module, builder, error_flag)
    
    errCode = { "full": 1, "empty": 2 }
    def check_error(type : str):
        # Check the error flag
        error = builder.load(error_flag)
        with builder.if_then(error):
            # reset the error flag
            builder.store(ir.Constant(ir.IntType(1), 0), error_flag)
            # exit the function
            builder.ret(i8(errCode[type]))
            
    def genPush(value):
        builder.call(push_func, [stack, value])
        check_error("full")
        
    def genPop() -> ir.Value:
        value = builder.call(pop_func, [stack])
        check_error("empty")
        return value
        
    def genPeek() -> ir.Value:
        value = builder.call(peek_func, [stack])
        check_error("empty")
        return value
    
    # Generate the function body
    for i, (opcode, *args) in enumerate(bytecode):
        if opcode == 0x00:
            # STOP
            builder.ret(i8(0))
            return module
        elif opcode == 0x01:
            # LOAD
            index = args[0]
            idx_ptr = builder.gep(in_ptr, [ir.Constant(i32, index)], name="idx_ptr")
            value = builder.load(idx_ptr, name="value")
            genPush(value)
        elif opcode == 0x02:
            # STORE
            index = args[0]
            idx_ptr = builder.gep(out_ptr, [ir.Constant(i32, index)], name="idx_ptr")
            value = genPeek()
            builder.store(value, idx_ptr)
        elif opcode == 0x03:
            # POP
            builder.call(pop_func, [stack])
        elif opcode == 0x04:
            # ADD
            value2 = genPop()
            value1 = genPop()
            result = builder.add(value1, value2)
            genPush(result)
        elif opcode == 0x05:
            # SUB
            value2 = genPop()
            value1 = genPop()
            result = builder.sub(value1, value2)
            builder.call(push_func, [stack, result])
        elif opcode == 0x06:
            # DUP
            value = genPeek()
            builder.call(push_func, [stack, value])
        else:
            raise ValueError(f"Unknown opcode {opcode} at index {i}")
