from llvmlite import ir
from bytecode_compiler.utils import i256, i32, StackType, capacity, genFun
    
def genPeek(module : ir.Module, type : ir.IdentifiedStructType, error_flag : ir.GlobalVariable) -> ir.Function:
    
    # Define the 'peek' function
    peek_func = genFun(module, "stack_peek", i256, [type.as_pointer()])
    block = peek_func.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)

    # Function arguments
    stack_ptr = peek_func.args[0]

    # Access the 'top' field of the stack
    top_ptr = builder.gep(stack_ptr, [i32(0), i32(1)], name="top_ptr")
    top = builder.load(top_ptr, name="top")

    # Check if the stack is empty
    is_empty = builder.icmp_signed("==", top, i32(0), name="is_empty")
    with builder.if_then(is_empty):
        builder.store(ir.Constant(ir.IntType(1), 1), error_flag)
        builder.ret(i256(0))

    # Peek the value from the stack
    new_top = builder.sub(top, i32(1), name="new_top")
    data_ptr = builder.gep(stack_ptr, [i32(0), i32(0), new_top], name="data_ptr")
    value = builder.load(data_ptr, name="value")
    builder.ret(value)
    
    return peek_func
    
def genPush(module : ir.Module, type : ir.IdentifiedStructType, error_flag : ir.GlobalVariable) -> ir.Function:

    # Define the 'push' function
    push_func = genFun(module, "stack_push", ir.VoidType(), [type.as_pointer(), i256])
    block = push_func.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)

    # Function arguments
    stack_ptr, value = push_func.args

    # Access the 'top' field of the stack
    top_ptr = builder.gep(stack_ptr, [i32(0), i32(1)], name="top_ptr")
    top = builder.load(top_ptr, name="top")

    # Check if the stack is full
    is_full = builder.icmp_signed(">=", top, i32(capacity), name="is_full")
    with builder.if_then(is_full):
        builder.store(ir.Constant(ir.IntType(1), 1), error_flag)
        builder.ret_void()

    # Push the value onto the stack
    data_ptr = builder.gep(stack_ptr, [i32(0), i32(0), top], name="data_ptr")
    builder.store(value, data_ptr)
    new_top = builder.add(top, i32(1), name="new_top")
    builder.store(new_top, top_ptr)
    builder.ret_void()
    
    return push_func
    
def genPop(module : ir.Module, type : ir.IdentifiedStructType, error_flag : ir.GlobalVariable) -> ir.Function:
    
    # Define the 'pop' function
    pop_func = genFun(module, "stack_pop", i256, [type.as_pointer()])
    block = pop_func.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)

    # Function arguments
    stack_ptr = pop_func.args[0]

    # Access the 'top' field of the stack
    top_ptr = builder.gep(stack_ptr, [i32(0), i32(1)], name="top_ptr")
    top = builder.load(top_ptr, name="top")

    # Check if the stack is empty
    is_empty = builder.icmp_signed("==", top, i32(0), name="is_empty")
    with builder.if_then(is_empty):
        builder.store(ir.Constant(ir.IntType(1), 1), error_flag)
        builder.ret(i256(0))

    # Pop the value from the stack
    new_top = builder.sub(top, i32(1), name="new_top")
    builder.store(new_top, top_ptr)
    data_ptr = builder.gep(stack_ptr, [i32(0), i32(0), new_top], name="data_ptr")
    value = builder.load(data_ptr, name="value")
    builder.ret(value)
    
    return pop_func
    
def genStack(module : ir.Module, builder : ir.IRBuilder, error_flag : ir.GlobalVariable) -> list[ir.AllocaInstr, ir.Function, ir.Function, ir.Function]:
    
    # Allocate the stack
    stack = builder.alloca(StackType, name="stack")
    
    # initialize 'top' to 0
    top_ptr = builder.gep(stack, [i32(0), i32(1)], name="top_ptr")
    builder.store(i32(0), top_ptr)
    
    # Generate the 'peek', 'push', and 'pop' functions
    peek_func = genPeek(module, StackType, error_flag)
    push_func = genPush(module, StackType, error_flag)
    pop_func = genPop(module, StackType, error_flag)
    
    # Return the stack and functions
    return [stack, peek_func, push_func, pop_func]