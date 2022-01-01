from jvm.context import GenerateContext
from jvm.instructions import Instructions


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


def store_32(context: GenerateContext, instructions: Instructions):
    # Stack: int (as long), index (as long)
    instructions.convert_long_to_integer()
    # Stack: int (as long), index (as int)
    instructions.move_short_behind_long()
    # Stack: index, int (as long)
    instructions.convert_long_to_integer()
    # Stack: index, int (as int)
    instructions.duplicate_top_2_of_stack()
    # Stack: index, int, index, int
    instructions.duplicate_top_2_of_stack()
    # Stack: index, int, index, int, index, int
    instructions.duplicate_top_2_of_stack()
    # Stack: index, int, index, int, index, int, index, int
    instructions.store_byte(0)
    # Stack: index, int, index, int, index, int
    instructions.store_byte(1)
    # Stack: index, int, index, int
    instructions.store_byte(2)
    # Stack: index, int
    instructions.store_byte(3)
    # Stack: (empty)


def store_16(context: GenerateContext, instructions: Instructions):
    # Stack: short (as long), index (as long)
    instructions.convert_long_to_integer()
    # Stack: short (as long), index (as int)
    instructions.move_short_behind_long()
    # Stack: index, short (as long)
    instructions.convert_long_to_integer()
    # Stack: index, short (as int)
    instructions.duplicate_top_2_of_stack()
    # Stack: index, short, index, short
    instructions.store_byte(0)
    # Stack: index, short
    instructions.store_byte(1)
    # Stack: (empty)


def store_8(context: GenerateContext, instructions: Instructions):
    # Stack: byte (as long), index (as long)
    instructions.convert_long_to_integer()
    # Stack: byte (as int), index
    instructions.move_short_behind_long()
    # Stack: index, byte (as long)
    instructions.convert_long_to_integer()
    # Stack: index, byte (as int)
    instructions.convert_integer_to_byte()
    # Stack: index, byte
    instructions.get_static_field(context.memory_ref)
    # Stack: index, byte, memory
    instructions.move_short_behind_top_2_of_stack()
    # Stack: memory, index, byte
    instructions.store_array_byte()
    # Stack: (empty)
