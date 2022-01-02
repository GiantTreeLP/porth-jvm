import inspect
from collections import deque
from typing import Deque, Dict, Callable, Union, TypeAlias, Tuple, Optional, Set

from jawa.constants import FieldReference, InvokeDynamic, InterfaceMethodRef, MethodReference, Constant, Integer, Float, \
    String, ConstantClass, MethodHandle, MethodType, Number, Long, Double

from jvm.intrinsics import Operand, INTEGER_TYPES, get_field_type, get_method_input_types, \
    get_method_return_type, Instruction, OperandType

OperandStack: TypeAlias = Deque[OperandType]


# <editor-fold desc="Stack operations">
# noinspection PyUnusedLocal
def no_stack_modification(stack: OperandStack) -> None:
    pass


def array_load(type_: OperandType) -> Callable[[OperandStack], None]:
    def array_load_impl(stack: OperandStack) -> None:
        if stack[-1] not in INTEGER_TYPES:
            raise Exception(f"No valid index for array load, expected size 1, got {stack[-1].size}")
        if stack[-2] != OperandType.Reference:
            raise Exception(f"No valid array reference for array load, expected reference, got {stack[-2]}")
        stack.pop()
        stack.pop()
        stack.append(type_)

    return array_load_impl


def array_store(type_: OperandType) -> Callable[[OperandStack], None]:
    def array_store_impl(stack: OperandStack) -> None:
        if stack[-1] not in INTEGER_TYPES and stack[-1] != type_:
            raise Exception(f"No valid value for array store, expected {type_}, got {stack[-1]}")
        if stack[-2] not in INTEGER_TYPES:
            raise Exception(f"No valid index for array store, expected integer, got {stack[-2]}")
        if stack[-3] != OperandType.Reference:
            raise Exception(f"No valid array reference for array store, expected reference, got {stack[-3]}")
        stack.pop()
        stack.pop()
        stack.pop()

    return array_store_impl


def push_reference(stack: OperandStack) -> None:
    stack.append(OperandType.Reference)


def push_integer(stack: OperandStack) -> None:
    stack.append(OperandType.Integer)


def push_long(stack: OperandStack) -> None:
    stack.append(OperandType.Long)


def push_float(stack: OperandStack) -> None:
    stack.append(OperandType.Float)


def push_double(stack: OperandStack) -> None:
    stack.append(OperandType.Double)


def new_array(stack: OperandStack) -> None:
    if stack[-1] not in INTEGER_TYPES:
        raise Exception(f"No valid size for new array, expected operand size 1, got {stack[-1].size}")
    stack.pop()
    stack.append(OperandType.Reference)


def pop_reference(stack: OperandStack) -> None:
    if stack[-1] != OperandType.Reference:
        raise Exception(f"No valid reference for pop reference, expected reference, got {stack[-1]}")
    stack.pop()


def pop_integer(stack: OperandStack) -> None:
    if stack[-1] not in INTEGER_TYPES:
        raise Exception(f"No valid integer for pop integer, expected integer, got {stack[-1]}")
    stack.pop()


def pop_long(stack: OperandStack) -> None:
    if stack[-1] != OperandType.Long:
        raise Exception(f"No valid long for pop long, expected long, got {stack[-1]}")
    stack.pop()


def pop_float(stack: OperandStack) -> None:
    if stack[-1] != OperandType.Float:
        raise Exception(f"No valid float for pop float, expected float, got {stack[-1]}")
    stack.pop()


def pop_double(stack: OperandStack) -> None:
    if stack[-1] != OperandType.Double:
        raise Exception(f"No valid double for pop double, expected double, got {stack[-1]}")
    stack.pop()


def pop_one(stack: OperandStack) -> None:
    if stack[-1].size != 1:
        raise Exception(f"No valid operand for pop one, expected size 1, got {stack[-1].size}")
    stack.pop()


