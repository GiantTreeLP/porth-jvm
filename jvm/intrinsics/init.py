from collections import deque

from jvm.commons import push_int
from jvm.context import GenerateContext


def clinit_method_instructions(context: GenerateContext):
    instructions = deque()
    push_int(context.cf, instructions, context.program.memory_capacity)
    instructions.append(("newarray", 8))  # byte array
    instructions.append(("putstatic", context.memory_ref))
    instructions.append(("return",))

    return instructions
