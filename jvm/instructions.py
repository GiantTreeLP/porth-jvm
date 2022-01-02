from collections import deque
from typing import NamedTuple, List, Dict, Union, Callable, Deque, Iterable

from jawa.assemble import assemble, Label, Instruction as AssemblyInstruction
from jawa.constants import FieldReference, MethodReference, Constant, ConstantClass, InvokeDynamic, InterfaceMethodRef

from jvm.context import GenerateContext
from jvm.intrinsics import OperandType, InstructionsType, LabelType, Instruction, Operand, \
    get_method_input_types, get_field_type, get_method_return_type
from jvm.intrinsics.stack import Stack


class InstructionInfo(NamedTuple):
    name: str
    description: str
    inputs: Union[List[OperandType], Callable[[Union[MethodReference, FieldReference]], List[OperandType]]]
    outputs: Union[List[OperandType], Callable[[Union[MethodReference, FieldReference]], List[OperandType]]]


def instance_method_input_types(method_reference: MethodReference) -> List[OperandType]:
    return [OperandType.Reference, *get_method_input_types(method_reference)]


# <editor-fold desc="Instructions" defaultstate="collapsed">
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
        "outputs": [OperandType.Reference],
    },
    0x02: {
        "name": "iconst_m1",
        "description": "Push -1 onto the stack",
        "inputs": [],
        "outputs": [OperandType.Integer],
    },
    0x03: {
        "name": "iconst_0",
        "description": "Push 0 onto the stack",
        "inputs": [],
        "outputs": [OperandType.Integer],
    },
    0x04: {
        "name": "iconst_1",
        "description": "Push 1 onto the stack",
        "inputs": [],
        "outputs": [OperandType.Integer],
    },
    0x05: {
        "name": "iconst_2",
        "description": "Push 2 onto the stack",
        "inputs": [],
        "outputs": [OperandType.Integer],
    },
    0x06: {
        "name": "iconst_3",
        "description": "Push 3 onto the stack",
        "inputs": [],
        "outputs": [OperandType.Integer],
    },
    0x07: {
        "name": "iconst_4",
        "description": "Push 4 onto the stack",
        "inputs": [],
        "outputs": [OperandType.Integer],
    },
    0x08: {
        "name": "iconst_5",
        "description": "Push 5 onto the stack",
        "inputs": [],
        "outputs": [OperandType.Integer],
    },
    0x09: {
        "name": "lconst_0",
        "description": "Push 0 onto the stack as a long or double",
        "inputs": [],
        "outputs": [OperandType.Long],
    },
    0x0a: {
        "name": "lconst_1",
        "description": "Push 1 onto the stack as a long or double",
        "inputs": [],
        "outputs": [OperandType.Long],
    },
    0x0b: {
        "name": "fconst_0",
        "description": "Push 0.0f or 0.0 onto the stack as a float or double",
        "inputs": [],
        "outputs": [OperandType.Float],
    },
    0x0c: {
        "name": "fconst_1",
        "description": "Push 1.0f or 1.0 onto the stack as a float or double",
        "inputs": [],
        "outputs": [OperandType.Float],
    },
    0x0d: {
        "name": "fconst_2",
        "description": "Push 2.0f or 2.0 onto the stack as a float or double",
        "inputs": [],
        "outputs": [OperandType.Float],
    },
    0x0e: {
        "name": "dconst_0",
        "description": "Push 0.0 onto the stack as a double",
        "inputs": [],
        "outputs": [OperandType.Double],
    },
    0x0f: {
        "name": "dconst_1",
        "description": "Push 1.0 onto the stack as a double",
        "inputs": [],
        "outputs": [OperandType.Double],
    },
    0x10: {
        "name": "bipush",
        "description": "Push a byte onto the stack as an integer",
        "inputs": [],
        "outputs": [OperandType.Integer],
    },
    0x11: {
        "name": "sipush",
        "description": "Push a short onto the stack as an integer",
        "inputs": [],
        "outputs": [OperandType.Integer],
    },
    0x12: {
        "name": "ldc",
        "description": "Push a constant #index from a constant pool (String, int or float) onto the stack",
        "inputs": [],
        "outputs": [OperandType.Reference],
    },
    0x13: {
        "name": "ldc_w",
        "description": "Push a constant #index from a constant pool (String, int or float) onto the stack",
        "inputs": [],
        "outputs": [OperandType.Reference],
    },
    0x14: {
        "name": "ldc2_w",
        "description": "Push a constant #index from a constant pool (double or long) onto the stack",
        "inputs": [],
        "outputs": [OperandType.Long],
    },
    0x15: {
        "name": "iload",
        "description": "Load an int from local variable #index",
        "inputs": [],
        "outputs": [OperandType.Integer],
    },
    0x16: {
        "name": "lload",
        "description": "Load a long from local variable #index",
        "inputs": [],
        "outputs": [OperandType.Long],
    },
    0x17: {
        "name": "fload",
        "description": "Load a float from local variable #index",
        "inputs": [],
        "outputs": [OperandType.Float],
    },
    0x18: {
        "name": "dload",
        "description": "Load a double from local variable #index",
        "inputs": [],
        "outputs": [OperandType.Double],
    },
    0x19: {
        "name": "aload",
        "description": "Load a reference from local variable #index",
        "inputs": [],
        "outputs": [OperandType.Reference],
    },
    0x1a: {
        "name": "iload_0",
        "description": "Load an int from local variable 0",
        "inputs": [],
        "outputs": [OperandType.Integer],
    },
    0x1b: {
        "name": "iload_1",
        "description": "Load an int from local variable 1",
        "inputs": [],
        "outputs": [OperandType.Integer],
    },
    0x1c: {
        "name": "iload_2",
        "description": "Load an int from local variable 2",
        "inputs": [],
        "outputs": [OperandType.Integer],
    },
    0x1d: {
        "name": "iload_3",
        "description": "Load an int from local variable 3",
        "inputs": [],
        "outputs": [OperandType.Integer],
    },
    0x1e: {
        "name": "lload_0",
        "description": "Load a long from local variable 0",
        "inputs": [],
        "outputs": [OperandType.Long],
    },
    0x1f: {
        "name": "lload_1",
        "description": "Load a long from local variable 1",
        "inputs": [],
        "outputs": [OperandType.Long],
    },
    0x20: {
        "name": "lload_2",
        "description": "Load a long from local variable 2",
        "inputs": [],
        "outputs": [OperandType.Long],
    },
    0x21: {
        "name": "lload_3",
        "description": "Load a long from local variable 3",
        "inputs": [],
        "outputs": [OperandType.Long],
    },
    0x22: {
        "name": "fload_0",
        "description": "Load a float from local variable 0",
        "inputs": [],
        "outputs": [OperandType.Float],
    },
    0x23: {
        "name": "fload_1",
        "description": "Load a float from local variable 1",
        "inputs": [],
        "outputs": [OperandType.Float],
    },
    0x24: {
        "name": "fload_2",
        "description": "Load a float from local variable 2",
        "inputs": [],
        "outputs": [OperandType.Float],
    },
    0x25: {
        "name": "fload_3",
        "description": "Load a float from local variable 3",
        "inputs": [],
        "outputs": [OperandType.Float],
    },
    0x26: {
        "name": "dload_0",
        "description": "Load a double from local variable 0",
        "inputs": [],
        "outputs": [OperandType.Double],
    },
    0x27: {
        "name": "dload_1",
        "description": "Load a double from local variable 1",
        "inputs": [],
        "outputs": [OperandType.Double],
    },
    0x28: {
        "name": "dload_2",
        "description": "Load a double from local variable 2",
        "inputs": [],
        "outputs": [OperandType.Double],
    },
    0x29: {
        "name": "dload_3",
        "description": "Load a double from local variable 3",
        "inputs": [],
        "outputs": [OperandType.Double],
    },
    0x2a: {
        "name": "aload_0",
        "description": "Load a reference from local variable 0",
        "inputs": [],
        "outputs": [OperandType.Reference],
    },
    0x2b: {
        "name": "aload_1",
        "description": "Load a reference from local variable 1",
        "inputs": [],
        "outputs": [OperandType.Reference],
    },
    0x2c: {
        "name": "aload_2",
        "description": "Load a reference from local variable 2",
        "inputs": [],
        "outputs": [OperandType.Reference],
    },
    0x2d: {
        "name": "aload_3",
        "description": "Load a reference from local variable 3",
        "inputs": [],
        "outputs": [OperandType.Reference],
    },
    0x2e: {
        "name": "iaload",
        "description": "Load an int from an array",
        "inputs": [OperandType.Reference, OperandType.Integer],
        "outputs": [OperandType.Integer],
    },
    0x2f: {
        "name": "laload",
        "description": "Load a long from an array",
        "inputs": [OperandType.Reference, OperandType.Integer],
        "outputs": [OperandType.Long],
    },
    0x30: {
        "name": "faload",
        "description": "Load a float from an array",
        "inputs": [OperandType.Reference, OperandType.Integer],
        "outputs": [OperandType.Float],
    },
    0x31: {
        "name": "daload",
        "description": "Load a double from an array",
        "inputs": [OperandType.Reference, OperandType.Integer],
        "outputs": [OperandType.Double],
    },
    0x32: {
        "name": "aaload",
        "description": "Load a reference from an array",
        "inputs": [OperandType.Reference, OperandType.Integer],
        "outputs": [OperandType.Reference],
    },
    0x33: {
        "name": "baload",
        "description": "Load a byte from an array",
        "inputs": [OperandType.Reference, OperandType.Integer],
        "outputs": [OperandType.Byte],
    },
    0x34: {
        "name": "caload",
        "description": "Load a char from an array",
        "inputs": [OperandType.Reference, OperandType.Integer],
        "outputs": [OperandType.Char],
    },
    0x35: {
        "name": "saload",
        "description": "Load a short from an array",
        "inputs": [OperandType.Reference, OperandType.Integer],
        "outputs": [OperandType.Short],
    },
    0x36: {
        "name": "istore",
        "description": "Store an int into a local variable",
        "inputs": [OperandType.Integer],
        "outputs": [],
    },
    0x37: {
        "name": "lstore",
        "description": "Store a long into a local variable",
        "inputs": [OperandType.Long],
        "outputs": [],
    },
    0x38: {
        "name": "fstore",
        "description": "Store a float into a local variable",
        "inputs": [OperandType.Float],
        "outputs": [],
    },
    0x39: {
        "name": "dstore",
        "description": "Store a double into a local variable",
        "inputs": [OperandType.Double],
        "outputs": [],
    },
    0x3a: {
        "name": "astore",
        "description": "Store a reference into a local variable",
        "inputs": [OperandType.Reference],
        "outputs": [],
    },
    0x3b: {
        "name": "istore_0",
        "description": "Store an int into local variable 0",
        "inputs": [OperandType.Integer],
        "outputs": [],
    },
    0x3c: {
        "name": "istore_1",
        "description": "Store an int into local variable 1",
        "inputs": [OperandType.Integer],
        "outputs": [],
    },
    0x3d: {
        "name": "istore_2",
        "description": "Store an int into local variable 2",
        "inputs": [OperandType.Integer],
        "outputs": [],
    },
    0x3e: {
        "name": "istore_3",
        "description": "Store an int into local variable 3",
        "inputs": [OperandType.Integer],
        "outputs": [],
    },
    0x3f: {
        "name": "lstore_0",
        "description": "Store a long into local variable 0",
        "inputs": [OperandType.Long],
        "outputs": [],
    },
    0x40: {
        "name": "lstore_1",
        "description": "Store a long into local variable 1",
        "inputs": [OperandType.Long],
        "outputs": [],
    },
    0x41: {
        "name": "lstore_2",
        "description": "Store a long into local variable 2",
        "inputs": [OperandType.Long],
        "outputs": [],
    },
    0x42: {
        "name": "lstore_3",
        "description": "Store a long into local variable 3",
        "inputs": [OperandType.Long],
        "outputs": [],
    },
    0x43: {
        "name": "fstore_0",
        "description": "Store a float into local variable 0",
        "inputs": [OperandType.Float],
        "outputs": [],
    },
    0x44: {
        "name": "fstore_1",
        "description": "Store a float into local variable 1",
        "inputs": [OperandType.Float],
        "outputs": [],
    },
    0x45: {
        "name": "fstore_2",
        "description": "Store a float into local variable 2",
        "inputs": [OperandType.Float],
        "outputs": [],
    },
    0x46: {
        "name": "fstore_3",
        "description": "Store a float into local variable 3",
        "inputs": [OperandType.Float],
        "outputs": [],
    },
    0x47: {
        "name": "dstore_0",
        "description": "Store a double into local variable 0",
        "inputs": [OperandType.Double],
        "outputs": [],
    },
    0x48: {
        "name": "dstore_1",
        "description": "Store a double into local variable 1",
        "inputs": [OperandType.Double],
        "outputs": [],
    },
    0x49: {
        "name": "dstore_2",
        "description": "Store a double into local variable 2",
        "inputs": [OperandType.Double],
        "outputs": [],
    },
    0x4a: {
        "name": "dstore_3",
        "description": "Store a double into local variable 3",
        "inputs": [OperandType.Double],
        "outputs": [],
    },
    0x4b: {
        "name": "astore_0",
        "description": "Store a reference into local variable 0",
        "inputs": [OperandType.Reference],
        "outputs": [],
    },
    0x4c: {
        "name": "astore_1",
        "description": "Store a reference into local variable 1",
        "inputs": [OperandType.Reference],
        "outputs": [],
    },
    0x4d: {
        "name": "astore_2",
        "description": "Store a reference into local variable 2",
        "inputs": [OperandType.Reference],
        "outputs": [],
    },
    0x4e: {
        "name": "astore_3",
        "description": "Store a reference into local variable 3",
        "inputs": [OperandType.Reference],
        "outputs": [],
    },
    0x4f: {
        "name": "iastore",
        "description": "Store into int array",
        "inputs": [OperandType.Reference, OperandType.Integer, OperandType.Integer],
        "outputs": [],
    },
    0x50: {
        "name": "lastore",
        "description": "Store into long array",
        "inputs": [OperandType.Reference, OperandType.Integer, OperandType.Long],
        "outputs": [],
    },
    0x51: {
        "name": "fastore",
        "description": "Store into float array",
        "inputs": [OperandType.Reference, OperandType.Integer, OperandType.Float],
        "outputs": [],
    },
    0x52: {
        "name": "dastore",
        "description": "Store into double array",
        "inputs": [OperandType.Reference, OperandType.Integer, OperandType.Double],
        "outputs": [],
    },
    0x53: {
        "name": "aastore",
        "description": "Store into reference array",
        "inputs": [OperandType.Reference, OperandType.Integer, OperandType.Reference],
        "outputs": [],
    },
    0x54: {
        "name": "bastore",
        "description": "Store into byte or boolean array",
        "inputs": [OperandType.Reference, OperandType.Integer, OperandType.Byte],
        "outputs": [],
    },
    0x55: {
        "name": "castore",
        "description": "Store into char array",
        "inputs": [OperandType.Reference, OperandType.Integer, OperandType.Char],
        "outputs": [],
    },
    0x56: {
        "name": "sastore",
        "description": "Store into short array",
        "inputs": [OperandType.Reference, OperandType.Integer, OperandType.Short],
        "outputs": [],
    },
    0x57: {
        "name": "pop",
        "description": "Pop the top operand stack value",
        "inputs": [OperandType.Integer],
        "outputs": [],
    },
    0x58: {
        "name": "pop2",
        "description": "Pop the top two operand stack values",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [],
    },
    0x59: {
        "name": "dup",
        "description": "Duplicate the top operand stack value",
        "inputs": [OperandType.Integer],
        "outputs": [OperandType.Integer, OperandType.Integer],
    },
    0x5a: {
        "name": "dup_x1",
        "description": "Duplicate the top operand stack value and insert beneath the second-top one",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [OperandType.Integer, OperandType.Integer, OperandType.Integer],
    },
    0x5b: {
        "name": "dup_x2",
        "description": "Duplicate the top operand stack value and insert beneath the one beneath it",
        "inputs": [OperandType.Integer, OperandType.Integer, OperandType.Integer],
        "outputs": [OperandType.Integer, OperandType.Integer, OperandType.Integer, OperandType.Integer],
    },
    0x5c: {
        "name": "dup2",
        "description": "Duplicate the top two operand stack values",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [OperandType.Integer, OperandType.Integer, OperandType.Integer, OperandType.Integer],
    },
    0x5d: {
        "name": "dup2_x1",
        "description": "Duplicate the top two operand stack values and insert beneath the one beneath it",
        "inputs": [OperandType.Integer, OperandType.Integer, OperandType.Integer],
        "outputs": [OperandType.Integer, OperandType.Integer, OperandType.Integer, OperandType.Integer,
                    OperandType.Integer],
    },
    0x5e: {
        "name": "dup2_x2",
        "description": "Duplicate the top two operand stack values and insert beneath the one beneath it",
        "inputs": [OperandType.Integer, OperandType.Integer, OperandType.Integer, OperandType.Integer],
        "outputs": [OperandType.Integer, OperandType.Integer, OperandType.Integer, OperandType.Integer,
                    OperandType.Integer,
                    OperandType.Integer],
    },
    0x5f: {
        "name": "swap",
        "description": "Swap the top two operand stack values",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [OperandType.Integer, OperandType.Integer],
    },
    0x60: {
        "name": "iadd",
        "description": "Add two integers",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [OperandType.Integer],
    },
    0x61: {
        "name": "ladd",
        "description": "Add two longs",
        "inputs": [OperandType.Long, OperandType.Long],
        "outputs": [OperandType.Long],
    },
    0x62: {
        "name": "fadd",
        "description": "Add two floats",
        "inputs": [OperandType.Float, OperandType.Float],
        "outputs": [OperandType.Float],
    },
    0x63: {
        "name": "dadd",
        "description": "Add two doubles",
        "inputs": [OperandType.Double, OperandType.Double],
        "outputs": [OperandType.Double],
    },
    0x64: {
        "name": "isub",
        "description": "Subtract two integers",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [OperandType.Integer],
    },
    0x65: {
        "name": "lsub",
        "description": "Subtract two longs",
        "inputs": [OperandType.Long, OperandType.Long],
        "outputs": [OperandType.Long],
    },
    0x66: {
        "name": "fsub",
        "description": "Subtract two floats",
        "inputs": [OperandType.Float, OperandType.Float],
        "outputs": [OperandType.Float],
    },
    0x67: {
        "name": "dsub",
        "description": "Subtract two doubles",
        "inputs": [OperandType.Double, OperandType.Double],
        "outputs": [OperandType.Double],
    },
    0x68: {
        "name": "imul",
        "description": "Multiply two integers",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [OperandType.Integer],
    },
    0x69: {
        "name": "lmul",
        "description": "Multiply two longs",
        "inputs": [OperandType.Long, OperandType.Long],
        "outputs": [OperandType.Long],
    },
    0x6a: {
        "name": "fmul",
        "description": "Multiply two floats",
        "inputs": [OperandType.Float, OperandType.Float],
        "outputs": [OperandType.Float],
    },
    0x6b: {
        "name": "dmul",
        "description": "Multiply two doubles",
        "inputs": [OperandType.Double, OperandType.Double],
        "outputs": [OperandType.Double],
    },
    0x6c: {
        "name": "idiv",
        "description": "Divide two integers",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [OperandType.Integer],
    },
    0x6d: {
        "name": "ldiv",
        "description": "Divide two longs",
        "inputs": [OperandType.Long, OperandType.Long],
        "outputs": [OperandType.Long],
    },
    0x6e: {
        "name": "fdiv",
        "description": "Divide two floats",
        "inputs": [OperandType.Float, OperandType.Float],
        "outputs": [OperandType.Float],
    },
    0x6f: {
        "name": "ddiv",
        "description": "Divide two doubles",
        "inputs": [OperandType.Double, OperandType.Double],
        "outputs": [OperandType.Double],
    },
    0x70: {
        "name": "irem",
        "description": "Remainder of two integers",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [OperandType.Integer],
    },
    0x71: {
        "name": "lrem",
        "description": "Remainder of two longs",
        "inputs": [OperandType.Long, OperandType.Long],
        "outputs": [OperandType.Long],
    },
    0x72: {
        "name": "frem",
        "description": "Remainder of two floats",
        "inputs": [OperandType.Float, OperandType.Float],
        "outputs": [OperandType.Float],
    },
    0x73: {
        "name": "drem",
        "description": "Remainder of two doubles",
        "inputs": [OperandType.Double, OperandType.Double],
        "outputs": [OperandType.Double],
    },
    0x74: {
        "name": "ineg",
        "description": "Negate an integer",
        "inputs": [OperandType.Integer],
        "outputs": [OperandType.Integer],
    },
    0x75: {
        "name": "lneg",
        "description": "Negate a long",
        "inputs": [OperandType.Long],
        "outputs": [OperandType.Long],
    },
    0x76: {
        "name": "fneg",
        "description": "Negate a float",
        "inputs": [OperandType.Float],
        "outputs": [OperandType.Float],
    },
    0x77: {
        "name": "dneg",
        "description": "Negate a double",
        "inputs": [OperandType.Double],
        "outputs": [OperandType.Double],
    },
    0x78: {
        "name": "ishl",
        "description": "Shift an integer left",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [OperandType.Integer],
    },
    0x79: {
        "name": "lshl",
        "description": "Shift a long left",
        "inputs": [OperandType.Long, OperandType.Integer],
        "outputs": [OperandType.Long],
    },
    0x7a: {
        "name": "ishr",
        "description": "Shift an integer right",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [OperandType.Integer],
    },
    0x7b: {
        "name": "lshr",
        "description": "Shift a long right",
        "inputs": [OperandType.Long, OperandType.Integer],
        "outputs": [OperandType.Long],
    },
    0x7c: {
        "name": "iushr",
        "description": "Shift an integer right",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [OperandType.Integer],
    },
    0x7d: {
        "name": "lushr",
        "description": "Shift a long right",
        "inputs": [OperandType.Long, OperandType.Integer],
        "outputs": [OperandType.Long],
    },
    0x7e: {
        "name": "iand",
        "description": "Bitwise and of two integers",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [OperandType.Integer],
    },
    0x7f: {
        "name": "land",
        "description": "Bitwise and of two longs",
        "inputs": [OperandType.Long, OperandType.Long],
        "outputs": [OperandType.Long],
    },
    0x80: {
        "name": "ior",
        "description": "Bitwise or of two integers",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [OperandType.Integer],
    },
    0x81: {
        "name": "lor",
        "description": "Bitwise or of two longs",
        "inputs": [OperandType.Long, OperandType.Long],
        "outputs": [OperandType.Long],
    },
    0x82: {
        "name": "ixor",
        "description": "Bitwise xor of two integers",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [OperandType.Integer],
    },
    0x83: {
        "name": "lxor",
        "description": "Bitwise xor of two longs",
        "inputs": [OperandType.Long, OperandType.Long],
        "outputs": [OperandType.Long],
    },
    0x84: {
        "name": "iinc",
        "description": "Increment an integer",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [],
    },
    0x85: {
        "name": "i2l",
        "description": "Convert an integer to a long",
        "inputs": [OperandType.Integer],
        "outputs": [OperandType.Long],
    },
    0x86: {
        "name": "i2f",
        "description": "Convert an integer to a float",
        "inputs": [OperandType.Integer],
        "outputs": [OperandType.Float],
    },
    0x87: {
        "name": "i2d",
        "description": "Convert an integer to a double",
        "inputs": [OperandType.Integer],
        "outputs": [OperandType.Double],
    },
    0x88: {
        "name": "l2i",
        "description": "Convert a long to an integer",
        "inputs": [OperandType.Long],
        "outputs": [OperandType.Integer],
    },
    0x89: {
        "name": "l2f",
        "description": "Convert a long to a float",
        "inputs": [OperandType.Long],
        "outputs": [OperandType.Float],
    },
    0x8a: {
        "name": "l2d",
        "description": "Convert a long to a double",
        "inputs": [OperandType.Long],
        "outputs": [OperandType.Double],
    },
    0x8b: {
        "name": "f2i",
        "description": "Convert a float to an integer",
        "inputs": [OperandType.Float],
        "outputs": [OperandType.Integer],
    },
    0x8c: {
        "name": "f2l",
        "description": "Convert a float to a long",
        "inputs": [OperandType.Float],
        "outputs": [OperandType.Long],
    },
    0x8d: {
        "name": "f2d",
        "description": "Convert a float to a double",
        "inputs": [OperandType.Float],
        "outputs": [OperandType.Double],
    },
    0x8e: {
        "name": "d2i",
        "description": "Convert a double to an integer",
        "inputs": [OperandType.Double],
        "outputs": [OperandType.Integer],
    },
    0x8f: {
        "name": "d2l",
        "description": "Convert a double to a long",
        "inputs": [OperandType.Double],
        "outputs": [OperandType.Long],
    },
    0x90: {
        "name": "d2f",
        "description": "Convert a double to a float",
        "inputs": [OperandType.Double],
        "outputs": [OperandType.Float],
    },
    0x91: {
        "name": "i2b",
        "description": "Convert an integer to a byte",
        "inputs": [OperandType.Integer],
        "outputs": [OperandType.Byte],
    },
    0x92: {
        "name": "i2c",
        "description": "Convert an integer to a character",
        "inputs": [OperandType.Integer],
        "outputs": [OperandType.Char],
    },
    0x93: {
        "name": "i2s",
        "description": "Convert an integer to a short",
        "inputs": [OperandType.Integer],
        "outputs": [OperandType.Short],
    },
    0x94: {
        "name": "lcmp",
        "description": "Compare two longs",
        "inputs": [OperandType.Long, OperandType.Long],
        "outputs": [OperandType.Integer],
    },
    0x95: {
        "name": "fcmpl",
        "description": "Compare two floats",
        "inputs": [OperandType.Float, OperandType.Float],
        "outputs": [OperandType.Integer],
    },
    0x96: {
        "name": "fcmpg",
        "description": "Compare two floats",
        "inputs": [OperandType.Float, OperandType.Float],
        "outputs": [OperandType.Integer],
    },
    0x97: {
        "name": "dcmpl",
        "description": "Compare two doubles",
        "inputs": [OperandType.Double, OperandType.Double],
        "outputs": [OperandType.Integer],
    },
    0x98: {
        "name": "dcmpg",
        "description": "Compare two doubles",
        "inputs": [OperandType.Double, OperandType.Double],
        "outputs": [OperandType.Integer],
    },
    0x99: {
        "name": "ifeq",
        "description": "If the first value is equal to the second, branch to the specified address",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [],
    },
    0x9a: {
        "name": "ifne",
        "description": "If the first value is not equal to the second, branch to the specified address",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [],
    },
    0x9b: {
        "name": "iflt",
        "description": "If the first value is less than the second, branch to the specified address",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [],
    },
    0x9c: {
        "name": "ifge",
        "description": "If the first value is greater than or equal to the second, branch to the specified address",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [],
    },
    0x9d: {
        "name": "ifgt",
        "description": "If the first value is greater than the second, branch to the specified address",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [],
    },
    0x9e: {
        "name": "ifle",
        "description": "If the first value is less than or equal to the second, branch to the specified address",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [],
    },
    0x9f: {
        "name": "if_icmpeq",
        "description": "If the first value is equal to the second, branch to the specified address",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [],
    },
    0xa0: {
        "name": "if_icmpne",
        "description": "If the first value is not equal to the second, branch to the specified address",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [],
    },
    0xa1: {
        "name": "if_icmplt",
        "description": "If the first value is less than the second, branch to the specified address",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [],
    },
    0xa2: {
        "name": "if_icmpge",
        "description": "If the first value is greater than or equal to the second, branch to the specified address",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [],
    },
    0xa3: {
        "name": "if_icmpgt",
        "description": "If the first value is greater than the second, branch to the specified address",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [],
    },
    0xa4: {
        "name": "if_icmple",
        "description": "If the first value is less than or equal to the second, branch to the specified address",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [],
    },
    0xa5: {
        "name": "if_acmpeq",
        "description": "If the first value is equal to the second, branch to the specified address",
        "inputs": [OperandType.Integer, OperandType.Integer],
        "outputs": [],
    },
    0xa6: {
        "name": "if_acmpne",
        "description": "If the first value is not equal to the second, branch to the specified address",
        "inputs": [OperandType.Integer, OperandType.Integer],
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
        "outputs": [OperandType.Reference],
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
        "inputs": [OperandType.Integer],
        "outputs": [],
    },
    0xab: {
        "name": "lookupswitch",
        "description": "Switch on a reference value",
        "inputs": [OperandType.Integer],
        "outputs": [],
    },
    0xac: {
        "name": "ireturn",
        "description": "Return an integer value from a method",
        "inputs": [OperandType.Integer],
        "outputs": [],
    },
    0xad: {
        "name": "lreturn",
        "description": "Return a long value from a method",
        "inputs": [OperandType.Long],
        "outputs": [],
    },
    0xae: {
        "name": "freturn",
        "description": "Return a float value from a method",
        "inputs": [OperandType.Float],
        "outputs": [],
    },
    0xaf: {
        "name": "dreturn",
        "description": "Return a double value from a method",
        "inputs": [OperandType.Double],
        "outputs": [],
    },
    0xb0: {
        "name": "areturn",
        "description": "Return an object reference from a method",
        "inputs": [OperandType.Reference],
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
        "outputs": [OperandType.Reference],
    },
    0xbc: {
        "name": "newarray",
        "description": "Create a new array",
        "inputs": [OperandType.Integer],
        "outputs": [OperandType.Reference],
    },
    0xbd: {
        "name": "anewarray",
        "description": "Create a new array of references",
        "inputs": [],
        "outputs": [OperandType.Reference],
    },
    0xbe: {
        "name": "arraylength",
        "description": "Get the length of an array",
        "inputs": [OperandType.Reference],
        "outputs": [OperandType.Integer],
    },
    0xbf: {
        "name": "athrow",
        "description": "Throw an exception or error",
        "inputs": [OperandType.Reference],
        "outputs": [OperandType.Reference],
    },
    0xc0: {
        "name": "checkcast",
        "description": "Check if an object is of a certain type",
        "inputs": [OperandType.Reference],
        "outputs": [OperandType.Reference],
    },
    0xc1: {
        "name": "instanceof",
        "description": "Check if an object is of a certain type",
        "inputs": [OperandType.Reference],
        "outputs": [OperandType.Integer],
    },
    0xc2: {
        "name": "monitorenter",
        "description": "Enter monitor for an object",
        "inputs": [OperandType.Reference],
        "outputs": [],
    },
    0xc3: {
        "name": "monitorexit",
        "description": "Exit monitor for an object",
        "inputs": [OperandType.Reference],
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
        "outputs": [OperandType.Reference],
    },
    0xc6: {
        "name": "ifnull",
        "description": "Jump if value is null",
        "inputs": [OperandType.Reference],
        "outputs": [],
    },
    0xc7: {
        "name": "ifnonnull",
        "description": "Jump if value is not null",
        "inputs": [OperandType.Reference],
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
        "outputs": [OperandType.Reference],
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
# </editor-fold>

INSTRUCTIONS = dict(map(lambda item: (item[0], InstructionInfo(**item[1])), INSTRUCTIONS.items()))
INSTRUCTIONS_BY_NAME: Dict[str, InstructionInfo] = dict(map(lambda item: (item[1].name, item[1]), INSTRUCTIONS.items()))


class Instructions(object):
    _context: GenerateContext
    _instructions: Deque[InstructionsType]
    _stack: Stack

    def __init__(self, context: GenerateContext):
        self._instructions = deque()
        self._stack = Stack()
        self._context = context

    @property
    def instructions(self):
        return self._instructions.copy()

    @property
    def stack(self):
        return self._stack

    @staticmethod
    def _map_label(label: LabelType) -> Label:
        if isinstance(label, Label):
            return label
        else:
            return Label(label)

    def assemble(self) -> List[AssemblyInstruction]:
        return assemble(self._instructions)

    def append(self, instruction: Instruction, *operands: Operand) -> 'Instructions':
        if isinstance(instruction, Label):
            self._instructions.append(instruction)
        else:
            self._instructions.append((instruction, *operands))
            self._stack.update_stack(instruction, *operands)
        return self

    def end_branch(self):
        self._stack.restore_stack()

    def else_branch(self):
        pass

    def label(self, name: LabelType) -> 'Instructions':
        return self.append(self._map_label(name))

    def push_constant(self, constant: Constant) -> 'Instructions':
        if constant.index <= 255:
            self.append("ldc", constant)
        else:
            self.append("ldc_w", constant)
        return self

    def push_long(self, long: int) -> 'Instructions':
        if long == 0:
            self.append("lconst_0")
        elif long == 1:
            self.append("lconst_1")
        elif long in range(-128, 128):
            self.append("bipush", long)
            self.append("i2l")
        elif long in range(-32768, 32768):
            self.append("sipush", long)
            self.append("i2l")
        elif long in range(-2147483648, 2147483648):
            self.push_constant(self._context.cf.constants.create_integer(long))
            self.append("i2l")
        elif long in range(-9223372036854775808, 9223372036854775808):
            self.append("ldc2_w", self._context.cf.constants.create_long(long))
        else:
            raise ValueError(f"{long} greater than MAX_LONG")
        return self

    def push_integer(self, integer: int) -> 'Instructions':
        if integer < -32768:
            self.push_constant(self._context.cf.constants.create_integer(integer))
        elif integer < -128:
            self.append("sipush", integer)
        elif integer < -1:
            self.append("bipush", integer)
        elif integer == -1:
            self.append("iconst_m1")
        elif integer <= 5:
            self.append(f"iconst_{integer}")
        elif integer <= 127:
            self.append("bipush", integer)
        elif integer <= 32767:
            self.append("sipush", integer)
        elif integer <= 2147483647:
            self.push_constant(self._context.cf.constants.create_integer(integer))
        else:
            raise ValueError(f"{integer} greater than MAX_INT")
        return self

    # <editor-fold desc="Drops/Pops" defaultstate="collapsed" defaultstate="collapsed">
    def pop(self) -> 'Instructions':
        return self.append("pop")

    def pop2(self) -> 'Instructions':
        return self.append("pop2")

    def drop(self) -> 'Instructions':
        return self.pop()

    def drop_long(self):
        return self.pop2()

    def drop_double(self):
        return self.pop2()

    # </editor-fold>

    # <editor-fold desc="Loads" defaultstate="collapsed" defaultstate="collapsed">
    def load_reference(self, index: int) -> 'Instructions':
        if 0 >= index >= 3:
            return self.append(f"aload_{index}")
        else:
            return self.append("aload", index)

    def load_double(self, index: int) -> 'Instructions':
        if 0 >= index >= 3:
            return self.append(f"dload_{index}")
        else:
            return self.append("dload", index)

    def load_float(self, index: int) -> 'Instructions':
        if 0 >= index >= 3:
            return self.append(f"fload_{index}")
        else:
            return self.append("fload", index)

    def load_integer(self, index: int) -> 'Instructions':
        if 0 >= index >= 3:
            return self.append(f"iload_{index}")
        else:
            return self.append("iload", index)

    def load_long(self, index: int) -> 'Instructions':
        if 0 >= index >= 3:
            return self.append(f"lload_{index}")
        else:
            return self.append("lload", index)

    # </editor-fold>

    # <editor-fold desc="Stores" defaultstate="collapsed">
    def store_reference(self, index: int) -> 'Instructions':
        if 0 >= index >= 3:
            return self.append(f"astore_{index}")
        else:
            return self.append("astore", index)

    def store_double(self, index: int) -> 'Instructions':
        if 0 >= index >= 3:
            return self.append(f"dstore_{index}")
        else:
            return self.append("dstore", index)

    def store_float(self, index: int) -> 'Instructions':
        if 0 >= index >= 3:
            return self.append(f"fstore_{index}")
        else:
            return self.append("fstore", index)

    def store_integer(self, index: int) -> 'Instructions':
        if 0 >= index >= 3:
            return self.append(f"istore_{index}")
        else:
            return self.append("istore", index)

    def store_long(self, index: int) -> 'Instructions':
        if 0 >= index >= 3:
            return self.append(f"lstore_{index}")
        else:
            return self.append("lstore", index)

    # </editor-fold>

    # <editor-fold desc="Increments/Decrements" defaultstate="collapsed">

    def increment_integer(self, index: int, value: int = 1) -> 'Instructions':
        return self.append("iinc", index, value)

    # </editor-fold>

    # <editor-fold desc="Array operations" defaultstate="collapsed">
    def array_length(self) -> 'Instructions':
        return self.append("arraylength")

    def new_array(self, primitive_type: int) -> 'Instructions':
        return self.append("newarray", primitive_type)

    def new_reference_array(self, reference_type: ConstantClass) -> 'Instructions':
        return self.append("anewarray", reference_type)

    def new_multi_dimension_reference_array(self, reference_type: ConstantClass, dimensions: int) -> 'Instructions':
        return self.append("multianewarray", reference_type, dimensions)

    # <editor-fold desc="Load from array" defaultstate="collapsed">
    def load_array_reference(self) -> 'Instructions':
        return self.append("aaload")

    def load_array_double(self) -> 'Instructions':
        return self.append("daload")

    def load_array_float(self) -> 'Instructions':
        return self.append("faload")

    def load_array_integer(self) -> 'Instructions':
        return self.append("iaload")

    def load_array_long(self) -> 'Instructions':
        return self.append("laload")

    def load_array_short(self) -> 'Instructions':
        return self.append("saload")

    def load_array_byte(self) -> 'Instructions':
        return self.append("baload")

    def load_array_char(self) -> 'Instructions':
        return self.append("caload")

    def load_array_boolean(self) -> 'Instructions':
        return self.load_array_byte()

    # </editor-fold>

    # <editor-fold desc="Store to array" defaultstate="collapsed">
    def store_array_reference(self) -> 'Instructions':
        return self.append("aastore")

    def store_array_double(self) -> 'Instructions':
        return self.append("dastore")

    def store_array_float(self) -> 'Instructions':
        return self.append("fastore")

    def store_array_integer(self) -> 'Instructions':
        return self.append("iastore")

    def store_array_long(self) -> 'Instructions':
        return self.append("lastore")

    def store_array_short(self) -> 'Instructions':
        return self.append("sastore")

    def store_array_byte(self) -> 'Instructions':
        return self.append("bastore")

    def store_array_char(self) -> 'Instructions':
        return self.append("castore")

    def store_array_boolean(self) -> 'Instructions':
        return self.store_array_byte()

    # </editor-fold>

    # </editor-fold>

    # <editor-fold desc="Conversions" defaultstate="collapsed">
    def convert_double_to_float(self) -> 'Instructions':
        return self.append("d2f")

    def convert_double_to_integer(self) -> 'Instructions':
        return self.append("d2i")

    def convert_double_to_long(self) -> 'Instructions':
        return self.append("d2l")

    def convert_float_to_double(self) -> 'Instructions':
        return self.append("f2d")

    def convert_float_to_integer(self) -> 'Instructions':
        return self.append("f2i")

    def convert_float_to_long(self) -> 'Instructions':
        return self.append("f2l")

    def convert_integer_to_byte(self) -> 'Instructions':
        return self.append("i2b")

    def convert_integer_to_char(self) -> 'Instructions':
        return self.append("i2c")

    def convert_integer_to_double(self) -> 'Instructions':
        return self.append("i2d")

    def convert_integer_to_float(self) -> 'Instructions':
        return self.append("i2f")

    def convert_integer_to_long(self) -> 'Instructions':
        return self.append("i2l")

    def convert_integer_to_short(self) -> 'Instructions':
        return self.append("i2s")

    def convert_long_to_double(self) -> 'Instructions':
        return self.append("l2d")

    def convert_long_to_float(self) -> 'Instructions':
        return self.append("l2f")

    def convert_long_to_integer(self) -> 'Instructions':
        return self.append("l2i")

    # </editor-fold>

    # <editor-fold desc="Duplications" defaultstate="collapsed">
    def duplicate_top_of_stack(self) -> 'Instructions':
        return self.append("dup")

    def duplicate_top_2_of_stack(self) -> 'Instructions':
        return self.append("dup2")

    def duplicate_long(self) -> 'Instructions':
        return self.duplicate_top_2_of_stack()

    def duplicate_double(self) -> 'Instructions':
        return self.duplicate_top_2_of_stack()

    def duplicate_behind_top_of_stack(self) -> 'Instructions':
        return self.append("dup_x1")

    def duplicate_behind_top_2_of_stack(self) -> 'Instructions':
        return self.append("dup_x2")

    def duplicate_short_behind_long(self) -> 'Instructions':
        return self.duplicate_behind_top_2_of_stack()

    def duplicate_short_behind_double(self) -> 'Instructions':
        return self.duplicate_behind_top_2_of_stack()

    def duplicate_top_2_behind_top_3_of_stack(self) -> 'Instructions':
        return self.append("dup2_x1")

    def duplicate_long_behind_short(self) -> 'Instructions':
        return self.duplicate_top_2_behind_top_3_of_stack()

    def duplicate_double_behind_short(self) -> 'Instructions':
        return self.duplicate_top_2_behind_top_3_of_stack()

    def duplicate_top_2_behind_top_4_of_stack(self) -> 'Instructions':
        return self.append("dup2_x2")

    def duplicate_long_behind_top_3_of_stack(self) -> 'Instructions':
        return self.duplicate_top_2_behind_top_4_of_stack()

    def duplicate_double_behind_top_3_of_stack(self) -> 'Instructions':
        return self.duplicate_top_2_behind_top_4_of_stack()

    def duplicate_top_2_behind_long(self) -> 'Instructions':
        return self.duplicate_top_2_behind_top_4_of_stack()

    def duplicate_top_2_behind_double(self) -> 'Instructions':
        return self.duplicate_top_2_behind_top_4_of_stack()

    def duplicate_long_behind_long(self) -> 'Instructions':
        return self.duplicate_top_2_behind_top_4_of_stack()

    def duplicate_double_behind_double(self) -> 'Instructions':
        return self.duplicate_top_2_behind_top_4_of_stack()

    # </editor-fold>

    # <editor-fold desc="Swaps" defaultstate="collapsed">
    def swap(self) -> 'Instructions':
        return self.append("swap")

    def swap_longs(self) -> 'Instructions':
        return self.duplicate_long_behind_long().drop_long()

    def swap_doubles(self) -> 'Instructions':
        return self.duplicate_double_behind_double().drop_double()

    def move_short_behind_long(self) -> 'Instructions':
        return self.duplicate_short_behind_long().pop()

    def move_short_behind_top_2_of_stack(self) -> 'Instructions':
        return self.duplicate_behind_top_2_of_stack().pop()

    def move_long_behind_short(self) -> 'Instructions':
        return self.duplicate_long_behind_short().drop_long()

    def move_top_2_behind_long(self) -> 'Instructions':
        return self.duplicate_top_2_behind_long().drop_long()

    # </editor-fold>

    # <editor-fold desc="Arithmetic" defaultstate="collapsed">

    # <editor-fold desc="Addition" defaultstate="collapsed">
    def add_integer(self) -> 'Instructions':
        return self.append("iadd")

    def add_long(self) -> 'Instructions':
        return self.append("ladd")

    def add_double(self) -> 'Instructions':
        return self.append("dadd")

    def add_float(self) -> 'Instructions':
        return self.append("fadd")

    # </editor-fold>

    # <editor-fold desc="Subtraction" defaultstate="collapsed">
    def subtract_integer(self) -> 'Instructions':
        return self.append("isub")

    def subtract_long(self) -> 'Instructions':
        return self.append("lsub")

    def subtract_double(self) -> 'Instructions':
        return self.append("dsub")

    def subtract_float(self) -> 'Instructions':
        return self.append("fsub")

    # </editor-fold>

    # <editor-fold desc="Multiplication" defaultstate="collapsed">
    def multiply_integer(self) -> 'Instructions':
        return self.append("imul")

    def multiply_long(self) -> 'Instructions':
        return self.append("lmul")

    def multiply_double(self) -> 'Instructions':
        return self.append("dmul")

    def multiply_float(self) -> 'Instructions':
        return self.append("fmul")

    # </editor-fold>

    # <editor-fold desc="Division" defaultstate="collapsed">
    def divide_integer(self) -> 'Instructions':
        return self.append("idiv")

    def divide_long(self) -> 'Instructions':
        return self.append("ldiv")

    def divide_double(self) -> 'Instructions':
        return self.append("ddiv")

    def divide_float(self) -> 'Instructions':
        return self.append("fdiv")

    # </editor-fold>

    # <editor-fold desc="Remainder/Modulo" defaultstate="collapsed">
    def remainder_integer(self) -> 'Instructions':
        return self.append("irem")

    def remainder_long(self) -> 'Instructions':
        return self.append("lrem")

    def remainder_double(self) -> 'Instructions':
        return self.append("drem")

    def remainder_float(self) -> 'Instructions':
        return self.append("frem")

    # </editor-fold>
    # </editor-fold>

    # <editor-fold desc="Bitwise" defaultstate="collapsed">
    # <editor-fold desc="Negation" defaultstate="collapsed">
    def negate_integer(self) -> 'Instructions':
        return self.append("ineg")

    def negate_long(self) -> 'Instructions':
        return self.append("lneg")

    def negate_double(self) -> 'Instructions':
        return self.append("dneg")

    def negate_float(self) -> 'Instructions':
        return self.append("fneg")

    # </editor-fold>

    # <editor-fold desc="Shifts" defaultstate="collapsed">
    # <editor-fold desc="Shift left" defaultstate="collapsed">
    def shift_left_integer(self) -> 'Instructions':
        return self.append("ishl")

    def shift_left_long(self) -> 'Instructions':
        return self.append("lshl")

    # </editor-fold>

    # <editor-fold desc="Shift right" defaultstate="collapsed">
    def shift_right_integer(self) -> 'Instructions':
        return self.append("ishr")

    def shift_right_long(self) -> 'Instructions':
        return self.append("lshr")

    # </editor-fold>

    # <editor-fold desc="Shift right unsigned" defaultstate="collapsed">
    def unsigned_shift_right_integer(self) -> 'Instructions':
        return self.append("iushr")

    def unsigned_shift_right_long(self) -> 'Instructions':
        return self.append("lushr")

    # </editor-fold>
    # </editor-fold>

    # <editor-fold desc="Bitwise or" defaultstate="collapsed">
    def or_integer(self) -> 'Instructions':
        return self.append("ior")

    def or_long(self) -> 'Instructions':
        return self.append("lor")

    # </editor-fold>

    # <editor-fold desc="Bitwise and" defaultstate="collapsed">
    def and_integer(self) -> 'Instructions':
        return self.append("iand")

    def and_long(self) -> 'Instructions':
        return self.append("land")

    # </editor-fold>

    # <editor-fold desc="Bitwise xor" defaultstate="collapsed">
    def xor_integer(self) -> 'Instructions':
        return self.append("ixor")

    def xor_long(self) -> 'Instructions':
        return self.append("lxor")

    # </editor-fold>
    # </editor-fold>

    # <editor-fold desc="Comparison" defaultstate="collapsed">
    def compare_long(self) -> 'Instructions':
        return self.append("lcmp")

    def compare_double(self) -> 'Instructions':
        return self.append("dcmpl")

    def compare_float(self) -> 'Instructions':
        return self.append("fcmpl")

    # </editor-fold>

    # <editor-fold desc="Branching" defaultstate="collapsed">
    def _branch(self, opcode: str, label: LabelType) -> 'Instructions':
        label = Instructions._map_label(label)
        return self.append(opcode, label)

    # <editor-fold desc="Boolean comparisons" defaultstate="collapsed">

    def branch_if_true(self, label: LabelType) -> 'Instructions':
        return self._branch("ifne", label)

    def branch_if_false(self, label: LabelType) -> 'Instructions':
        return self._branch("ifeq", label)

    # </editor-fold>

    # <editor-fold desc="Comparison (against 0, from lcmp, dcmpg or fcmpg or directly to an int or boolean)"
    # defaultstate="collapsed">
    def branch_if_less(self, label: LabelType) -> 'Instructions':
        return self._branch("iflt", label)

    def branch_if_greater(self, label: LabelType) -> 'Instructions':
        return self._branch("ifgt", label)

    def branch_if_less_or_equal(self, label: LabelType) -> 'Instructions':
        return self._branch("ifle", label)

    def branch_if_greater_or_equal(self, label: LabelType) -> 'Instructions':
        return self._branch("ifge", label)

    def branch_if_equal(self, label: LabelType) -> 'Instructions':
        return self._branch("ifeq", label)

    def branch_if_not_equal(self, label: LabelType) -> 'Instructions':
        return self._branch("ifne", label)

    # </editor-fold>

    # <editor-fold desc="Comparison between two integers" defaultstate="collapsed">
    def branch_if_integer_less(self, label: LabelType) -> 'Instructions':
        return self._branch("if_icmplt", label)

    def branch_if_integer_greater(self, label: LabelType) -> 'Instructions':
        return self._branch("if_icmpgt", label)

    def branch_if_integer_less_or_equal(self, label: LabelType) -> 'Instructions':
        return self._branch("if_icmple", label)

    def branch_if_integer_greater_or_equal(self, label: LabelType) -> 'Instructions':
        return self._branch("if_icmpge", label)

    def branch_if_integer_equal(self, label: LabelType) -> 'Instructions':
        return self._branch("if_icmpeq", label)

    def branch_if_integer_not_equal(self, label: LabelType) -> 'Instructions':
        return self._branch("if_icmpne", label)

    # </editor-fold>

    # <editor-fold desc="Comparison for reference" defaultstate="collapsed">
    def branch_if_reference_is_null(self, label: LabelType) -> 'Instructions':
        return self._branch("ifnull", label)

    def branch_if_reference_is_not_null(self, label: LabelType) -> 'Instructions':
        return self._branch("ifnonnull", label)

    # </editor-fold>

    # <editor-fold desc="Comparison between two references" defaultstate="collapsed">
    def branch_if_reference_equal(self, label: LabelType) -> 'Instructions':
        return self._branch("if_acmpeq", label)

    def branch_if_reference_not_equal(self, label: LabelType) -> 'Instructions':
        return self._branch("if_acmpne", label)

    # </editor-fold>

    # <editor-fold desc="Control flow" defaultstate="collapsed">
    def branch(self, label: LabelType) -> 'Instructions':
        return self._branch("goto", label)

    def lookup_switch(self, default: LabelType, branch_pairs: Dict[int, LabelType]) -> 'Instructions':
        default = Instructions._map_label(default)
        branch_pairs = {int(k): Instructions._map_label(v) for k, v in branch_pairs.items()}
        return self.append("lookupswitch", branch_pairs, default)

    def table_switch(self, default: LabelType, low: int, high: int, labels: Iterable[LabelType]) -> 'Instructions':
        default = Instructions._map_label(default)
        labels = [Instructions._map_label(label) for label in labels]
        return self.append("tableswitch", default, low, high, *labels)

    # </editor-fold>

    # </editor-fold>

    # <editor-fold desc="Return from method" defaultstate="collapsed">

    def return_void(self) -> 'Instructions':
        return self.append("return")

    def return_integer(self) -> 'Instructions':
        return self.append("ireturn")

    def return_float(self) -> 'Instructions':
        return self.append("freturn")

    def return_reference(self) -> 'Instructions':
        return self.append("areturn")

    def return_long(self) -> 'Instructions':
        return self.append("lreturn")

    def return_double(self) -> 'Instructions':
        return self.append("dreturn")

    # </editor-fold>

    # <editor-fold desc="Field operations" defaultstate="collapsed">

    def get_static_field(self, field: FieldReference) -> 'Instructions':
        return self.append("getstatic", field)

    def put_static_field(self, field: FieldReference) -> 'Instructions':
        return self.append("putstatic", field)

    def get_field(self, field: FieldReference) -> 'Instructions':
        return self.append("getfield", field)

    def put_field(self, field: FieldReference) -> 'Instructions':
        return self.append("putfield", field)

    # </editor-fold>

    # <editor-fold desc="Invocations" defaultstate="collapsed">

    def invoke_static(self, method: MethodReference) -> 'Instructions':
        return self.append("invokestatic", method)

    def invoke_virtual(self, method: MethodReference) -> 'Instructions':
        return self.append("invokevirtual", method)

    def invoke_special(self, method: MethodReference) -> 'Instructions':
        return self.append("invokespecial", method)

    def invoke_interface(self, method: InterfaceMethodRef) -> 'Instructions':
        return self.append("invokeinterface", method, 1, 0)

    def invoke_native(self, method: MethodReference) -> 'Instructions':
        return self.append("invokenative", method)

    def invoke_dynamic(self, method: InvokeDynamic) -> 'Instructions':
        return self.append("invokedynamic", method, 0, 0)

    # </editor-fold>

    # <editor-fold desc="References" defaultstate="collapsed">

    def new(self, class_: ConstantClass) -> 'Instructions':
        return self.append("new", class_)

    def check_cast(self, class_: ConstantClass) -> 'Instructions':
        return self.append("checkcast", class_)

    # </editor-fold>

    # <editor-fold desc="Convenience functions" defaultstate="collapsed">

    def load_byte(self, index: int) -> 'Instructions':
        shift = index * 8
        if shift != 0:
            self.push_integer(index).add_integer()

        self.get_static_field(self._context.memory_ref)
        self.swap()
        self.load_array_byte()
        self.push_integer(0xff)
        self.and_integer()

        if shift != 0:
            self.push_integer(shift).shift_left_integer()
        return self

    def load_byte_wide(self, index: int) -> 'Instructions':
        shift = index * 8
        if shift != 0:
            self.push_integer(index).add_integer()

        self.get_static_field(self._context.memory_ref)
        self.swap()
        self.load_array_byte()
        self.convert_integer_to_long()
        self.push_long(0xff)
        self.and_long()

        if shift != 0:
            self.push_integer(shift).shift_left_long()
        return self

    def store_byte(self, index: int) -> 'Instructions':
        shift = index * 8
        if index != 0:
            self.swap().push_integer(index).add_integer().swap()
        if shift != 0:
            self.push_integer(shift).unsigned_shift_right_integer()

        self.get_static_field(self._context.memory_ref).duplicate_behind_top_2_of_stack().pop().store_array_byte()
        return self

    def array_copy(self) -> 'Instructions':
        return self.invoke_static(
            self._context.cf.constants.create_method_ref(
                "java/lang/System",
                "arraycopy",
                "(Ljava/lang/Object;ILjava/lang/Object;II)V"
            )
        )

    def string_get_bytes(self) -> 'Instructions':
        return self.invoke_virtual(
            self._context.cf.constants.create_method_ref(
                "java/lang/String",
                "getBytes",
                "()[B"
            )
        )

    # </editor-fold>