def pop_two(stack: OperandStack) -> None:
    if stack[-1].size == 2:
        stack.pop()
    elif stack[-1].size == 1 and stack[-2].size == 1:
        stack.pop()
        stack.pop()
    else:
        raise Exception(f"No valid operand for pop two, expected size 1 and 1 or size 2,"
                        f" got {stack[-1].size} and {stack[-2].size}")


def array_length(stack: OperandStack) -> None:
    pop_reference(stack)
    stack.append(OperandType.Integer)


def throw_exception(stack: OperandStack) -> None:
    if stack[-1] != OperandType.Reference:
        raise Exception(f"No valid exception reference for throw, expected reference, got {stack[-1]}")
    stack.pop()
    stack.append(OperandType.Reference)


def check_cast(stack: OperandStack) -> None:
    if stack[-1] != OperandType.Reference:
        raise Exception(f"No valid reference for check cast, expected reference, got {stack[-1]}")
    stack.pop()
    stack.append(OperandType.Reference)


def convert(from_: OperandType, to: OperandType) -> Callable[[OperandStack], None]:
    def convert_impl(stack: OperandStack) -> None:
        if stack[-1] in INTEGER_TYPES and from_ in INTEGER_TYPES:
            stack.pop()
            stack.append(from_)
        if stack[-1] != from_:
            raise Exception(f"No valid value for convert, expected {from_}, got {stack[-1]}")
        stack.pop()
        stack.append(to)

    return convert_impl


def binary_operation(type_: OperandType) -> Callable[[OperandStack], None]:
    def binary_operation_impl(stack: OperandStack) -> None:
        if stack[-1] != type_ or stack[-2] != type_:
            if type_ not in INTEGER_TYPES and (stack[-1] not in INTEGER_TYPES or stack[-2] not in INTEGER_TYPES):
                raise Exception(
                    f"No valid value for binary operation, expected {type_}, got {stack[-1]} and {stack[-2]}")
        stack.pop()
        stack.pop()
        stack.append(type_)

    return binary_operation_impl


def unary_operation(type_: OperandType) -> Callable[[OperandStack], None]:
    def unary_operation_impl(stack: OperandStack) -> None:
        if stack[-1] != type_:
            raise Exception(f"No valid value for unary operation, expected {type_}, got {stack[-1]}")
        if stack[-1] not in INTEGER_TYPES and type_ in INTEGER_TYPES:
            raise Exception(f"No valid value for unary operation, expected {type_}, got {stack[-1]}")
        stack.pop()
        stack.append(type_)

    return unary_operation_impl


def separate_comparison(type_: OperandType) -> Callable[[OperandStack], None]:
    def separate_comparison_impl(stack: OperandStack) -> None:
        if stack[-1] != type_ or stack[-2] != type_:
            raise Exception(
                f"No valid value for separate comparison, expected {type_}, got {stack[-1]} and {stack[-2]}")
        stack.pop()
        stack.pop()
        stack.append(OperandType.Integer)

    return separate_comparison_impl


def duplicate_short(stack: OperandStack) -> None:
    if stack[-1].size != 1:
        raise Exception(f"No valid value for duplicate short, expected operand size 1, got {stack[-1].size}")
    dup = stack.pop()
    stack.append(dup)
    stack.append(dup)


def duplicate_short_behind(stack: OperandStack) -> None:
    if stack[-1].size != 1 or stack[-2].size != 1:
        raise Exception(f"No valid value for duplicate short behind, "
                        f"expected operand sizes of 1, got {stack[-1].size} and {stack[-2].size}")
    first = stack.pop()
    second = stack.pop()
    stack.append(first)
    stack.append(second)
    stack.append(first)


