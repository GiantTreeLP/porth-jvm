from jawa.assemble import Label

from jvm.context import GenerateContext
from jvm.instructions import Instructions

SYSCALL_READ = 0x0
SYSCALL_WRITE = 0x1


def syscall3_method_instructions(context: GenerateContext):
    return (
        Instructions(context)
        .load_long(6)
        .convert_long_to_integer()
        .lookup_switch("exit0", {
            SYSCALL_READ: Label("read"),
            SYSCALL_WRITE: Label("write"),
        })
        .label("read")
        .load_long(4)
        .convert_long_to_integer()
        .get_static_field(context.fd_ref)
        .swap()
        .load_array_reference()
        .new(context.cf.constants.create_class("java/io/FileInputStream"))
        .duplicate_behind_top_of_stack()
        .duplicate_behind_top_of_stack()
        .pop()
        .invoke_special(context.cf.constants.create_method_ref("java/io/FileInputStream",
                                                               "<init>",
                                                               "(Ljava/io/FileDescriptor;)V"))
        .get_static_field(context.memory_ref)
        .load_long(2)
        .convert_long_to_integer()
        .load_long(0)
        .convert_long_to_integer()
        .invoke_virtual(context.cf.constants.create_method_ref("java/io/FileInputStream",
                                                               "read",
                                                               "([BII)I"))
        .duplicate_top_of_stack()
        .push_integer(-1)
        .branch_if_integer_not_equal("read_return_value")  # if read() != -1, goto read_return_value
        .push_integer(0)
        .swap()
        .pop()
        .label("read_return_value")
        .convert_integer_to_long()
        .branch("exit")

        .label("write")
        .load_long(4)
        .convert_long_to_integer()
        .get_static_field(context.fd_ref)
        .swap()
        .load_array_reference()
        .new(context.cf.constants.create_class("java/io/FileOutputStream"))
        .duplicate_behind_top_of_stack()
        .duplicate_behind_top_of_stack()
        .pop()
        .invoke_special(context.cf.constants.create_method_ref("java/io/FileOutputStream",
                                                               "<init>",
                                                               "(Ljava/io/FileDescriptor;)V"))
        .duplicate_top_of_stack()
        .get_static_field(context.memory_ref)
        .load_long(2)
        .convert_long_to_integer()
        .load_long(0)
        .convert_long_to_integer()
        .invoke_virtual(context.cf.constants.create_method_ref("java/io/OutputStream",
                                                               "write",
                                                               "([BII)V"))
        .invoke_virtual(context.cf.constants.create_method_ref("java/io/OutputStream",
                                                               "flush",
                                                               "()V"))
        .load_long(0)
        .branch("exit")

        .label("exit0")
        .push_long(0)

        .label("exit")
        .return_long()
    )
