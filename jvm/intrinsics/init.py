from collections import deque

from jvm.commons import push_int
from jvm.context import GenerateContext


def clinit_method_instructions(context: GenerateContext):
    instructions = deque()
    push_int(context.cf, instructions, context.program.memory_capacity)
    instructions.append(("newarray", 8))  # byte array
    instructions.append(("putstatic", context.memory_ref))
    push_int(context.cf, instructions, 3)  # Size
    instructions.append(("anewarray", context.cf.constants.create_class("java/io/FileDescriptor")))

    instructions.append(("dup",))
    push_int(context.cf, instructions, 0)
    instructions.append(
        ("getstatic",
         (context.cf.constants.create_field_ref("java/io/FileDescriptor", "in", "Ljava/io/FileDescriptor;"))))
    instructions.append(("aastore",))

    instructions.append(("dup",))
    push_int(context.cf, instructions, 1)
    instructions.append(
        ("getstatic",
         (context.cf.constants.create_field_ref("java/io/FileDescriptor", "out", "Ljava/io/FileDescriptor;"))))
    instructions.append(("aastore",))

    instructions.append(("dup",))
    push_int(context.cf, instructions, 2)
    instructions.append(
        ("getstatic",
         (context.cf.constants.create_field_ref("java/io/FileDescriptor", "err", "Ljava/io/FileDescriptor;"))))
    instructions.append(("aastore",))

    instructions.append(("putstatic", context.fd_ref))
    instructions.append(("return",))

    return instructions