def duplicate_x2(stack: OperandStack) -> None:
    if stack[-1].size != 1:
        raise Exception(f"No valid value for duplicate x2, expected operand size 1, got {stack[-1].size}")
    if stack[-2].size == 1 and stack[-3].size == 1:
        first = stack.pop()
        second = stack.pop()
        third = stack.pop()
        stack.append(first)
        stack.append(third)
        stack.append(second)
        stack.append(first)
    elif stack[-2].size == 2:
        first = stack.pop()
        second = stack.pop()
        stack.append(first)
        stack.append(second)
        stack.append(first)
    else:
        raise Exception(
            f"No valid value for duplicate x2, "
            f"expected operand sizes of 1 and 1 or 2, got {stack[-1].size} and {stack[-2].size}")


def duplicate_two(stack: OperandStack) -> None:
    if stack[-1].size == 1 and stack[-2].size == 1:
        first = stack.pop()
        second = stack.pop()
        stack.append(first)
        stack.append(second)
        stack.append(first)
        stack.append(second)
    elif stack[-1].size == 2:
        first = stack.pop()
        stack.append(first)
        stack.append(first)
    else:
        raise Exception(
            f"No valid value for duplicate two, "
            f"expected operand sizes of 1 and 1 or 2, got {stack[-1].size} and {stack[-2].size}")


def duplicate_two_behind(stack: OperandStack) -> None:
    if stack[-1].size == 1 and stack[-2].size == 1 and stack[-3].size == 1:
        first = stack.pop()
        second = stack.pop()
        third = stack.pop()
        stack.append(second)
        stack.append(first)
        stack.append(third)
        stack.append(second)
        stack.append(first)
    elif stack[-1].size == 2 and stack[-2].size == 1:
        first = stack.pop()
        second = stack.pop()
        stack.append(first)
        stack.append(second)
        stack.append(first)
    else:
        raise Exception(
            f"No valid value for duplicate two behind, "
            f"expected operand sizes of 1 and 1 and 1 or 2 and 1, "
            f"got {stack[-1].size}, {stack[-2].size} and {stack[-3].size}")


def duplicate_two_x2(stack: OperandStack) -> None:
    if stack[-1].size == 1 and stack[-2].size == 1 and stack[-3].size == 1 and stack[-4].size == 1:
        first = stack.pop()
        second = stack.pop()
        third = stack.pop()
        fourth = stack.pop()
        stack.append(second)
        stack.append(first)
        stack.append(fourth)
        stack.append(third)
        stack.append(second)
        stack.append(first)
    elif stack[-1].size == 2 and stack[-2].size == 1 and stack[-3].size == 1:
        first = stack.pop()
        second = stack.pop()
        third = stack.pop()
        stack.append(first)
        stack.append(third)
        stack.append(second)
        stack.append(first)
    elif stack[-1].size == 1 and stack[-2].size == 1 and stack[-3].size == 2:
        first = stack.pop()
        second = stack.pop()
        third = stack.pop()
        stack.append(second)
        stack.append(first)
        stack.append(third)
        stack.append(second)
        stack.append(first)
    elif stack[-1].size == 2 and stack[-2].size == 2:
        first = stack.pop()
        second = stack.pop()
        stack.append(first)
        stack.append(second)
        stack.append(first)
    else:
        raise Exception(
            f"No valid value for duplicate two x2, "
            f"expected operand sizes of 1 and 1 and 1 and 1 or 2 and 1 and 1 or 1 and 1 and 2 or 2 and 2, "
            f"got {stack[-1].size}, {stack[-2].size} and {stack[-3].size} and {stack[-4].size}")


def get_field(stack: OperandStack, operands: Tuple[Operand]) -> None:
    if len(operands) != 1:
        raise Exception(f"get_field expected 1 operand, got {len(operands)}")
    operand = operands[0]
    if not isinstance(operand, FieldReference):
        raise Exception(f"get_field expected operand to be a FieldReference, got {operand}")

    if stack[-1] != OperandType.Reference:
        raise Exception(f"get_field expected reference on top of stack, got {stack[-1]}")
    else:
        type_ = get_field_type(operand)[0]
        stack.pop()
        stack.append(type_)


