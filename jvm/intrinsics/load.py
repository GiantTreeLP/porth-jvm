from jvm.context import GenerateContext
from jvm.instructions import Instructions


def load_64_method_instructions(context: GenerateContext) -> Instructions:
    return (
        Instructions(context)
        .load_long(0)
        # Stack: index (as long)
        .convert_long_to_integer()
        # Stack: index (as int)
        .duplicate_top_of_stack()
        # Stack: index, index
        .duplicate_top_of_stack()
        # Stack: index, index, index
        .duplicate_top_of_stack()
        # Stack: index, index, index, index
        .duplicate_top_of_stack()
        # Stack: index, index, index, index, index
        .duplicate_top_of_stack()
        # Stack: index, index, index, index, index, index
        .duplicate_top_of_stack()
        # Stack: index, index, index, index, index, index, index
        .duplicate_top_of_stack()
        .load_byte_wide(0)
        .move_long_behind_short()
        .load_byte_wide(1)
        .or_long()
        .move_long_behind_short()
        .load_byte_wide(2)
        .or_long()
        .move_long_behind_short()
        .load_byte_wide(3)
        .or_long()
        .move_long_behind_short()
        .load_byte_wide(4)
        .or_long()
        .move_long_behind_short()
        .load_byte_wide(5)
        .or_long()
        .move_long_behind_short()
        .load_byte_wide(6)
        .or_long()
        .move_long_behind_short()
        .load_byte_wide(7)
        .or_long()
        .return_long()
    )


def load_32_method_instructions(context: GenerateContext) -> Instructions:
    return (
        Instructions(context)
        .load_long(0)
        .convert_long_to_integer()
        .duplicate_top_of_stack()
        .duplicate_top_of_stack()
        .duplicate_top_of_stack()
        .load_byte(0)
        .swap()
        .load_byte(1)
        .or_integer()
        .swap()
        .load_byte(2)
        .or_integer()
        .swap()
        .load_byte(3)
        .or_integer()
        .convert_integer_to_long()
        .return_long()
    )


def load_16_method_instructions(context: GenerateContext) -> Instructions:
    return (
        Instructions(context)
        .load_long(0)
        .convert_long_to_integer()
        .duplicate_top_of_stack()
        .load_byte(0)
        .swap()
        .load_byte(1)
        .or_integer()
        .convert_integer_to_short()
        .convert_integer_to_long()
        .return_long()
    )


def load_8_method_instructions(context: GenerateContext) -> Instructions:
    return (
        Instructions(context)
        .load_long(0)
        .convert_long_to_integer()
        .get_static_field(context.memory_ref)
        .swap()
        .load_array_byte()
        .convert_integer_to_long()
        .return_long()
    )
