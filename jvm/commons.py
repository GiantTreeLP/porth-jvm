import inspect
from typing import Iterable, MutableSequence

from jawa.cf import ClassFile
from jawa.constants import Constant, MethodReference, FieldReference, InterfaceMethodRef
from jawa.util.bytecode import Instruction

from jvm.context import GenerateContext
from jvm.instructions import INSTRUCTIONS, OperandType, Instructions

LONG_SIZE = 8


def _print_boilerplate(cf: ClassFile, signature: str, fd: str):
    return (("getstatic", (cf.constants.create_field_ref("java/lang/System", fd, "Ljava/io/PrintStream;"))),
            ("swap",),
            ("invokevirtual", cf.constants.create_method_ref(
                "java/io/PrintStream",
                "println",
                signature
            )),)


def print_string(cf: ClassFile, instructions: MutableSequence):
    for ins in _print_boilerplate(cf, "(Ljava/lang/String;)V", "out"):
        instructions.append(ins)


def _print_boilerplate_wide(cf: ClassFile, signature: str):
    return (("getstatic", (cf.constants.create_field_ref("java/lang/System", "out", "Ljava/io/PrintStream;"))),
            ("dup_x2",),
            ("pop",),
            ("invokevirtual", cf.constants.create_method_ref(
                "java/io/PrintStream",
                "println",
                signature
            )),)


def print_long(cf: ClassFile, instructions: MutableSequence):
    for ins in _print_boilerplate_wide(cf, "(J)V"):
        instructions.append(ins)


def print_long_method_instructions(context: GenerateContext) -> Instructions:
    return (
        Instructions(context)
            .load_long(0)
            .get_static_field(context.cf.constants.create_field_ref("java/lang/System", "out", "Ljava/io/PrintStream;"))
            .move_short_behind_long()
            .invoke_virtual(context.cf.constants.create_method_ref(
            "java/io/PrintStream",
            "println",
            "(J)V"
        ))
            .return_void()
    )


def count_locals(descriptor: str, instructions: Iterable):
    locals_count_table = {
        "dload": -1,
        "dload_0": 2,
        "dload_1": 3,
        "dload_2": 4,
        "dload_3": 5,
        "lload": -1,
        "lload_0": 2,
        "lload_1": 3,
        "lload_2": 4,
        "lload_3": 5,
        "iload": -1,
        "iload_0": 1,
        "iload_1": 2,
        "iload_2": 3,
        "iload_3": 4,
        "fload": -1,
        "fload_0": 1,
        "fload_1": 2,
        "fload_2": 3,
        "fload_3": 4,
        "aload": -1,
        "aload_0": 1,
        "aload_1": 2,
        "aload_2": 3,
        "aload_3": 4,
        "dstore": -1,
        "dstore_0": 2,
        "dstore_1": 3,
        "dstore_2": 4,
        "dstore_3": 5,
        "lstore": -1,
        "lstore_0": 2,
        "lstore_1": 3,
        "lstore_2": 4,
        "lstore_3": 5,
        "istore": -1,
        "istore_0": 1,
        "istore_1": 2,
        "istore_2": 3,
        "istore_3": 4,
        "fstore": -1,
        "fstore_0": 1,
        "fstore_1": 2,
        "fstore_2": 3,
        "fstore_3": 4,
        "astore": -1,
        "astore_0": 1,
        "astore_1": 2,
        "astore_2": 3,
        "astore_3": 4,
    }

    max_count = 0

    params = {
        "B": 1,
        "C": 1,
        "D": 2,
        "F": 1,
        "I": 1,
        "J": 2,
        "L": 1,
        "S": 1,
        "Z": 1,
        "[": 1,
    }

    i = 0
    while i < len(descriptor):
        if descriptor[i] in params:
            max_count += params[descriptor[i]]
        if descriptor[i] == "[":
            i += 1
            continue
        elif descriptor[i] == "L":
            i += 1
            while descriptor[i] != ";":
                i += 1
        elif descriptor[i] == ")":
            break
        i += 1

    for instruction in instructions:
        if instruction[0] in locals_count_table:
            count = locals_count_table[instruction[0]]
            if count == -1:
                if instruction[0][0] in ["d", "l"]:
                    count = instruction[1] + 1
                else:
                    count = instruction[1]
            max_count = max(max_count, count)

    return max_count + 1