def get_static(stack: OperandStack, operands: Tuple[Operand]) -> None:
    if len(operands) != 1:
        raise Exception(f"get_static expected 1 operand, got {len(operands)}")
    operand = operands[0]
    if not isinstance(operand, FieldReference):
        raise Exception(f"get_static expected operand to be a FieldReference, got {operand}")

    field_type = get_field_type(operand)[0]
    stack.append(field_type)


def branch_compare_references(stack: OperandStack) -> None:
    if stack[-1] != OperandType.Reference or stack[-2] != OperandType.Reference:
        raise Exception(f"branch_compare_references expected operands of reference, got {stack[-1]} and {stack[-2]}")
    else:
        stack.pop()
        stack.pop()


def branch_compare_integers(stack: OperandStack) -> None:
    if stack[-1] not in INTEGER_TYPES or stack[-2] not in INTEGER_TYPES:
        raise Exception(f"branch_compare_integers expected operands of integer, got {stack[-1]} and {stack[-2]}")
    else:
        stack.pop()
        stack.pop()


def instance_of(stack: OperandStack) -> None:
    if stack[-1] != OperandType.Reference:
        raise Exception(f"instance_of expected reference on top of stack, got {stack[-1]}")
    else:
        stack.pop()
        stack.append(OperandType.Boolean)


def invoke_static(stack: OperandStack, operands: Tuple[Operand]) -> None:
    if len(operands) < 1:
        raise Exception(f"invoke_static expected at least 1 operand, got {len(operands)}")
    invocation = operands[0]
    if not isinstance(invocation, (MethodReference, InvokeDynamic)):
        raise Exception(f"invoke_static expected operand to be a static method reference, got {invocation}")
    input_types = get_method_input_types(invocation)
    return_type = get_method_return_type(invocation)[0]

    for input_type in reversed(input_types):
        if stack[-1] != input_type:
            raise Exception(f"invoke_static expected operand to be {input_type}, got {stack[-1]}")
        else:
            stack.pop()

    if return_type is not None:
        stack.append(return_type)


def invoke_instance(stack: OperandStack, operands: Tuple[Operand]) -> None:
    if len(operands) < 1:
        raise Exception(f"invoke_instance expected at least 1 operand, got {len(operands)}")
    invocation = operands[0]
    if not isinstance(invocation, (MethodReference, InterfaceMethodRef)):
        raise Exception(f"invoke_instance expected operand to be a method reference, got {invocation}")
    input_types = get_method_input_types(invocation)
    return_type = get_method_return_type(invocation)[0]

    if len(stack) < len(input_types) + 1:
        raise Exception(f"invoke_instance expected at least {len(input_types) + 1} operands on stack, got {len(stack)}")

    for input_type in reversed(input_types):
        if stack[-1] != input_type:
            raise Exception(f"invoke_instance expected operand to be {input_type}, got {stack[-1]}")
        else:
            stack.pop()

    if stack[-1] != OperandType.Reference:
        raise Exception(f"invoke_instance expected reference on top of stack, got {stack[-1]}")
    stack.pop()

    if return_type is not None:
        stack.append(return_type)


def new_multidimensional_array(stack: OperandStack, operands: Tuple[Operand]) -> None:
    if len(operands) != 2:
        raise Exception(f"new_multidimensional_array expected 2 operands, got {len(operands)}")
    dimensions = operands[1]
    for i in range(dimensions):
        if stack[-1] not in INTEGER_TYPES:
            raise Exception(f"new_multidimensional_array expected operand to be an integer, got {stack[-1]}")
        else:
            stack.pop()

    stack.append(OperandType.Reference)


