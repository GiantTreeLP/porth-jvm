from jvm.context import GenerateContext
from jvm.instructions import Instructions
from jvm.intrinsics import OperandType


def clinit_method_instructions(context: GenerateContext) -> Instructions:
    return (
        Instructions(context)
        .push_integer(context.program.memory_capacity)
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
        .put_static_field(context.fd_ref)
        .return_void()
    )
