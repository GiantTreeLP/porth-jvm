from jvm.context import GenerateContext
from jvm.instructions import Instructions
from jvm.intrinsics import OperandType


def clinit_method_instructions(context: GenerateContext) -> Instructions:
    instructions = (Instructions(context)
                    .push_integer(context.program.memory_capacity + context.get_strings_size())
                    .new_array(OperandType.Byte.array_type)
                    .put_static_field(context.memory_ref)
                    .push_integer(3)
                    .new_reference_array(context.cf.constants.create_class("java/io/FileDescriptor"))
                    .duplicate_top_of_stack()
                    .push_integer(0)
                    .get_static_field(
        context.cf.constants.create_field_ref("java/io/FileDescriptor", "in",
                                              "Ljava/io/FileDescriptor;"))
                    .store_array_reference()
                    .duplicate_top_of_stack()
                    .push_integer(1)
                    .get_static_field(
        context.cf.constants.create_field_ref("java/io/FileDescriptor", "out",
                                              "Ljava/io/FileDescriptor;"))
                    .store_array_reference()
                    .duplicate_top_of_stack()
                    .push_integer(2)
                    .get_static_field(
        context.cf.constants.create_field_ref("java/io/FileDescriptor", "err",
                                              "Ljava/io/FileDescriptor;"))
                    .store_array_reference()
                    .put_static_field(context.fd_ref))

    large_string = context.cf.constants.create_string("".join(context.strings.keys()))

    instructions.push_constant(large_string)
    instructions.string_get_bytes()
    # Stack: string (as byte array)
    instructions.duplicate_top_of_stack()
    # Stack: string (as byte array), string (as byte array)
    instructions.push_integer(0)
    # Stack: string (as byte array), string (as byte array), 0
    instructions.swap()
    # Stack: string (as byte array), 0, string (as byte array)
    instructions.array_length()
    # Stack: string (as byte array), 0, length

    instructions.get_static_field(context.memory_ref)
    # Stack: string (as byte array), 0, length, memory
    instructions.swap()
    # Stack: string (as byte array), 0, memory, length
    instructions.push_integer(context.program.memory_capacity)
    # Stack: string (as byte array), 0, memory, length, capacity
    instructions.swap()
    # Stack: string (as byte array), 0, memory, capacity, length
    instructions.array_copy()
    # Stack: (empty)

    instructions.return_void()

    return instructions