def push_constant(stack: OperandStack, operands: Tuple[Operand]) -> None:
    if len(operands) != 1:
        raise Exception(f"push_constant expected 1 operand, got {len(operands)}")
    operand = operands[0]
    if not isinstance(operand, Constant):
        raise Exception(f"push_constant expected operand to be a Constant, got {operand}")
    if isinstance(operand, Integer):
        stack.append(OperandType.Integer)
    elif isinstance(operand, Float):
        stack.append(OperandType.Float)
    elif isinstance(operand, String):
        stack.append(OperandType.Reference)
    elif isinstance(operand, ConstantClass):
        stack.append(OperandType.Reference)
    elif isinstance(operand, MethodHandle):
        stack.append(OperandType.Reference)
    elif isinstance(operand, MethodType):
        stack.append(OperandType.Reference)
    elif isinstance(operand, InvokeDynamic):
        stack.append(OperandType.Reference)
    else:
        raise Exception(f"push_constant expected operand to be a Constant, got {operand}")


def push_constant_long(stack: OperandStack, operands: Tuple[Operand]) -> None:
    if len(operands) != 1:
        raise Exception(f"push_constant expected 1 operand, got {len(operands)}")
    operand = operands[0]
    if not isinstance(operand, Number):
        raise Exception(f"push_constant expected operand to be a Number, got {operand}")
    if isinstance(operand, Long):
        stack.append(OperandType.Long)
    elif isinstance(operand, Double):
        stack.append(OperandType.Double)
    else:
        raise Exception(f"push_constant expected operand to be a Long or Double, got {operand}")


def long_shift(stack: OperandStack) -> None:
    if stack[-1] not in INTEGER_TYPES:
        raise Exception(f"long_shift expected operand to be an integer, got {stack[-1]}")
    if stack[-2] != OperandType.Long:
        raise Exception(f"long_shift expected operand to be a long, got {stack[-2]}")
    stack.pop()
    stack.pop()
    stack.append(OperandType.Long)


def put_field(stack: OperandStack, operands: Tuple[Operand]) -> None:
    if len(operands) != 1:
        raise Exception(f"put_field expected 1 operand, got {len(operands)}")
    field = operands[0]
    if not isinstance(field, FieldReference):
        raise Exception(f"put_field expected operand to be a Field, got {field}")
    field_type = get_field_type(field)[0]
    if stack[-1] != field_type:
        raise Exception(f"put_field expected operand to be {field_type}, got {stack[-1]}")
    if stack[-2] != OperandType.Reference:
        raise Exception(f"put_field expected reference on top of stack, got {stack[-1]}")
    stack.pop()
    stack.pop()


def put_static(stack: OperandStack, operands: Tuple[Operand]) -> None:
    if len(operands) != 1:
        raise Exception(f"put_static expected 1 operand, got {len(operands)}")
    field = operands[0]
    if not isinstance(field, FieldReference):
        raise Exception(f"put_static expected operand to be a Field, got {field}")
    field_type = get_field_type(field)[0]
    if stack[-1] != field_type:
        raise Exception(f"put_static expected operand to be {field_type}, got {stack[-1]}")
    else:
        stack.pop()


def swap(stack: OperandStack) -> None:
    if stack[-1].size != 1:
        raise Exception(f"swap expected operand to be of size 1, got {stack[-1].size}")
    if stack[-2].size != 1:
        raise Exception(f"swap expected operand to be of size 1, got {stack[-2].size}")
    first = stack.pop()
    second = stack.pop()
    stack.append(first)
    stack.append(second)


# </editor-fold>

