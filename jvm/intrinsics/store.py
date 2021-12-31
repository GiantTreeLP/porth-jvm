from typing import MutableSequence

from jvm.commons import push_int
from jvm.context import GenerateContext
from jvm.instructions import Instructions


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

def store_64_method_instructions(context: GenerateContext) -> Instructions:
    return (
        Instructions(context)
        .load_long(0)
        .load_long(2)
        .convert_long_to_integer()
        .move_short_behind_long()
        .store_long(2)
        .duplicate_top_of_stack()
        .load_long(2)
        .push_long(0xffffffff)
        .and_long()
        .convert_long_to_integer()
        .duplicate_top_2_of_stack()
        .duplicate_top_2_of_stack()
        .duplicate_top_2_of_stack()
        .store_byte(0)
        .store_byte(1)
        .store_byte(2)
        .store_byte(3)
        .load_long(2)
        .push_integer(32)
        .unsigned_shift_right_long()
        .convert_long_to_integer()
        .swap()
        .push_integer(4)
        .add_integer()
        .swap()
        .duplicate_top_2_of_stack()
        .duplicate_top_2_of_stack()
        .duplicate_top_2_of_stack()
        .store_byte(0)
        .store_byte(1)
        .store_byte(2)
        .store_byte(3)
        .return_void()
    )


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