def push_long(cf: ClassFile, instructions: MutableSequence, long: int):
    if long == 0:
        instructions.append(("lconst_0",))
    elif long == 1:
        instructions.append(("lconst_1",))
    elif long in range(-128, 128):
        instructions.append(("bipush", long), )
        instructions.append(("i2l",))
    elif long in range(-32768, 32768):
        instructions.append(("sipush", long), )
        instructions.append(("i2l",))
    elif long in range(-2147483648, 2147483648):
        push_constant(instructions, cf.constants.create_integer(long))
        instructions.append(("i2l",))
    else:
        instructions.append(("ldc2_w", cf.constants.create_long(long)))


def push_int(cf: ClassFile, instructions: MutableSequence, integer: int):
    if integer < -32768:
        push_constant(instructions, cf.constants.create_integer(integer))
    elif integer < -128:
        instructions.append(("sipush", integer), )
    elif integer < -1:
        instructions.append(("bipush", integer), )
    elif integer == -1:
        instructions.append(("iconst_m1",))
    elif integer <= 5:
        instructions.append((f"iconst_{integer}",))
    elif integer in range(-128, 128):
        instructions.append(("bipush", integer), )
    elif integer in range(-32768, 32768):
        instructions.append(("sipush", integer), )
    elif integer in range(-2147483648, 2147483648):
        push_constant(instructions, cf.constants.create_integer(integer))
    else:
        raise ValueError(f"{integer} greater than MAX_INT")


def string_get_bytes(cf: ClassFile, instructions: MutableSequence):
    # Stack: string ref
    instructions.append(("invokevirtual", cf.constants.create_method_ref(
        "java/lang/String",
        "getBytes",
        "()[B"
    )))


def push_constant(instructions: MutableSequence, constant: Constant):
    if constant.index <= 255:
        instructions.append(("ldc", constant))
    else:
        instructions.append(("ldc_w", constant))


def calculate_max_stack(context: GenerateContext, instructions: Iterable[Instruction]) -> int:
    def sum_list_of_types(types: Iterable[OperandType]) -> int:
        return sum(map(lambda t: t.size if t is not None else 0, types))

    running_maximum = 0
    current_size = 0

    for instruction in instructions:
        mapping = INSTRUCTIONS[instruction[1]]
        outputs = mapping.outputs

        if callable(outputs):
            constant = context.cf.constants.get(instruction.operands[0].value)
            signature = inspect.signature(outputs)
            if len(signature.parameters) == 1:
                first = next(iter(signature.parameters.values()))
                if first.annotation in (MethodReference, FieldReference, InterfaceMethodRef):
                    current_size += sum_list_of_types(outputs(constant))
                elif first.annotation == FieldReference:
                    current_size += sum_list_of_types(outputs(constant))
                elif isinstance(constant, first.annotation.__args__):
                    current_size += sum_list_of_types(outputs(constant))
                else:
                    raise ValueError(f"Unknown annotation {first.annotation}")
            else:
                raise ValueError(f"Cannot handle {signature}")
        else:
            current_size += sum_list_of_types(outputs)

        inputs = mapping.inputs

        if callable(inputs):
            constant = context.cf.constants.get(instruction.operands[0].value)
            signature = inspect.signature(inputs)
            if len(signature.parameters) == 1:
                first = next(iter(signature.parameters.values()))
                if first.annotation == MethodReference:
                    current_size -= sum_list_of_types(inputs(constant))
                elif first.annotation == FieldReference:
                    current_size -= sum_list_of_types(inputs(constant))
                elif isinstance(constant, first.annotation.__args__):
                    current_size += sum_list_of_types(outputs(constant))
                else:
                    raise ValueError(f"Unknown annotation {first.annotation}")
            else:
                raise ValueError(f"Cannot handle {signature}")
        else:
            current_size -= sum_list_of_types(inputs)

        running_maximum = max(running_maximum, current_size)

    return running_maximum