INSTRUCTION_TO_STACK_MODIFICATION: Dict[
    str, Union[
        Callable[[OperandStack], None],
        Callable[[OperandStack, Tuple[Operand]], None]
    ]
] = {
    "aaload": array_load(OperandType.Reference),
    "aastore": array_store(OperandType.Reference),
    "aconst_null": push_reference,
    "aload": push_reference,
    "aload_0": push_reference,
    "aload_1": push_reference,
    "aload_2": push_reference,
    "aload_3": push_reference,
    "anewarray": new_array,
    "areturn": pop_reference,
    "arraylength": array_length,
    "astore": pop_reference,
    "astore_0": pop_reference,
    "astore_1": pop_reference,
    "astore_2": pop_reference,
    "astore_3": pop_reference,
    "athrow": throw_exception,
    "baload": array_load(OperandType.Byte),
    "bastore": array_store(OperandType.Byte),
    "bipush": push_integer,
    "caload": array_load(OperandType.Char),
    "castore": array_store(OperandType.Char),
    "checkcast": check_cast,
    "d2f": convert(OperandType.Double, OperandType.Float),
    "d2i": convert(OperandType.Double, OperandType.Integer),
    "d2l": convert(OperandType.Double, OperandType.Long),
    "dadd": binary_operation(OperandType.Double),
    "daload": array_load(OperandType.Double),
    "dastore": array_store(OperandType.Double),
    "dcmpg": separate_comparison(OperandType.Double),
    "dcmpl": separate_comparison(OperandType.Double),
    "dconst_0": push_double,
    "dconst_1": push_double,
    "ddiv": binary_operation(OperandType.Double),
    "dload": push_double,
    "dload_0": push_double,
    "dload_1": push_double,
    "dload_2": push_double,
    "dload_3": push_double,
    "dmul": binary_operation(OperandType.Double),
    "dneg": unary_operation(OperandType.Double),
    "drem": binary_operation(OperandType.Double),
    "dreturn": pop_double,
    "dstore": pop_double,
    "dstore_0": pop_double,
    "dstore_1": pop_double,
    "dstore_2": pop_double,
    "dstore_3": pop_double,
    "dsub": binary_operation(OperandType.Double),
    "dup": duplicate_short,
    "dup_x1": duplicate_short_behind,
    "dup_x2": duplicate_x2,
    "dup2": duplicate_two,
    "dup2_x1": duplicate_two_behind,
    "dup2_x2": duplicate_two_x2,
    "f2d": convert(OperandType.Float, OperandType.Double),
    "f2i": convert(OperandType.Float, OperandType.Integer),
    "f2l": convert(OperandType.Float, OperandType.Long),
    "fadd": binary_operation(OperandType.Float),
    "faload": array_load(OperandType.Float),
    "fastore": array_store(OperandType.Float),
    "fcmpg": separate_comparison(OperandType.Float),
    "fcmpl": separate_comparison(OperandType.Float),
    "fconst_0": push_float,
    "fconst_1": push_float,
    "fconst_2": push_float,
    "fdiv": binary_operation(OperandType.Float),
    "fload": push_float,
    "fload_0": push_float,
    "fload_1": push_float,
    "fload_2": push_float,
    "fload_3": push_float,
    "fmul": binary_operation(OperandType.Float),
    "fneg": unary_operation(OperandType.Float),
    "frem": binary_operation(OperandType.Float),
    "freturn": pop_float,
    "fstore": pop_float,
    "fstore_0": pop_float,
    "fstore_1": pop_float,
    "fstore_2": pop_float,
    "fstore_3": pop_float,
    "fsub": binary_operation(OperandType.Float),
    "getfield": get_field,
    "getstatic": get_static,
    "goto": no_stack_modification,
    "goto_w": no_stack_modification,
    "i2b": convert(OperandType.Integer, OperandType.Byte),
    "i2c": convert(OperandType.Integer, OperandType.Char),
    "i2d": convert(OperandType.Integer, OperandType.Double),
    "i2f": convert(OperandType.Integer, OperandType.Float),
    "i2l": convert(OperandType.Integer, OperandType.Long),
    "i2s": convert(OperandType.Integer, OperandType.Short),
    "iadd": binary_operation(OperandType.Integer),
    "iaload": array_load(OperandType.Integer),
    "iand": binary_operation(OperandType.Integer),
    "iastore": array_store(OperandType.Integer),
    "iconst_m1": push_integer,
    "iconst_0": push_integer,
    "iconst_1": push_integer,
    "iconst_2": push_integer,
    "iconst_3": push_integer,
    "iconst_4": push_integer,
    "iconst_5": push_integer,
    "idiv": binary_operation(OperandType.Integer),
    "if_acmpeq": branch_compare_references,
    "if_acmpne": branch_compare_references,
    "if_icmpeq": branch_compare_integers,
    "if_icmpne": branch_compare_integers,
    "if_icmplt": branch_compare_integers,
    "if_icmpge": branch_compare_integers,
    "if_icmpgt": branch_compare_integers,
    "if_icmple": branch_compare_integers,
    "ifeq": pop_integer,
    "ifne": pop_integer,
    "iflt": pop_integer,
    "ifge": pop_integer,
    "ifgt": pop_integer,
    "ifle": pop_integer,
    "ifnonnull": pop_reference,
    "ifnull": pop_reference,
    "iinc": no_stack_modification,
    "iload": push_integer,
    "iload_0": push_integer,
    "iload_1": push_integer,
    "iload_2": push_integer,
    "iload_3": push_integer,
    "imul": binary_operation(OperandType.Integer),
    "ineg": unary_operation(OperandType.Integer),
    "instanceof": instance_of,
    "invokedynamic": invoke_static,
    "invokeinterface": invoke_instance,
    "invokespecial": invoke_instance,
    "invokestatic": invoke_static,
    "invokevirtual": invoke_instance,
    "ior": binary_operation(OperandType.Integer),
    "irem": binary_operation(OperandType.Integer),
    "ireturn": pop_integer,
    "ishl": binary_operation(OperandType.Integer),
    "ishr": binary_operation(OperandType.Integer),
    "istore": pop_integer,
    "istore_0": pop_integer,
    "istore_1": pop_integer,
    "istore_2": pop_integer,
    "istore_3": pop_integer,
    "isub": binary_operation(OperandType.Integer),
    "iushr": binary_operation(OperandType.Integer),
    "ixor": binary_operation(OperandType.Integer),
    "jsr": push_reference,
    "jsr_w": push_reference,
    "l2d": convert(OperandType.Long, OperandType.Double),
    "l2f": convert(OperandType.Long, OperandType.Float),
    "l2i": convert(OperandType.Long, OperandType.Integer),
    "ladd": binary_operation(OperandType.Long),
    "laload": array_load(OperandType.Long),
    "land": binary_operation(OperandType.Long),
    "lastore": array_store(OperandType.Long),
    "lcmp": separate_comparison(OperandType.Long),
    "lconst_0": push_long,
    "lconst_1": push_long,
    "ldc": push_constant,
    "ldc_w": push_constant,
    "ldc2_w": push_constant_long,
    "ldiv": binary_operation(OperandType.Long),
    "lload": push_long,
    "lload_0": push_long,
    "lload_1": push_long,
    "lload_2": push_long,
    "lload_3": push_long,
    "lmul": binary_operation(OperandType.Long),
    "lneg": unary_operation(OperandType.Long),
    "lookupswitch": pop_integer,
    "lor": binary_operation(OperandType.Long),
    "lrem": binary_operation(OperandType.Long),
    "lreturn": pop_long,
    "lshl": long_shift,
    "lshr": long_shift,
    "lstore": pop_long,
    "lstore_0": pop_long,
    "lstore_1": pop_long,
    "lstore_2": pop_long,
    "lstore_3": pop_long,
    "lsub": binary_operation(OperandType.Long),
    "lushr": long_shift,
    "lxor": binary_operation(OperandType.Long),
    "monitorenter": pop_reference,
    "monitorexit": pop_reference,
    "multianewarray": new_multidimensional_array,
    "new": push_reference,
    "newarray": new_array,
    "nop": no_stack_modification,
    "pop": pop_one,
    "pop2": pop_two,
    "putfield": put_field,
    "putstatic": put_static,
    "ret": no_stack_modification,
    "return": no_stack_modification,
    "saload": array_load(OperandType.Short),
    "sastore": array_store(OperandType.Short),
    "sipush": push_integer,
    "swap": swap,
    "tableswitch": pop_integer,
    "wide": no_stack_modification,
}

