from jvm.context import GenerateContext
from jvm.instructions import Instructions
from jvm.syscalls import SysCalls


def syscall1_method_instructions(context: GenerateContext):
    return (
        Instructions(context)
        .load_long(2)
        .convert_long_to_integer()
        .lookup_switch("exit0", {
            SysCalls.CLOSE: "close",
            SysCalls.EXIT: "exit"
        })

        .label("close")
        .new(context.cf.constants.create_class("java/io/FileInputStream"))
        .duplicate_top_of_stack()
        .get_static_field(context.fd_ref)
        .load_long(0)  # file descriptor
        .convert_long_to_integer()
        .load_array_reference()
        .invoke_special(context.cf.constants.create_method_ref("java/io/FileInputStream", "<init>",
                                                               "(Ljava/io/FileDescriptor;)V"))
        .invoke_virtual(context.cf.constants.create_method_ref("java/io/FileInputStream", "close", "()V"))
        .get_static_field(context.fd_ref)
        .load_long(0)  # file descriptor
        .convert_long_to_integer()
        .push_null()
        .store_array_reference()

        .branch("exit0")
        .end_branch()

        .label("exit")
        .load_long(0)
        .convert_long_to_integer()
        .invoke_static(context.cf.constants.create_method_ref("java/lang/System", "exit", "(I)V"))
        .branch("exit0")
        .end_branch()

        .label("exit0")
        .end_branch()
        .push_long(0)
        .return_long()
    )