from typing import NamedTuple, List, Dict, Union, Callable

from jawa.constants import FieldReference, MethodReference


class OperandType(NamedTuple("OperandType", [("size", int)])):
    size: int


Reference = OperandType(size=1)
Integer = OperandType(size=1)
Float = OperandType(size=1)
Byte = OperandType(size=1)
Short = OperandType(size=1)
Char = OperandType(size=1)
Boolean = OperandType(size=1)
Long = OperandType(size=2)
Double = OperandType(size=2)


TYPE_TO_TYPE = {
    'I': Integer,
    'J': Long,
    'F': Float,
    'D': Double,
    'B': Byte,
    'S': Short,
    'C': Char,
    'Z': Boolean,
    '[': Reference,
    'L': Reference,
}


def get_field_type(field_reference: FieldReference) -> List[OperandType]:
    return_type = field_reference.name_and_type.descriptor.value[0]
    if return_type in TYPE_TO_TYPE:
        return [TYPE_TO_TYPE[return_type]]
    else:
        return []


def get_method_return_type(method_reference: MethodReference) -> List[OperandType]:
    return_type = method_reference.name_and_type.descriptor.value[-1]
    if return_type in TYPE_TO_TYPE:
        return [TYPE_TO_TYPE[return_type]]
    else:
        return []


def get_method_input_types(method_reference: MethodReference) -> List[OperandType]:
    descriptor = method_reference.name_and_type.descriptor.value

    types = []

    i = 1

    while i < len(descriptor):
        if descriptor[i] == ')':
            break
        elif descriptor[i] == 'L':
            types.append(Reference)
            while descriptor[i] != ';':
                i += 1
        elif descriptor[i] == '[':
            types.append(Reference)
            i += 1
            if descriptor[i] == 'L':
                while descriptor[i] != ';':
                    i += 1
                i += 1
            continue
        else:
            if descriptor[i] in TYPE_TO_TYPE:
                types.append(TYPE_TO_TYPE[descriptor[i]])
            else:
                raise Exception(f'Unknown type {descriptor[i]}')
        i += 1

    return types


class InstructionInfo(NamedTuple):
    name: str
    description: str
    inputs: Union[List[OperandType], Callable[[Union[MethodReference, FieldReference]], List[OperandType]]]
    outputs: Union[List[OperandType], Callable[[Union[MethodReference, FieldReference]], List[OperandType]]]


def instance_method_input_types(method_reference: MethodReference) -> List[OperandType]:
    return [Reference, *get_method_input_types(method_reference)]