INSTRUCTION_TO_LOCAL_COUNT: Dict[str, Optional[int]] = {
    "aload": None,
    "astore": None,
    "dload": None,
    "dstore": None,
    "fload": None,
    "fstore": None,
    "iload": None,
    "istore": None,
    "lload": None,
    "lstore": None,
    "ret": None,
    "aload_0": 1,
    "aload_1": 2,
    "aload_2": 3,
    "aload_3": 4,
    "astore_0": 1,
    "astore_1": 2,
    "astore_2": 3,
    "astore_3": 4,
    "dload_0": 2,
    "dload_1": 3,
    "dload_2": 4,
    "dload_3": 5,
    "dstore_0": 2,
    "dstore_1": 3,
    "dstore_2": 4,
    "dstore_3": 5,
    "fload_0": 1,
    "fload_1": 2,
    "fload_2": 3,
    "fload_3": 4,
    "fstore_0": 1,
    "fstore_1": 2,
    "fstore_2": 3,
    "fstore_3": 4,
    "iload_0": 1,
    "iload_1": 2,
    "iload_2": 3,
    "iload_3": 4,
    "istore_0": 1,
    "istore_1": 2,
    "istore_2": 3,
    "istore_3": 4,
    "lload_0": 2,
    "lload_1": 3,
    "lload_2": 4,
    "lload_3": 5,
    "lstore_0": 2,
    "lstore_1": 3,
    "lstore_2": 4,
    "lstore_3": 5,
}

