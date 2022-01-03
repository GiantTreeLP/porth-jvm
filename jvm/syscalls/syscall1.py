from jvm.context import GenerateContext
from jvm.instructions import Instructions
from jvm.syscalls import SysCalls


def syscall1_method_instructions(context: GenerateContext):
    return (
        Instructions(context)
        .load_long(2)
        .convert_long_to_integer()
        .lookup_switch("exit0", {
            SysCalls.EXIT: "exit"
        })
        .label("exit")
        .load_long(0)
        .convert_long_to_integer()
        .invoke_static(context.cf.constants.create_method_ref("java/lang/System", "exit", "(I)V"))
        .push_long(0)
        .return_long()
        .label("exit0")
        .push_long(0)
        .return_long()
    )