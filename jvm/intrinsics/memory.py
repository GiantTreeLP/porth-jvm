from collections import deque
from typing import MutableSequence

from jvm.commons import push_int, system_arraycopy, string_get_bytes
from jvm.context import GenerateContext


def increase_mem_capacity(context: GenerateContext, instructions: MutableSequence):
    # Stack: additional size
    instructions.append(("getstatic", context.memory_ref))
    # Stack: additional size, memory
    instructions.append(("arraylength",))
    # Stack: additional size, memory capacity
    instructions.append(("iadd",))
    # Stack: additional size + memory capacity
    instructions.append(("newarray", 8))  # byte array
    # Stack: new array
    instructions.append(("dup",))
    # Stack: new array, new array
    instructions.append(("getstatic", context.memory_ref))
    # Stack: new array, new array, memory
    instructions.append(("swap",))
    # Stack: new array, memory, new array
    push_int(context.cf, instructions, 0)
    # Stack: new array, memory, new array, 0
    instructions.append(("swap",))
    # Stack: new array, memory, 0, new array
    push_int(context.cf, instructions, 0)
    # Stack: new array, memory, 0, new array, 0
    instructions.append(("getstatic", context.memory_ref))
    # Stack: new array, memory, 0, new array, 0, memory
    instructions.append(("arraylength",))
    # Stack: new array, memory, 0, new array, 0, memory capacity
    instructions.append(("dup",))
    # Stack: new array, memory, 0, new array, 0, memory capacity, memory capacity
    instructions.append(("iload_0",))
    # Stack: new array, memory, 0, new array, 0, memory capacity, memory capacity, additional size
    instructions.append(("iadd",))
    # Stack: new array, memory, 0, new array, 0, memory capacity, memory capacity + additional size
    instructions.append(("invokestatic", context.cf.constants.create_method_ref("java/lang/Math", "min", "(II)I")))
    # Stack: new array, memory, 0, new array, 0, min(memory capacity + additional size, memory capacity)
    system_arraycopy(context.cf, instructions)
    # Stack: new array
    instructions.append(("putstatic", context.memory_ref))
    # Stack: (empty)


def extend_mem_method_instructions(context: GenerateContext):
    instructions = deque()
    instructions.append(("iload_0",))
    increase_mem_capacity(context, instructions)
    instructions.append(("return",))

    return instructions


def put_string(context: GenerateContext, instructions: MutableSequence):
    instructions.append(("getstatic", context.memory_ref))
    # Stack: memory
    instructions.append(("arraylength",))
    # Stack: memory size (insertion index)
    instructions.append(("dup",))
    # Stack: memory size (insertion index), index

    instructions.append(("aload_0",))

    # Stack: memory size (insertion index), index, string
    string_get_bytes(context.cf, instructions)
    # Stack: memory size (insertion index), index, string as bytes
    instructions.append(("dup",))
    # Stack: memory size (insertion index), index, string as bytes, string as bytes
    instructions.append(("arraylength",))
    # Stack: memory size (insertion index), index, string as bytes, string length
    instructions.append(("dup",))
    # Stack: memory size (insertion index), index, string as bytes, string length, string length
    instructions.append(("invokestatic", context.extend_mem_method))
    # Stack: memory size (insertion index), index, string as bytes, string length
    instructions.append(("dup2_x1",))
    # Stack: memory size (insertion index), string as bytes, string length, index, string as bytes,
    # string length
    instructions.append(("pop2",))
    # Stack: memory size (insertion index), string as bytes, string length, index
    push_int(context.cf, instructions, 0)
    # Stack: memory size (insertion index), string as bytes, string length, index, 0
    instructions.append(("swap",))
    # Stack: memory size (insertion index), string as bytes, string length, 0, index
    instructions.append(("dup2_x1",))
    # Stack: memory size (insertion index), string as bytes, 0, index, string length, 0, index
    instructions.append(("pop2",))
    # Stack: memory size (insertion index), string as bytes, 0, index, string length
    instructions.append(("getstatic", context.memory_ref))
    # Stack: memory size (insertion index), string as bytes, 0, index, string length, memory
    instructions.append(("dup_x2",))
    # Stack: memory size (insertion index), string as bytes, 0, memory, index, string length, memory
    instructions.append(("pop",))
    # Stack: memory size (insertion index), string as bytes, 0, memory, index, string length
    system_arraycopy(context.cf, instructions)
    # Stack: memory size (insertion index)
    instructions.append(("i2l",))
    # Stack: index (as long)


def put_string_method_instructions(context: GenerateContext):
    instructions = deque()

    put_string(context, instructions)
    instructions.append(("lreturn",))

    return instructions
