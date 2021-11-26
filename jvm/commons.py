from collections import deque
from typing import Iterable, MutableSequence

from jawa.cf import ClassFile
from jawa.constants import Constant

from jvm.context import GenerateContext


def _print_boilerplate(cf: ClassFile, signature: str, fd: str):
    return (("getstatic", (cf.constants.create_field_ref("java/lang/System", fd, "Ljava/io/PrintStream;"))),
            ("swap",),
            ("invokevirtual", cf.constants.create_method_ref(
                "java/io/PrintStream",
                "println",
                signature
            )),)


def _write_boilerplate(cf: ClassFile, signature: str, fd: str):
    return (("getstatic", (cf.constants.create_field_ref("java/lang/System", fd, "Ljava/io/PrintStream;"))),
            ("swap",),
            ("invokevirtual", cf.constants.create_method_ref(
                "java/io/PrintStream",
                "write",
                signature
            )),)


def write_bytes_out(cf: ClassFile):
    return _write_boilerplate(cf, "([BII)V", "out")


def write_bytes_err(cf: ClassFile):
    return _write_boilerplate(cf, "([BII)V", "err")


def print_string(cf: ClassFile):
    return _print_boilerplate(cf, "(Ljava/lang/String;)V", "out")


def print_string_err(cf: ClassFile):
    return _print_boilerplate(cf, "(Ljava/lang/String;)V", "err")


def print_int(cf: ClassFile):
    return _print_boilerplate(cf, "(I)V", "out")


def _print_boilerplate_wide(cf: ClassFile, signature: str):
    return (("getstatic", (cf.constants.create_field_ref("java/lang/System", "out", "Ljava/io/PrintStream;"))),
            ("dup_x2",),
            ("pop",),
            ("invokevirtual", cf.constants.create_method_ref(
                "java/io/PrintStream",
                "println",
                signature
            )),)


def print_long(cf: ClassFile):
    return _print_boilerplate_wide(cf, "(J)V")


def print_long_method_instructions(cf: ClassFile):
    instructions = deque()

    instructions.append(("lload_0",))
    instructions.extend(_print_boilerplate_wide(cf, "(J)V"))
    instructions.append(("return",))
    return instructions


def print_double(cf: ClassFile):
    return _print_boilerplate_wide(cf, "(D)V")


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


def system_arraycopy(cf: ClassFile, instructions: MutableSequence):
    # Stack: src, src_pos, dst, dst_pos, length
    instructions.append(("invokestatic", cf.constants.create_method_ref(
        "java/lang/System",
        "arraycopy",
        "(Ljava/lang/Object;ILjava/lang/Object;II)V"
    )))


def print_memory(context: GenerateContext, instructions: MutableSequence):
    instructions.append(("getstatic", context.memory_ref))
    # Stack: memory
    instructions.append(("invokestatic", context.cf.constants.create_method_ref(
        "java/util/Arrays",
        "toString",
        "([B)Ljava/lang/String;"
    )))
    # Stack: string
    for ins in print_string(context.cf):
        instructions.append(ins)


def push_constant(instructions: MutableSequence, constant: Constant):
    if constant.index <= 255:
        instructions.append(("ldc", constant))
    else:
        instructions.append(("ldc_w", constant))


ARGC_OFFSET = 0
ARGV_OFFSET = 8
MAX_STACK = 0xe000  # Seems to be the highest it'll go without a stack overflow
LONG_SIZE = 8
