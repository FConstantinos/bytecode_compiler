import unittest
from bytecode_compiler.parser import parse_assembly
from bytecode_compiler.compiler import compile_bytecode
from bytecode_compiler.execution import execute

class TestIntegration(unittest.TestCase):

    def parse_compile_execute(self, assembly, in_array, out_array):
        
        # Parse the assembly code
        bytecode = parse_assembly(assembly)
        
        # Compile the bytecode
        module = compile_bytecode(bytecode)
        
        # Execute the module
        result, in_array, out_array = execute(in_array, out_array, module)
        
        return result, in_array, out_array
    
    def test_add(self):
        assembly_code = '''
            LOAD 0
            LOAD 1
            ADD
            STORE 2
            STOP
        '''
        in_array = [10, 20] + [0] * (254)
        out_array = [0] * (256)
        expected_out_array = [0, 0, 30] + [0] * (253)
        result, actual_in_array, actual_out_array = self.parse_compile_execute(assembly_code, in_array, out_array)

        # Check the output
        self.assertEqual(actual_in_array, in_array)
        self.assertEqual(actual_out_array, expected_out_array)
        self.assertEqual(result, 0)
        
    def test_subtract(self):
        assembly_code = '''
            LOAD 0
            LOAD 1
            SUB
            STORE 2
            STOP
        '''
        in_array = [50, 20] + [0] * 254
        out_array = [0] * 256
        expected_out_array = [0, 0, 30] + [0] * 253

        result, actual_in_array, actual_out_array = self.parse_compile_execute(assembly_code, in_array, out_array)
        self.assertEqual(actual_in_array, in_array)
        self.assertEqual(actual_out_array, expected_out_array)
        self.assertEqual(result, 0)
        
    def test_duplicate(self):
        assembly_code = '''
            LOAD 0
            DUP
            STORE 0
            STORE 1
            STOP
        '''
        in_array = [42] + [0] * 255
        out_array = [0] * 256
        expected_out_array = [42, 42] + [0] * 254
        
        result, actual_in_array, actual_out_array = self.parse_compile_execute(assembly_code, in_array, out_array)
        self.assertEqual(actual_in_array, in_array)
        self.assertEqual(actual_out_array, expected_out_array)
        self.assertEqual(result, 0)
        
    def test_pop_on_empty(self):
        assembly_code = '''
            LOAD 0
            POP
            STORE 1
            STOP
        '''
        in_array = [99] + [0] * 255
        out_array = [0] * 256
        expected_out_array = [0] * 256
        result, actual_in_array, actual_out_array = self.parse_compile_execute(assembly_code, in_array, out_array)
                
        self.assertEqual(actual_in_array, in_array)
        self.assertEqual(actual_out_array, expected_out_array)
        self.assertEqual(result, 2)

    def test_stack_overflow(self):
        assembly_code = "\n".join(['LOAD 0'] * 1025 + ['STOP'])
        
        in_array = [42] + [0] * 255
        out_array = [0] * 256
        expected_out_array = [0] * 256
        
        result, actual_in_array, actual_out_array = self.parse_compile_execute(assembly_code, in_array, out_array)
                
        self.assertEqual(actual_in_array, in_array)
        self.assertEqual(actual_out_array, expected_out_array)
        self.assertEqual(result, 1)
        
    def test_invalid_instruction(self):
        assembly_code = '''
            INVALID_OP
            STOP
        '''
        in_array = [0] * 256
        out_array = [0] * 256
        with self.assertRaises(ValueError) as context:
            self.parse_compile_execute(assembly_code, in_array, out_array)
        self.assertIn("Unknown command 'INVALID_OP'", str(context.exception))
        
    def test_stop(self):
        assembly_code = '''
            LOAD 0
            STOP
            LOAD 1
            STORE 1
        '''
        in_array = [100, 200] + [0] * 254
        out_array = [0] * 256
        expected_out_array = [0] * 256  # Execution stops before LOAD 1

        result, actual_in_array, actual_out_array = self.parse_compile_execute(assembly_code, in_array, out_array)
        self.assertEqual(actual_in_array, in_array)
        self.assertEqual(actual_out_array, expected_out_array)
        self.assertEqual(result, 0)
        
    def test_empty_program(self):
        assembly_code = ''
        in_array = [0] * 256
        out_array = [0] * 256
        with self.assertRaises(ValueError):
            self.parse_compile_execute(assembly_code, in_array, out_array)
            
    def test_multiple_operations(self):
        assembly_code = '''
            LOAD 0
            LOAD 1
            ADD
            DUP
            STORE 2
            STORE 3
            POP
            LOAD 4
            SUB
            STORE 5
            STOP
        '''
        in_array = [5, 10, 0, 0, 8] + [0] * 251
        out_array = [0] * 256
        expected_out_array = [0, 0, 15, 15, 0, 7] + [0] * 250
        
        result, actual_in_array, actual_out_array = self.parse_compile_execute(assembly_code, in_array, out_array)
        self.assertEqual(actual_in_array, in_array)
        self.assertEqual(actual_out_array, expected_out_array)
        self.assertEqual(result, 0)


            