from collections import deque
from typing import MutableSequence

from jawa.assemble import assemble
from jawa.constants import MethodReference

from jvm.commons import push_long, push_int, count_locals, calculate_max_stack
from jvm.context import GenerateContext


def store_byte(context: GenerateContext, instructions: MutableSequence, index: int):
    shift = index * 8
    if index != 0:
        # Stack: index, int
        instructions.append(("swap",))
        # Stack: int, index
        push_int(context.cf, instructions, index)
        # Stack: int, index, 1
        instructions.append(("iadd",))
        # Stack: int, index + 1
        instructions.append(("swap",))
    # Stack: index + 1, int
    if shift != 0:
        push_int(context.cf, instructions, shift)
        # Stack: index, int, shift
        instructions.append(("iushr",))
        # Stack: index, int >>> shift
    # instructions.append(("i2b",))
    # Stack: index, byte
    instructions.append(("getstatic", context.memory_ref))
    # Stack: index, byte, ref
    instructions.append(("dup_x2",))
    # Stack: ref, index, byte, ref
    instructions.append(("pop",))
    # Stack: ref, index, byte
    instructions.append(("bastore",))  # Requires ref, index, byte
    # Stack: (empty)


def store_64(context: GenerateContext, instructions: MutableSequence, local_variable_index: int):
    # Stack: long, index (as long)
    instructions.append(("l2i",))
    # Stack: long, index (as int)
    instructions.append(("dup_x2",))
    # Stack: index (as int), long, index (as int)
    instructions.append(("pop",))
    # Stack: index, long
    instructions.append(("lstore", local_variable_index + 2))
    # Stack: index
    instructions.append(("dup",))
    # Stack: index, index
    instructions.append(("lload", local_variable_index + 2))
    # Stack: index, index, long
    push_long(context.cf, instructions, 0xffffffff)  # Lower 32 bits
    # Stack: index, index, long, 0xffffffff
    instructions.append(("land",))
    # Stack:index, index, long (lower 32 bits)
    instructions.append(("l2i",))
    # Stack: index, index, int (lower 32 bits)
    instructions.append(("dup2",))
    # Stack: index, index, int, index, int
    instructions.append(("dup2",))
    # Stack: index, index, int, index, int, index, int
    instructions.append(("dup2",))
    # Stack: index, index, int, index, int, index, int, index, int
    store_byte(context, instructions, 0)
    # Stack: index, index, int, index, int, index, int
    store_byte(context, instructions, 1)
    # Stack: index, index, int, index, int
    store_byte(context, instructions, 2)
    # Stack: index, index, int
    store_byte(context, instructions, 3)
    # Stack: index
    instructions.append(("lload", local_variable_index + 2))
    # Stack: index, long
    push_int(context.cf, instructions, 32)  # Upper 32 bits
    # Stack: index, long, 32
    instructions.append(("lushr",))
    # Stack: index, long (upper 32 bits)
    instructions.append(("l2i",))
    # Stack: index, int (upper 32 bits)
    instructions.append(("swap",))
    # Stack: int (upper 32 bits), index
    push_int(context.cf, instructions, 4)
    # Stack: int (upper 32 bits), index, 4
    instructions.append(("iadd",))
    # Stack: int (upper 32 bits), index
    instructions.append(("swap",))
    # Stack: index, int (upper 32 bits)
    instructions.append(("dup2",))
    # Stack: index, int, index, int
    instructions.append(("dup2",))
    # Stack: index, int, index, int, index, int
    instructions.append(("dup2",))
    # Stack: index, int, index, int, index, int, index, int
    store_byte(context, instructions, 0)
    # Stack: index, int, index, int, index, int
    store_byte(context, instructions, 1)
    # Stack: index, int, index, int
    store_byte(context, instructions, 2)
    # Stack: index, int
    store_byte(context, instructions, 3)
    # Stack: (empty)


def add_store_64_method(context: GenerateContext) -> MethodReference:
    method = context.cf.methods.create("store_64", "(JJ)V", code=True)
    method.access_flags.acc_public = False
    method.access_flags.acc_private = True
    method.access_flags.acc_static = True
    method.access_flags.acc_synthetic = True

    instructions = deque()

    instructions.append(("lload_0",))
    instructions.append(("lload_2",))

    store_64(context, instructions, 0)

    instructions.append(("return",))

    method.code.assemble(assemble(instructions))
    method.code.max_locals = count_locals(method.descriptor.value, instructions)
    method.code.max_stack = calculate_max_stack(context, assemble(instructions))

    return context.cf.constants.create_method_ref(context.cf.this.name.value, method.name.value,
                                                  method.descriptor.value)


def store_32(context: GenerateContext, instructions: MutableSequence):
    # Stack: int (as long), index (as long)
    instructions.append(("l2i",))
    # Stack: int (as long), index (as int)
    instructions.append(("dup_x2",))
    # Stack: index (as int), int (as long), index (as int)
    instructions.append(("pop",))
    # Stack: index, int (as long)
    instructions.append(("l2i",))
    # Stack: index, int (as int)
    instructions.append(("dup2",))
    # Stack: index, int, index, int
    instructions.append(("dup2",))
    # Stack: index, int, index, int, index, int
    instructions.append(("dup2",))
    # Stack: index, int, index, int, index, int, index, int
    store_byte(context, instructions, 0)
    # Stack: index, int, index, int, index, int
    store_byte(context, instructions, 1)
    # Stack: index, int, index, int
    store_byte(context, instructions, 2)
    # Stack: index, int
    store_byte(context, instructions, 3)
    # Stack: (empty)


def store_16(context: GenerateContext, instructions: MutableSequence):
    # Stack: short (as long), index (as long)
    instructions.append(("l2i",))
    # Stack: short (as long), index (as int)
    instructions.append(("dup_x2",))
    # Stack: index (as int), short (as long), index (as int)
    instructions.append(("pop",))
    # Stack: index, short (as long)
    instructions.append(("l2i",))
    # Stack: index, short (as int)
    instructions.append(("dup2",))
    # Stack: index, short, index, short
    store_byte(context, instructions, 0)
    # Stack: index, short
    store_byte(context, instructions, 1)
    # Stack: (empty)


def store_8(context: GenerateContext, instructions: MutableSequence):
    # Stack: byte, index
    instructions.append(("l2i",))
    instructions.append(("dup_x2",))
    instructions.append(("pop",))
    # Stack: index, byte
    instructions.append(("l2i",))
    instructions.append(("i2b",))
    instructions.append(("getstatic", context.memory_ref))
    instructions.append(("dup_x2",))
    instructions.append(("pop",))
    instructions.append(("bastore",))
    # Stack: (empty)