BRANCHES: Set[str] = {
    "goto",
    "goto_w",
    "if_acmpeq",
    "if_acmpne",
    "if_icmpeq",
    "if_icmpge",
    "if_icmpgt",
    "if_icmple",
    "if_icmplt",
    "if_icmpne",
    "ifeq",
    "ifge",
    "ifgt",
    "ifle",
    "iflt",
    "ifne",
    "lookupswitch",
    "tableswitch",
}


class Stack(object):
    _stack: OperandStack
    _saved_stacks: Deque[OperandStack]
    _max_stack_size: int
    _local_count: int
    _branch_depth: int

    def __init__(self):
        self._stack = deque()
        self._saved_stacks = deque()
        self._max_stack_size = 0
        self._local_count = 0
        self._branch_depth = 0

    @property
    def max_stack_size(self) -> int:
        return self._max_stack_size

    @property
    def local_count(self) -> int:
        return self._local_count

    def update_stack(self, instruction: Instruction, *operands: Operand):
        if instruction in INSTRUCTION_TO_STACK_MODIFICATION:
            stack_modification = INSTRUCTION_TO_STACK_MODIFICATION[instruction]
            arg_spec = inspect.getfullargspec(stack_modification)

            if len(arg_spec.args) == 1:
                stack_modification(self._stack)
            elif len(arg_spec.args) == 2:
                stack_modification(self._stack, operands)
            else:
                raise Exception("Unsupported stack modification")

            # Update max stack size
            self._max_stack_size = max(self._max_stack_size,
                                       sum(map(lambda op: op.size, self._stack)))
        else:
            raise NotImplementedError(f"No stack modification for instruction {instruction}!")

        # print(f"Stack: {len(self._stack)}", f"Instruction: {instruction}", "Operands:", *operands)

        if instruction in INSTRUCTION_TO_LOCAL_COUNT:
            local_count = INSTRUCTION_TO_LOCAL_COUNT[instruction]
            if local_count is not None:
                self._local_count = max(self._local_count, local_count)
            elif len(operands) == 1 and isinstance(operands[0], int):
                if instruction[0] in ("l", "d"):
                    self._local_count = max(self._local_count, operands[0] + 2)
                else:
                    self._local_count = max(self._local_count, operands[0] + 1)

        if instruction in BRANCHES:
            if instruction in ("lookupswitch", "tablewitch"):
                for _ in range(len(operands[0])):
                    self._saved_stacks.append(self._stack.copy())
            self._saved_stacks.append(self._stack.copy())

    def restore_stack(self):
        self._stack = self._saved_stacks.pop()
