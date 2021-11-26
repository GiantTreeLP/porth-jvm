from collections import deque
from typing import MutableSequence

from jawa.cf import ClassFile
from jawa.constants import FieldReference

from jvm.commons import push_long, push_int
from jvm.context import GenerateContext


def load_byte(cf: ClassFile, instructions: MutableSequence, index: int, memory_ref: FieldReference) -> None:
    """
    Loads a byte from the given index.
    Returns it as an int.
    :param cf: the class file
    :param instructions: the list of instructions to append to
    :param index: the index to load from
    :param memory_ref: the reference to the memory
    """
    shift = index * 8
    # Stack: index
    if index != 0:
        push_int(cf, instructions, index)
        # Stack: index, index_1
        instructions.append(("iadd",))
        # Stack: index
    instructions.append(("getstatic", memory_ref))
    # Stack: index, ref
    instructions.append(("swap",))
    # Stack: ref, index
    instructions.append(("baload",))
    # Stack: byte (as int, extended)
    push_int(cf, instructions, 0xff)
    # Stack: byte (as int, extended), 0xff
    instructions.append(("iand",))
    # Stack: byte (as int, lower 8 bits)
    if shift != 0:
        push_int(cf, instructions, shift)
        # Stack: byte (as int, lower 8 bits), shift
        instructions.append(("ishl",))
        # Stack: byte (as int, lower 8 bits) << shift


def load_byte_w(context: GenerateContext, instructions: MutableSequence, index: int) -> None:
    """
    Loads a wide byte from the given index.
    Returns it as a long.
    :param context: The context to use for generating the instructions
    :param instructions: the list of instructions to append to
    :param index: the index to load from
    """
    shift = index * 8
    # Stack: index
    if index != 0:
        push_int(context.cf, instructions, index)
        # Stack: index, index_1
        instructions.append(("iadd",))
        # Stack: index
    instructions.append(("getstatic", context.memory_ref))
    # Stack: index, ref
    instructions.append(("swap",))
    # Stack: ref, index
    instructions.append(("baload",))
    # Stack: byte (as int, extended)
    instructions.append(("i2l",))
    # Stack: byte (as long)
    push_long(context.cf, instructions, 0xff)
    # Stack: byte (as int, extended), 0xff
    instructions.append(("land",))
    # Stack: byte (as long, lower 8 bits)
    if shift != 0:
        push_int(context.cf, instructions, shift)
        # Stack: byte (as long, lower 8 bits), shift
        instructions.append(("lshl",))
        # Stack: byte (as long, lower 8 bits) << shift


def load_64(context: GenerateContext, instructions: MutableSequence):
    # Stack: index
    instructions.append(("l2i",))
    # Stack: index (as int)
    instructions.append(("dup",))
    # Stack: index, index
    instructions.append(("dup",))
    # Stack: index, index, index
    instructions.append(("dup",))
    # Stack: index, index, index, index
    instructions.append(("dup",))
    # Stack: index, index, index, index, index
    instructions.append(("dup",))
    # Stack: index, index, index, index, index, index
    instructions.append(("dup",))
    # Stack: index, index, index, index, index, index, index
    instructions.append(("dup",))
    # Stack: index, index, index, index, index, index, index, index
    load_byte_w(context, instructions, 0)
    # Stack: index, index, index, index, index, index, index, byte1
    instructions.append(("dup2_x1",))
    # Stack: index, index, index, index, index, index, byte1, index, byte1
    instructions.append(("pop2",))
    # Stack: index, index, index, index, index, index, byte1, index
    load_byte_w(context, instructions, 1)
    # Stack: index, index, index, index, index, index, byte1, byte2
    instructions.append(("lor",))
    # Stack: index, index, index, index, index, index, short
    instructions.append(("dup2_x1",))
    # Stack: index, index, index, index, index, short, index, short
    instructions.append(("pop2",))
    # Stack: index, index, index, index, index, short, index
    load_byte_w(context, instructions, 2)
    # Stack: index, index, index, index, index, short, byte3
    instructions.append(("lor",))
    # Stack: index, index, index, index, index, long
    instructions.append(("dup2_x1",))
    # Stack: index, index, index, index, long, index, long
    instructions.append(("pop2",))
    # Stack: index, index, index, index, long, index
    load_byte_w(context, instructions, 3)
    # Stack: index, index, index, index, long, byte4
    instructions.append(("lor",))
    # Stack: index, index, index, index, long
    instructions.append(("dup2_x1",))
    # Stack: index, index, index, long, index, long
    instructions.append(("pop2",))
    # Stack: index, index, index, long, index
    load_byte_w(context, instructions, 4)
    # Stack: index, index, index, long, byte4
    instructions.append(("lor",))
    # Stack: index, index, index, long
    instructions.append(("dup2_x1",))
    # Stack: index, index, long, index, long
    instructions.append(("pop2",))
    # Stack: index, index, long, index
    load_byte_w(context, instructions, 5)
    # Stack: index, index, long, byte5
    instructions.append(("lor",))
    # Stack: index, index, long
    instructions.append(("dup2_x1",))
    # Stack: index, long, index, long
    instructions.append(("pop2",))
    # Stack: index, long, index
    load_byte_w(context, instructions, 6)
    # Stack: index, long, byte6
    instructions.append(("lor",))
    # Stack: index, long
    instructions.append(("dup2_x1",))
    # Stack: long, index, long
    instructions.append(("pop2",))
    # Stack: long, index
    load_byte_w(context, instructions, 7)
    # Stack: long, byte7
    instructions.append(("lor",))
    # Stack: long


