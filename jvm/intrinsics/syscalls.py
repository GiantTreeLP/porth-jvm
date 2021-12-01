from collections import deque

from jawa.assemble import Label

from jvm.commons import push_long
from jvm.context import GenerateContext

SYSCALL_READ = 0x0
SYSCALL_WRITE = 0x1

STDIN = 0
STDOUT = 1
STDERR = 2


def syscall3_method_instructions(context: GenerateContext):
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

    return instructions
