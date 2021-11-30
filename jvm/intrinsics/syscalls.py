from collections import deque

from jawa.assemble import assemble, Label

from jvm.commons import count_locals, push_long, calculate_max_stack
from jvm.context import GenerateContext

SYSCALL_READ = 0x0
SYSCALL_WRITE = 0x1

STDIN = 0
STDOUT = 1
STDERR = 2


def add_syscall3(context: GenerateContext):
    method = context.cf.methods.create("syscall3", "(JJJJ)J", code=True)
    method.access_flags.acc_public = False
    method.access_flags.acc_private = True
    method.access_flags.acc_static = True
    method.access_flags.acc_synthetic = True

    instructions = deque()

    instructions.append(("lload", 6))
    instructions.append(("l2i",))
    # Stack: syscall id
    instructions.append(("lookupswitch", {
        SYSCALL_READ: Label("read"),
        SYSCALL_WRITE: Label("write"),
    }, Label("exit")))

    # region: write
    instructions.append(Label("write"))

    instructions.append(("lload", 4))
    # Stack: fd
    instructions.append(("l2i",))
    # Stack: fd

    instructions.append(("lookupswitch", {
        STDOUT: Label("write_out"),
        STDERR: Label("write_err"),
    }, Label("exit")))

    instructions.append(Label("write_out"))
    instructions.append(
        ("getstatic", (context.cf.constants.create_field_ref("java/lang/System", "out", "Ljava/io/PrintStream;"))))
    instructions.append(("goto", Label("write_printstream")))

    instructions.append(Label("write_err"))
    instructions.append(
        ("getstatic", (context.cf.constants.create_field_ref("java/lang/System", "err", "Ljava/io/PrintStream;"))))
    instructions.append(("goto", Label("write_printstream")))

    instructions.append(Label("write_printstream"))
    instructions.append(("getstatic", context.memory_ref))
    # Stack: string, string, memory
    instructions.append(("lload", 2))
    # Stack: string, string, memory, offset
    instructions.append(("l2i",))
    # Stack: string, string, memory, offset
    instructions.append(("lload", 0))
    # Stack: string, string, memory, offset, length
    instructions.append(("l2i",))
    # Stack: string, string, memory, offset, length

    instructions.append(("invokevirtual", context.cf.constants.create_method_ref(
        "java/io/OutputStream",
        "write",
        "([BII)V"
    )))

    instructions.append(("goto", Label("exit")))
    # endregion

    instructions.append(Label("read"))

    instructions.append(Label("exit"))

    push_long(context.cf, instructions, 0)
    instructions.append(("lreturn",))

    method.code.assemble(assemble(instructions))
    method.code.max_locals = count_locals(method.descriptor.value, instructions)
    method.code.max_stack = calculate_max_stack(context, assemble(instructions))

    return context.cf.constants.create_method_ref(context.cf.this.name.value, method.name.value,
                                                  method.descriptor.value)