def load_64_method_instructions(context: GenerateContext):
    instructions = deque()
    instructions.append(("lload_0",))
    load_64(context, instructions)
    instructions.append(("lreturn",))
    return instructions


def load_32(context: GenerateContext, instructions: MutableSequence):
    # Stack: index
    instructions.append(("l2i",))
    # Stack: index (as int)
    instructions.append(("dup",))
    # Stack: index, index
    instructions.append(("dup",))
    # Stack: index, index, index
    instructions.append(("dup",))
    # Stack: index, index, index, index
    load_byte(context.cf, instructions, 0, context.memory_ref)
    # Stack: index, index, index, byte1
    instructions.append(("swap",))
    # Stack: index, index, byte1, index
    load_byte(context.cf, instructions, 1, context.memory_ref)
    # Stack : index, index, byte1, byte2
    instructions.append(("ior",))
    # Stack: index, index, short
    instructions.append(("swap",))
    # Stack: index, short, index
    load_byte(context.cf, instructions, 2, context.memory_ref)
    # Stack: index, short, byte3
    instructions.append(("ior",))
    # Stack: index, int
    instructions.append(("swap",))
    # Stack: int, index
    load_byte(context.cf, instructions, 3, context.memory_ref)
    # Stack: int, byte4
    instructions.append(("ior",))
    # Stack: int
    instructions.append(("i2l",))


def load_32_method_instructions(context: GenerateContext):
    instructions = deque()
    instructions.append(("lload_0",))
    load_32(context, instructions)
    instructions.append(("lreturn",))
    return instructions


def load_16(context: GenerateContext, instructions: MutableSequence):
    # Stack: index
    instructions.append(("l2i",))
    instructions.append(("dup",))
    # Stack: index, index
    load_byte(context.cf, instructions, 0, context.memory_ref)
    # Stack: index, byte1
    instructions.append(("swap",))
    # Stack: byte1, index
    load_byte(context.cf, instructions, 1, context.memory_ref)
    # Stack: byte1, byte2
    instructions.append(("ior",))
    # Stack: short
    instructions.append(("i2s",))
    # Stack: short
    instructions.append(("i2l",))
    # Stack: short (as long)


def load_16_method_instructions(context: GenerateContext):
    instructions = deque()
    instructions.append(("lload_0",))
    load_16(context, instructions)
    instructions.append(("lreturn",))
    return instructions


def load_8(context: GenerateContext, instructions: MutableSequence):
    # Stack: index
    instructions.append(("l2i",))
    # Stack: index (as int)
    instructions.append(("getstatic", context.memory_ref))
    # Stack: index (as int), array
    instructions.append(("swap",))
    # Stack: array, index (as int)
    instructions.append(("baload",))
    # Stack: value (as int)
    instructions.append(("i2l",))
    # Stack: byte (as long)


def load_8_method_instructions(context: GenerateContext):
    instructions = deque()
    instructions.append(("lload_0",))
    load_8(context, instructions)
    instructions.append(("lreturn",))
    return instructions
