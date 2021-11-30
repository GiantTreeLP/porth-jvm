from collections import deque

from jawa.assemble import assemble

from jvm.commons import push_int, count_locals, calculate_max_stack
from jvm.context import GenerateContext


def add_init(context: GenerateContext):
    init_method = context.cf.methods.create("<clinit>", "()V", code=True)
    init_method.access_flags.acc_public = False
    init_method.access_flags.acc_private = True
    init_method.access_flags.acc_static = True
    init_method.access_flags.acc_synthetic = True

    instructions = deque()
    push_int(context.cf, instructions, context.program.memory_capacity)
    instructions.append(("newarray", 8))  # byte array
    instructions.append(("putstatic", context.memory_ref))
    instructions.append(("return",))

    init_method.code.assemble(assemble(instructions))
    init_method.code.max_stack = calculate_max_stack(context, assemble(instructions))
    init_method.code.max_locals = count_locals(init_method.descriptor.value, instructions)

    return context.cf.constants.create_method_ref(context.cf.this.name.value, init_method.name.value,
                                                  init_method.descriptor.value)
