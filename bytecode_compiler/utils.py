from llvmlite import ir

# Define basic types
i8 = ir.IntType(8)
i32 = ir.IntType(32)
i256 = ir.IntType(256)
i8ptr = ir.PointerType(i8)
i256ptr = ir.PointerType(i256)

# Define stack capacity
capacity = 1024

# Define the Stack structure: struct Stack { i256 data[capacity]; i32 top; }
array_type = ir.ArrayType(i256, capacity)
StackType = ir.global_context.get_identified_type("Stack")
StackType.set_body(array_type, i32)

def genFun(module : ir.Module, name : str, returnType : ir.Type, argTypes : list[ir.Type], var_arg : bool = False) -> ir.Function:
    """Declare an LLVM function."""
    
    func_type = ir.FunctionType(returnType, argTypes, var_arg)
    return ir.Function(module, func_type, name=name)
