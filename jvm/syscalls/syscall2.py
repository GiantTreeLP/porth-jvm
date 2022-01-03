from jvm.commons import LONG_SIZE
from jvm.context import GenerateContext
from jvm.instructions import Instructions
from jvm.syscalls import SysCalls


def syscall2_method_instructions(context: GenerateContext) -> Instructions:
    return (
        Instructions(context)
        .load_long(4)
        .convert_long_to_integer()
        .lookup_switch("exit0", {
            SysCalls.CLOCK_GETTIME: "clock_gettime"
        })
        .label("clock_gettime")
        .load_long(2)
        .convert_long_to_integer()
        .push_integer(1)  # CLOCK_MONOTONIC
        .branch_if_integer_not_equal("exit-1")
        .invoke_static(context.cf.constants.create_method_ref("java/lang/System", "nanoTime", "()J"))
        # Stack: time
        .duplicate_long()
        # Stack: time, time
        .push_long(1_000_000_000)
        # Stack: time, time, 1.000.000.000
        .divide_long()
        # Stack: time, time (seconds)
        .load_long(0)
        # Stack: time, time (seconds), timespec + 0 (*timespec.tv_sec)
        .invoke_static(context.store_64_method)
        # Stack: time
        .push_long(1_000_000_000)
        # Stack: time, 1.000.000.000
        .remainder_long()
        # Stack: time (nanoseconds)
        .load_long(0)
        # Stack: time (nanoseconds), timespec
        .push_long(LONG_SIZE)
        # Stack: time (nanoseconds), timespec, 8
        .add_long()
        # Stack: time (nanoseconds), timespec + 8 (*timspec.tv_nsec)
        .invoke_static(context.store_64_method)
        # Stack: (empty)
        .branch("exit0")
        .end_branch()
        .label("exit-1")
        .end_branch()
        .push_long(-1)
        .return_long()
        .label("exit0")
        .end_branch()
        .push_long(0)
        .return_long()
    )