INSTRUCTIONS: Dict[int, InstructionInfo] = {
    0x00: {
        "name": "nop",
        "description": "Do nothing",
        "inputs": [],
        "outputs": [],
    },
    0x01: {
        "name": "aconst_null",
        "description": "Push null onto the stack",
        "inputs": [],
        "outputs": [Reference],
    },
    0x02: {
        "name": "iconst_m1",
        "description": "Push -1 onto the stack",
        "inputs": [],
        "outputs": [Integer],
    },
    0x03: {
        "name": "iconst_0",
        "description": "Push 0 onto the stack",
        "inputs": [],
        "outputs": [Integer],
    },
    0x04: {
        "name": "iconst_1",
        "description": "Push 1 onto the stack",
        "inputs": [],
        "outputs": [Integer],
    },
    0x05: {
        "name": "iconst_2",
        "description": "Push 2 onto the stack",
        "inputs": [],
        "outputs": [Integer],
    },
    0x06: {
        "name": "iconst_3",
        "description": "Push 3 onto the stack",
        "inputs": [],
        "outputs": [Integer],
    },
    0x07: {
        "name": "iconst_4",
        "description": "Push 4 onto the stack",
        "inputs": [],
        "outputs": [Integer],
    },
    0x08: {
        "name": "iconst_5",
        "description": "Push 5 onto the stack",
        "inputs": [],
        "outputs": [Integer],
    },
    0x09: {
        "name": "lconst_0",
        "description": "Push 0 onto the stack as a long or double",
        "inputs": [],
        "outputs": [Long],
    },
    0x0a: {
        "name": "lconst_1",
        "description": "Push 1 onto the stack as a long or double",
        "inputs": [],
        "outputs": [Long],
    },
    0x0b: {
        "name": "fconst_0",
        "description": "Push 0.0f or 0.0 onto the stack as a float or double",
        "inputs": [],
        "outputs": [Float],
    },
    0x0c: {
        "name": "fconst_1",
        "description": "Push 1.0f or 1.0 onto the stack as a float or double",
        "inputs": [],
        "outputs": [Float],
    },
    0x0d: {
        "name": "fconst_2",
        "description": "Push 2.0f or 2.0 onto the stack as a float or double",
        "inputs": [],
        "outputs": [Float],
    },
    0x0e: {
        "name": "dconst_0",
        "description": "Push 0.0 onto the stack as a double",
        "inputs": [],
        "outputs": [Double],
    },
    0x0f: {
        "name": "dconst_1",
        "description": "Push 1.0 onto the stack as a double",
        "inputs": [],
        "outputs": [Double],
    },
    0x10: {
        "name": "bipush",
        "description": "Push a byte onto the stack as an integer",
        "inputs": [],
        "outputs": [Integer],
    },
    0x11: {
        "name": "sipush",
        "description": "Push a short onto the stack as an integer",
        "inputs": [],
        "outputs": [Integer],
    },
    0x12: {
        "name": "ldc",
        "description": "Push a constant #index from a constant pool (String, int or float) onto the stack",
        "inputs": [],
        "outputs": [Reference],
    },
    0x13: {
        "name": "ldc_w",
        "description": "Push a constant #index from a constant pool (String, int or float) onto the stack",
        "inputs": [],
        "outputs": [Reference],
    },
    0x14: {
        "name": "ldc2_w",
        "description": "Push a constant #index from a constant pool (double or long) onto the stack",
        "inputs": [],
        "outputs": [Long],
    },
    0x15: {
        "name": "iload",
        "description": "Load an int from local variable #index",
        "inputs": [],
        "outputs": [Integer],
    },
    0x16: {
        "name": "lload",
        "description": "Load a long from local variable #index",
        "inputs": [],
        "outputs": [Long],
    },
    0x17: {
        "name": "fload",
        "description": "Load a float from local variable #index",
        "inputs": [],
        "outputs": [Float],
    },
    0x18: {
        "name": "dload",
        "description": "Load a double from local variable #index",
        "inputs": [],
        "outputs": [Double],
    },
    0x19: {
        "name": "aload",
        "description": "Load a reference from local variable #index",
        "inputs": [],
        "outputs": [Reference],
    },
    0x1a: {
        "name": "iload_0",
        "description": "Load an int from local variable 0",
        "inputs": [],
        "outputs": [Integer],
    },
    0x1b: {
        "name": "iload_1",
        "description": "Load an int from local variable 1",
        "inputs": [],
        "outputs": [Integer],
    },
    0x1c: {
        "name": "iload_2",
        "description": "Load an int from local variable 2",
        "inputs": [],
        "outputs": [Integer],
    },
    0x1d: {
        "name": "iload_3",
        "description": "Load an int from local variable 3",
        "inputs": [],
        "outputs": [Integer],
    },
    0x1e: {
        "name": "lload_0",
        "description": "Load a long from local variable 0",
        "inputs": [],
        "outputs": [Long],
    },
    0x1f: {
        "name": "lload_1",
        "description": "Load a long from local variable 1",
        "inputs": [],
        "outputs": [Long],
    },
    0x20: {
        "name": "lload_2",
        "description": "Load a long from local variable 2",
        "inputs": [],
        "outputs": [Long],
    },
    0x21: {
        "name": "lload_3",
        "description": "Load a long from local variable 3",
        "inputs": [],
        "outputs": [Long],
    },
    0x22: {
        "name": "fload_0",
        "description": "Load a float from local variable 0",
        "inputs": [],
        "outputs": [Float],
    },
    0x23: {
        "name": "fload_1",
        "description": "Load a float from local variable 1",
        "inputs": [],
        "outputs": [Float],
    },
    0x24: {
        "name": "fload_2",
        "description": "Load a float from local variable 2",
        "inputs": [],
        "outputs": [Float],
    },
    0x25: {
        "name": "fload_3",
        "description": "Load a float from local variable 3",
        "inputs": [],
        "outputs": [Float],
    },
    0x26: {
        "name": "dload_0",
        "description": "Load a double from local variable 0",
        "inputs": [],
        "outputs": [Double],
    },
    0x27: {
        "name": "dload_1",
        "description": "Load a double from local variable 1",
        "inputs": [],
        "outputs": [Double],
    },
    0x28: {
        "name": "dload_2",
        "description": "Load a double from local variable 2",
        "inputs": [],
        "outputs": [Double],
    },
    0x29: {
        "name": "dload_3",
        "description": "Load a double from local variable 3",
        "inputs": [],
        "outputs": [Double],
    },
    0x2a: {
        "name": "aload_0",
        "description": "Load a reference from local variable 0",
        "inputs": [],
        "outputs": [Reference],
    },
    0x2b: {
        "name": "aload_1",
        "description": "Load a reference from local variable 1",
        "inputs": [],
        "outputs": [Reference],
    },
    0x2c: {
        "name": "aload_2",
        "description": "Load a reference from local variable 2",
        "inputs": [],
        "outputs": [Reference],
    },
    0x2d: {
        "name": "aload_3",
        "description": "Load a reference from local variable 3",
        "inputs": [],
        "outputs": [Reference],
    },
    0x2e: {
        "name": "iaload",
        "description": "Load an int from an array",
        "inputs": [Reference, Integer],
        "outputs": [Integer],
    },
    0x2f: {
        "name": "laload",
        "description": "Load a long from an array",
        "inputs": [Reference, Integer],
        "outputs": [Long],
    },
    0x30: {
        "name": "faload",
        "description": "Load a float from an array",
        "inputs": [Reference, Integer],
        "outputs": [Float],
    },
    0x31: {
        "name": "daload",
        "description": "Load a double from an array",
        "inputs": [Reference, Integer],
        "outputs": [Double],
    },
    0x32: {
        "name": "aaload",
        "description": "Load a reference from an array",
        "inputs": [Reference, Integer],
        "outputs": [Reference],
    },
    0x33: {
        "name": "baload",
        "description": "Load a byte from an array",
        "inputs": [Reference, Integer],
        "outputs": [Byte],
    },
    0x34: {
        "name": "caload",
        "description": "Load a char from an array",
        "inputs": [Reference, Integer],
        "outputs": [Char],
    },
    0x35: {
        "name": "saload",
        "description": "Load a short from an array",
        "inputs": [Reference, Integer],
        "outputs": [Short],
    },
    0x36: {
        "name": "istore",
        "description": "Store an int into a local variable",
        "inputs": [Integer],
        "outputs": [],
    },
    0x37: {
        "name": "lstore",
        "description": "Store a long into a local variable",
        "inputs": [Long],
        "outputs": [],
    },
    0x38: {
        "name": "fstore",
        "description": "Store a float into a local variable",
        "inputs": [Float],
        "outputs": [],
    },
    0x39: {
        "name": "dstore",
        "description": "Store a double into a local variable",
        "inputs": [Double],
        "outputs": [],
    },
    0x3a: {
        "name": "astore",
        "description": "Store a reference into a local variable",
        "inputs": [Reference],
        "outputs": [],
    },
    0x3b: {
        "name": "istore_0",
        "description": "Store an int into local variable 0",
        "inputs": [Integer],
        "outputs": [],
    },
    0x3c: {
        "name": "istore_1",
        "description": "Store an int into local variable 1",
        "inputs": [Integer],
        "outputs": [],
    },
    0x3d: {
        "name": "istore_2",
        "description": "Store an int into local variable 2",
        "inputs": [Integer],
        "outputs": [],
    },
    0x3e: {
        "name": "istore_3",
        "description": "Store an int into local variable 3",
        "inputs": [Integer],
        "outputs": [],
    },
    0x3f: {
        "name": "lstore_0",
        "description": "Store a long into local variable 0",
        "inputs": [Long],
        "outputs": [],
    },
    0x40: {
        "name": "lstore_1",
        "description": "Store a long into local variable 1",
        "inputs": [Long],
        "outputs": [],
    },
    0x41: {
        "name": "lstore_2",
        "description": "Store a long into local variable 2",
        "inputs": [Long],
        "outputs": [],
    },
    0x42: {
        "name": "lstore_3",
        "description": "Store a long into local variable 3",
        "inputs": [Long],
        "outputs": [],
    },
    0x43: {
        "name": "fstore_0",
        "description": "Store a float into local variable 0",
        "inputs": [Float],
        "outputs": [],
    },
    0x44: {
        "name": "fstore_1",
        "description": "Store a float into local variable 1",
        "inputs": [Float],
        "outputs": [],
    },
    0x45: {
        "name": "fstore_2",
        "description": "Store a float into local variable 2",
        "inputs": [Float],
        "outputs": [],
    },
    0x46: {
        "name": "fstore_3",
        "description": "Store a float into local variable 3",
        "inputs": [Float],
        "outputs": [],
    },
    0x47: {
        "name": "dstore_0",
        "description": "Store a double into local variable 0",
        "inputs": [Double],
        "outputs": [],
    },
    0x48: {
        "name": "dstore_1",
        "description": "Store a double into local variable 1",
        "inputs": [Double],
        "outputs": [],
    },
    0x49: {
        "name": "dstore_2",
        "description": "Store a double into local variable 2",
        "inputs": [Double],
        "outputs": [],
    },
    0x4a: {
        "name": "dstore_3",
        "description": "Store a double into local variable 3",
        "inputs": [Double],
        "outputs": [],
    },
    0x4b: {
        "name": "astore_0",
        "description": "Store a reference into local variable 0",
        "inputs": [Reference],
        "outputs": [],
    },
    0x4c: {
        "name": "astore_1",
        "description": "Store a reference into local variable 1",
        "inputs": [Reference],
        "outputs": [],
    },
    0x4d: {
        "name": "astore_2",
        "description": "Store a reference into local variable 2",
        "inputs": [Reference],
        "outputs": [],
    },
    0x4e: {
        "name": "astore_3",
        "description": "Store a reference into local variable 3",
        "inputs": [Reference],
        "outputs": [],
    },
    0x4f: {
        "name": "iastore",
        "description": "Store into int array",
        "inputs": [Reference, Integer, Integer],
        "outputs": [],
    },
    0x50: {
        "name": "lastore",
        "description": "Store into long array",
        "inputs": [Reference, Integer, Long],
        "outputs": [],
    },
    0x51: {
        "name": "fastore",
        "description": "Store into float array",
        "inputs": [Reference, Integer, Float],
        "outputs": [],
    },
    0x52: {
        "name": "dastore",
        "description": "Store into double array",
        "inputs": [Reference, Integer, Double],
        "outputs": [],
    },
    0x53: {
        "name": "aastore",
        "description": "Store into reference array",
        "inputs": [Reference, Integer, Reference],
        "outputs": [],
    },
    0x54: {
        "name": "bastore",
        "description": "Store into byte or boolean array",
        "inputs": [Reference, Integer, Byte],
        "outputs": [],
    },
    0x55: {
        "name": "castore",
        "description": "Store into char array",
        "inputs": [Reference, Integer, Char],
        "outputs": [],
    },
    0x56: {
        "name": "sastore",
        "description": "Store into short array",
        "inputs": [Reference, Integer, Short],
        "outputs": [],
    },
    0x57: {
        "name": "pop",
        "description": "Pop the top operand stack value",
        "inputs": [Integer],
        "outputs": [],
    },
    0x58: {
        "name": "pop2",
        "description": "Pop the top two operand stack values",
        "inputs": [Integer, Integer],
        "outputs": [],
    },
    0x59: {
        "name": "dup",
        "description": "Duplicate the top operand stack value",
        "inputs": [Integer],
        "outputs": [Integer, Integer],
    },
    0x5a: {
        "name": "dup_x1",
        "description": "Duplicate the top operand stack value and insert beneath the second-top one",
        "inputs": [Integer, Integer],
        "outputs": [Integer, Integer, Integer],
    },
    0x5b: {
        "name": "dup_x2",
        "description": "Duplicate the top operand stack value and insert beneath the one beneath it",
        "inputs": [Integer, Integer, Integer],
        "outputs": [Integer, Integer, Integer, Integer],
    },
    0x5c: {
        "name": "dup2",
        "description": "Duplicate the top two operand stack values",
        "inputs": [Integer, Integer],
        "outputs": [Integer, Integer, Integer, Integer],
    },
    0x5d: {
        "name": "dup2_x1",
        "description": "Duplicate the top two operand stack values and insert beneath the one beneath it",
        "inputs": [Integer, Integer, Integer],
        "outputs": [Integer, Integer, Integer, Integer, Integer],
    },
    0x5e: {
        "name": "dup2_x2",
        "description": "Duplicate the top two operand stack values and insert beneath the one beneath it",
        "inputs": [Integer, Integer, Integer, Integer],
        "outputs": [Integer, Integer, Integer, Integer, Integer, Integer],
    },
    0x5f: {
        "name": "swap",
        "description": "Swap the top two operand stack values",
        "inputs": [Integer, Integer],
        "outputs": [Integer, Integer],
    },
    0x60: {
        "name": "iadd",
        "description": "Add two integers",
        "inputs": [Integer, Integer],
        "outputs": [Integer],
    },
    0x61: {
        "name": "ladd",
        "description": "Add two longs",
        "inputs": [Long, Long],
        "outputs": [Long],
    },
    0x62: {
        "name": "fadd",
        "description": "Add two floats",
        "inputs": [Float, Float],
        "outputs": [Float],
    },
    0x63: {
        "name": "dadd",
        "description": "Add two doubles",
        "inputs": [Double, Double],
        "outputs": [Double],
    },
    0x64: {
        "name": "isub",
        "description": "Subtract two integers",
        "inputs": [Integer, Integer],
        "outputs": [Integer],
    },
    0x65: {
        "name": "lsub",
        "description": "Subtract two longs",
        "inputs": [Long, Long],
        "outputs": [Long],
    },
    0x66: {
        "name": "fsub",
        "description": "Subtract two floats",
        "inputs": [Float, Float],
        "outputs": [Float],
    },
    0x67: {
        "name": "dsub",
        "description": "Subtract two doubles",
        "inputs": [Double, Double],
        "outputs": [Double],
    },
    0x68: {
        "name": "imul",
        "description": "Multiply two integers",
        "inputs": [Integer, Integer],
        "outputs": [Integer],
    },
    0x69: {
        "name": "lmul",
        "description": "Multiply two longs",
        "inputs": [Long, Long],
        "outputs": [Long],
    },
    0x6a: {
        "name": "fmul",
        "description": "Multiply two floats",
        "inputs": [Float, Float],
        "outputs": [Float],
    },
    0x6b: {
        "name": "dmul",
        "description": "Multiply two doubles",
        "inputs": [Double, Double],
        "outputs": [Double],
    },
    0x6c: {
        "name": "idiv",
        "description": "Divide two integers",
        "inputs": [Integer, Integer],
        "outputs": [Integer],
    },
    0x6d: {
        "name": "ldiv",
        "description": "Divide two longs",
        "inputs": [Long, Long],
        "outputs": [Long],
    },
    0x6e: {
        "name": "fdiv",
        "description": "Divide two floats",
        "inputs": [Float, Float],
        "outputs": [Float],
    },
    0x6f: {
        "name": "ddiv",
        "description": "Divide two doubles",
        "inputs": [Double, Double],
        "outputs": [Double],
    },
    0x70: {
        "name": "irem",
        "description": "Remainder of two integers",
        "inputs": [Integer, Integer],
        "outputs": [Integer],
    },
    0x71: {
        "name": "lrem",
        "description": "Remainder of two longs",
        "inputs": [Long, Long],
        "outputs": [Long],
    },
    0x72: {
        "name": "frem",
        "description": "Remainder of two floats",
        "inputs": [Float, Float],
        "outputs": [Float],
    },
    0x73: {
        "name": "drem",
        "description": "Remainder of two doubles",
        "inputs": [Double, Double],
        "outputs": [Double],
    },
    0x74: {
        "name": "ineg",
        "description": "Negate an integer",
        "inputs": [Integer],
        "outputs": [Integer],
    },
    0x75: {
        "name": "lneg",
        "description": "Negate a long",
        "inputs": [Long],
        "outputs": [Long],
    },
    0x76: {
        "name": "fneg",
        "description": "Negate a float",
        "inputs": [Float],
        "outputs": [Float],
    },
    0x77: {
        "name": "dneg",
        "description": "Negate a double",
        "inputs": [Double],
        "outputs": [Double],
    },
    0x78: {
        "name": "ishl",
        "description": "Shift an integer left",
        "inputs": [Integer, Integer],
        "outputs": [Integer],
    },
    0x79: {
        "name": "lshl",
        "description": "Shift a long left",
        "inputs": [Long, Integer],
        "outputs": [Long],
    },
    0x7a: {
        "name": "ishr",
        "description": "Shift an integer right",
        "inputs": [Integer, Integer],
        "outputs": [Integer],
    },
    0x7b: {
        "name": "lshr",
        "description": "Shift a long right",
        "inputs": [Long, Integer],
        "outputs": [Long],
    },
    0x7c: {
        "name": "iushr",
        "description": "Shift an integer right",
        "inputs": [Integer, Integer],
        "outputs": [Integer],
    },
    0x7d: {
        "name": "lushr",
        "description": "Shift a long right",
        "inputs": [Long, Integer],
        "outputs": [Long],
    },
    0x7e: {
        "name": "iand",
        "description": "Bitwise and of two integers",
        "inputs": [Integer, Integer],
        "outputs": [Integer],
    },
    0x7f: {
        "name": "land",
        "description": "Bitwise and of two longs",
        "inputs": [Long, Long],
        "outputs": [Long],
    },
    0x80: {
        "name": "ior",
        "description": "Bitwise or of two integers",
        "inputs": [Integer, Integer],
        "outputs": [Integer],
    },
    0x81: {
        "name": "lor",
        "description": "Bitwise or of two longs",
        "inputs": [Long, Long],
        "outputs": [Long],
    },
    0x82: {
        "name": "ixor",
        "description": "Bitwise xor of two integers",
        "inputs": [Integer, Integer],
        "outputs": [Integer],
    },
    0x83: {
        "name": "lxor",
        "description": "Bitwise xor of two longs",
        "inputs": [Long, Long],
        "outputs": [Long],
    },
    0x84: {
        "name": "iinc",
        "description": "Increment an integer",
        "inputs": [Integer, Integer],
        "outputs": [],
    },
    0x85: {
        "name": "i2l",
        "description": "Convert an integer to a long",
        "inputs": [Integer],
        "outputs": [Long],
    },
    0x86: {
        "name": "i2f",
        "description": "Convert an integer to a float",
        "inputs": [Integer],
        "outputs": [Float],
    },
    0x87: {
        "name": "i2d",
        "description": "Convert an integer to a double",
        "inputs": [Integer],
        "outputs": [Double],
    },
    0x88: {
        "name": "l2i",
        "description": "Convert a long to an integer",
        "inputs": [Long],
        "outputs": [Integer],
    },
    0x89: {
        "name": "l2f",
        "description": "Convert a long to a float",
        "inputs": [Long],
        "outputs": [Float],
    },
    0x8a: {
        "name": "l2d",
        "description": "Convert a long to a double",
        "inputs": [Long],
        "outputs": [Double],
    },
    0x8b: {
        "name": "f2i",
        "description": "Convert a float to an integer",
        "inputs": [Float],
        "outputs": [Integer],
    },
    0x8c: {
        "name": "f2l",
        "description": "Convert a float to a long",
        "inputs": [Float],
        "outputs": [Long],
    },
    0x8d: {
        "name": "f2d",
        "description": "Convert a float to a double",
        "inputs": [Float],
        "outputs": [Double],
    },
    0x8e: {
        "name": "d2i",
        "description": "Convert a double to an integer",
        "inputs": [Double],
        "outputs": [Integer],
    },
    0x8f: {
        "name": "d2l",
        "description": "Convert a double to a long",
        "inputs": [Double],
        "outputs": [Long],
    },
    0x90: {
        "name": "d2f",
        "description": "Convert a double to a float",
        "inputs": [Double],
        "outputs": [Float],
    },
    0x91: {
        "name": "i2b",
        "description": "Convert an integer to a byte",
        "inputs": [Integer],
        "outputs": [Byte],
    },
    0x92: {
        "name": "i2c",
        "description": "Convert an integer to a character",
        "inputs": [Integer],
        "outputs": [Char],
    },
    0x93: {
        "name": "i2s",
        "description": "Convert an integer to a short",
        "inputs": [Integer],
        "outputs": [Short],
    },
    0x94: {
        "name": "lcmp",
        "description": "Compare two longs",
        "inputs": [Long, Long],
        "outputs": [Integer],
    },
    0x95: {
        "name": "fcmpl",
        "description": "Compare two floats",
        "inputs": [Float, Float],
        "outputs": [Integer],
    },
    0x96: {
        "name": "fcmpg",
        "description": "Compare two floats",
        "inputs": [Float, Float],
        "outputs": [Integer],
    },
    0x97: {
        "name": "dcmpl",
        "description": "Compare two doubles",
        "inputs": [Double, Double],
        "outputs": [Integer],
    },
    0x98: {
        "name": "dcmpg",
        "description": "Compare two doubles",
        "inputs": [Double, Double],
        "outputs": [Integer],
    },
    0x99: {
        "name": "ifeq",
        "description": "If the first value is equal to the second, branch to the specified address",
        "inputs": [Integer, Integer],
        "outputs": [],
    },
    0x9a: {
        "name": "ifne",
        "description": "If the first value is not equal to the second, branch to the specified address",
        "inputs": [Integer, Integer],
        "outputs": [],
    },
    0x9b: {
        "name": "iflt",
        "description": "If the first value is less than the second, branch to the specified address",
        "inputs": [Integer, Integer],
        "outputs": [],
    },
    0x9c: {
        "name": "ifge",
        "description": "If the first value is greater than or equal to the second, branch to the specified address",
        "inputs": [Integer, Integer],
        "outputs": [],
    },
    0x9d: {
        "name": "ifgt",
        "description": "If the first value is greater than the second, branch to the specified address",
        "inputs": [Integer, Integer],
        "outputs": [],
    },
    0x9e: {
        "name": "ifle",
        "description": "If the first value is less than or equal to the second, branch to the specified address",
        "inputs": [Integer, Integer],
        "outputs": [],
    },
    0x9f: {
        "name": "if_icmpeq",
        "description": "If the first value is equal to the second, branch to the specified address",
        "inputs": [Integer, Integer],
        "outputs": [],
    },
    0xa0: {
        "name": "if_icmpne",
        "description": "If the first value is not equal to the second, branch to the specified address",
        "inputs": [Integer, Integer],
        "outputs": [],
    },
    0xa1: {
        "name": "if_icmplt",
        "description": "If the first value is less than the second, branch to the specified address",
        "inputs": [Integer, Integer],
        "outputs": [],
    },
    0xa2: {
        "name": "if_icmpge",
        "description": "If the first value is greater than or equal to the second, branch to the specified address",
        "inputs": [Integer, Integer],
        "outputs": [],
    },
    0xa3: {
        "name": "if_icmpgt",
        "description": "If the first value is greater than the second, branch to the specified address",
        "inputs": [Integer, Integer],
        "outputs": [],
    },
    0xa4: {
        "name": "if_icmple",
        "description": "If the first value is less than or equal to the second, branch to the specified address",
        "inputs": [Integer, Integer],
        "outputs": [],
    },
    0xa5: {
        "name": "if_acmpeq",
        "description": "If the first value is equal to the second, branch to the specified address",
        "inputs": [Integer, Integer],
        "outputs": [],
    },
    0xa6: {
        "name": "if_acmpne",
        "description": "If the first value is not equal to the second, branch to the specified address",
        "inputs": [Integer, Integer],
        "outputs": [],
    },
    0xa7: {
        "name": "goto",
        "description": "Branch to the specified address",
        "inputs": [],
        "outputs": [],
    },
    0xa8: {
        "name": "jsr",
        "description": "Jump to subroutine and save return address",
        "inputs": [],
        "outputs": [Reference],
    },
    0xa9: {
        "name": "ret",
        "description": "Return from subroutine",
        "inputs": [],
        "outputs": [],
    },
    0xaa: {
        "name": "tableswitch",
        "description": "Switch on an integer value",
        "inputs": [Integer],
        "outputs": [],
    },
    0xab: {
        "name": "lookupswitch",
        "description": "Switch on a reference value",
        "inputs": [Integer],
        "outputs": [],
    },
    0xac: {
        "name": "ireturn",
        "description": "Return an integer value from a method",
        "inputs": [Integer],
        "outputs": [],
    },
    0xad: {
        "name": "lreturn",
        "description": "Return a long value from a method",
        "inputs": [Long],
        "outputs": [],
    },
    0xae: {
        "name": "freturn",
        "description": "Return a float value from a method",
        "inputs": [Float],
        "outputs": [],
    },
    0xaf: {
        "name": "dreturn",
        "description": "Return a double value from a method",
        "inputs": [Double],
        "outputs": [],
    },
    0xb0: {
        "name": "areturn",
        "description": "Return an object reference from a method",
        "inputs": [Reference],
        "outputs": [],
    },
    0xb1: {
        "name": "return",
        "description": "Return void from method",
        "inputs": [],
        "outputs": [],
    },
    0xb2: {
        "name": "getstatic",
        "description": "Get a static field value",
        "inputs": [],
        "outputs": get_field_type,
    },
    0xb3: {
        "name": "putstatic",
        "description": "Set a static field value",
        "inputs": get_field_type,
        "outputs": [],
    },
    0xb4: {
        "name": "getfield",
        "description": "Get a field value",
        "inputs": [],
        "outputs": get_field_type,
    },
    0xb5: {
        "name": "putfield",
        "description": "Set a field value",
        "inputs": get_field_type,
        "outputs": [],
    },
    0xb6: {
        "name": "invokevirtual",
        "description": "Invoke a virtual method on an object",
        "inputs": instance_method_input_types,
        "outputs": get_method_return_type,
    },
    0xb7: {
        "name": "invokespecial",
        "description": "Invoke a special method on an object",
        "inputs": instance_method_input_types,
        "outputs": get_method_return_type,
    },
    0xb8: {
        "name": "invokestatic",
        "description": "Invoke a static method",
        "inputs": get_method_input_types,
        "outputs": get_method_return_type,
    },
    0xb9: {
        "name": "invokeinterface",
        "description": "Invoke an interface method on an object",
        "inputs": instance_method_input_types,
        "outputs": get_method_return_type,
    },
    0xba: {
        "name": "invokedynamic",
        "description": "Invoke a dynamic method",
        "inputs": get_method_input_types,
        "outputs": get_method_return_type,
    },
    0xbb: {
        "name": "new",
        "description": "Create a new object",
        "inputs": [],
        "outputs": [Reference],
    },
    0xbc: {
        "name": "newarray",
        "description": "Create a new array",
        "inputs": [Integer],
        "outputs": [Reference],
    },
    0xbd: {
        "name": "anewarray",
        "description": "Create a new array of references",
        "inputs": [],
        "outputs": [Reference],
    },
    0xbe: {
        "name": "arraylength",
        "description": "Get the length of an array",
        "inputs": [Reference],
        "outputs": [Integer],
    },
    0xbf: {
        "name": "athrow",
        "description": "Throw an exception or error",
        "inputs": [Reference],
        "outputs": [Reference],
    },
    0xc0: {
        "name": "checkcast",
        "description": "Check if an object is of a certain type",
        "inputs": [Reference],
        "outputs": [Reference],
    },
    0xc1: {
        "name": "instanceof",
        "description": "Check if an object is of a certain type",
        "inputs": [Reference],
        "outputs": [Integer],
    },
    0xc2: {
        "name": "monitorenter",
        "description": "Enter monitor for an object",
        "inputs": [Reference],
        "outputs": [],
    },
    0xc3: {
        "name": "monitorexit",
        "description": "Exit monitor for an object",
        "inputs": [Reference],
        "outputs": [],
    },
    0xc4: {
        "name": "wide",
        "description": "Execute a wide instruction",
        "inputs": [],
        "outputs": [],
    },
    0xc5: {
        "name": "multianewarray",
        "description": "Create a new multi-dimensional array",
        "inputs": [],
        "outputs": [Reference],
    },
    0xc6: {
        "name": "ifnull",
        "description": "Jump if value is null",
        "inputs": [Reference],
        "outputs": [],
    },
    0xc7: {
        "name": "ifnonnull",
        "description": "Jump if value is not null",
        "inputs": [Reference],
        "outputs": [],
    },
    0xc8: {
        "name": "goto_w",
        "description": "Jump to a new location in the code",
        "inputs": [],
        "outputs": [],
    },
    0xc9: {
        "name": "jsr_w",
        "description": "Jump to a new location in the code",
        "inputs": [],
        "outputs": [Reference],
    },
    0xca: {
        "name": "breakpoint",
        "description": "Execute a breakpoint instruction",
        "inputs": [],
        "outputs": [],
    },
    0xfe: {
        "name": "impdep1",
        "description": "Implementation-dependent instruction",
        "inputs": [],
        "outputs": [],
    },
    0xff: {
        "name": "impdep2",
        "description": "Implementation-dependent instruction",
        "inputs": [],
        "outputs": [],
    },
}

INSTRUCTIONS = dict(map(lambda item: (item[0], InstructionInfo(**item[1])), INSTRUCTIONS.items()))