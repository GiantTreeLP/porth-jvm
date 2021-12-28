from collections import deque
from typing import MutableSequence

from jawa.assemble import Label

from jvm.commons import push_int, system_arraycopy, string_get_bytes, print_string, push_constant, print_long, \
    LONG_SIZE
from jvm.context import GenerateContext


def increase_mem_capacity(context: GenerateContext, instructions: MutableSequence):
    instructions.append(("getstatic", context.memory_ref))
    # Stack: memory
    instructions.append(("arraylength",))
    # Stack: memory size
    instructions.append(("dup",))
    # Stack: memory size, memory size
    instructions.append(("iload_0",))
    # Stack: memory size, memory size, additional size
    instructions.append(("iadd",))
    # Stack: memory size, memory size + additional size
    instructions.append(("newarray", 8))  # byte array
    # Stack: new memory pointer, new array
    instructions.append(("dup",))
    # Stack: new memory pointer, new array, new array
    instructions.append(("getstatic", context.memory_ref))
    # Stack: new memory pointer, new array, new array, memory
    instructions.append(("swap",))
    # Stack: new memory pointer, new array, memory, new array
    push_int(context.cf, instructions, 0)
    # Stack: new memory pointer, new array, memory, new array, 0
    instructions.append(("swap",))
    # Stack: new memory pointer, new array, memory, 0, new array
    push_int(context.cf, instructions, 0)
    # Stack: new memory pointer, new array, memory, 0, new array, 0
    instructions.append(("getstatic", context.memory_ref))
    # Stack: new memory pointer, new array, memory, 0, new array, 0, memory
    instructions.append(("arraylength",))
    # Stack: new memory pointer, new array, memory, 0, new array, 0, memory capacity
    instructions.append(("dup",))
    # Stack: new memory pointer, new array, memory, 0, new array, 0, memory capacity, memory capacity
    instructions.append(("iload_0",))
    # Stack: new memory pointer, new array, memory, 0, new array, 0, memory capacity, memory capacity, additional size
    instructions.append(("iadd",))
    # Stack: new memory pointer, new array, memory, 0, new array, 0, memory capacity, memory capacity + additional size
    instructions.append(("invokestatic", context.cf.constants.create_method_ref("java/lang/Math", "min", "(II)I")))
    # Stack: new memory pointer, new array, memory, 0, new array, 0, min(memory capacity + additional size, memory capacity)
    system_arraycopy(context.cf, instructions)
    # Stack: new memory pointer, new array
    instructions.append(("putstatic", context.memory_ref))
    # Stack: new memory pointer
    instructions.append(("i2l",))
    # Stack: new memory pointer (as long)
    instructions.append(("lreturn",))


def extend_mem_method_instructions(context: GenerateContext):
    instructions = deque()

    increase_mem_capacity(context, instructions)

    return instructions


def put_string(context: GenerateContext, instructions: MutableSequence):
    instructions.append(("aload_0",))
    # Stack: string
    string_get_bytes(context.cf, instructions)
    # Stack: bytes
    instructions.append(("dup",))
    # Stack: bytes, bytes
    instructions.append(("arraylength",))
    # Stack: bytes, string length
    instructions.append(("dup",))
    # Stack: bytes, string length, string length
    instructions.append(("invokestatic", context.extend_mem_method))
    # Stack: bytes, string length, insertion index (as long)
    instructions.append(("l2i",))
    # Stack: bytes, string length, insertion index
    instructions.append(("dup_x2",))
    # Stack: insertion index, bytes, string length, insertion index
    instructions.append(("swap",))
    # Stack: insertion index, bytes, insertion index, string length
    push_int(context.cf, instructions, 0)
    # Stack: insertion index, bytes, insertion index, string length, 0
    instructions.append(("dup_x2",))
    # Stack: insertion index, bytes, 0, insertion index, string length, 0
    instructions.append(("pop",))
    # Stack: insertion index, bytes, 0, insertion index, string length
    instructions.append(("getstatic", context.memory_ref))
    # Stack: insertion index, bytes, 0, insertion index, string length, memory
    instructions.append(("dup_x2",))
    # Stack: insertion index, bytes, 0, memory, insertion index, string length, memory
    instructions.append(("pop",))
    # Stack: insertion index, bytes, 0, memory, insertion index, string length
    system_arraycopy(context.cf, instructions)
    # Stack: insertion index
    instructions.append(("i2l",))
    # Stack: insertion index (as long)


def put_string_method_instructions(context: GenerateContext):
    instructions = deque()

    put_string(context, instructions)
    instructions.append(("lreturn",))

    return instructions


def cstrlen(context: GenerateContext, instructions: MutableSequence):
    # Stack: cstr pointer (as long)
    instructions.append(("l2i",))
    # Stack: cstr pointer
    push_int(context.cf, instructions, 0)
    # Stack: cstr pointer, counter
    instructions.append(("swap",))
    # Stack: counter, cstr pointer
    instructions.append(Label("cstr_loop"))
    instructions.append(("dup",))
    # Stack: counter, cstr pointer, cstr pointer
    instructions.append(("i2l",))
    # Stack: counter, cstr pointer, cstr pointer (as long)
    instructions.append(("invokestatic", context.load_8_method))
    # Stack: counter, cstr pointer, cstr byte
    instructions.append(("l2i",))
    # Stack: counter, cstr pointer, cstr byte (as int)
    instructions.append(("ifeq", Label("cstr_loop_end")))
    # Stack: counter, cstr pointer
    push_int(context.cf, instructions, 1)
    # Stack: counter, cstr pointer, 1
    instructions.append(("iadd",))
    # Stack: counter, cstr pointer + 1
    instructions.append(("swap",))
    # Stack: cstr pointer + 1, counter
    push_int(context.cf, instructions, 1)
    # Stack: cstr pointer + 1, counter, 1
    instructions.append(("iadd",))
    # Stack: cstr pointer + 1, counter + 1
    instructions.append(("swap",))
    # Stack: counter + 1, cstr pointer + 1
    instructions.append(("goto", Label("cstr_loop")))

    instructions.append(Label("cstr_loop_end"))
    # Stack: counter, cstr pointer
    instructions.append(("pop",))
    # Stack: counter


def print_memory(context: GenerateContext, instructions: MutableSequence):
    instructions.append(("getstatic", context.memory_ref))
    # Stack: memory
    instructions.append(("invokestatic", context.cf.constants.create_method_ref(
        "java/util/Arrays",
        "toString",
        "([B)Ljava/lang/String;"
    )))
    # Stack: string
    print_string(context.cf, instructions)

    # argc
    push_constant(instructions, context.cf.constants.create_string("argc: "))
    print_string(context.cf, instructions)

    instructions.append(("getstatic", context.argc_ref))
    print_long(context.cf, instructions)

    push_constant(instructions, context.cf.constants.create_string("*argc: "))
    print_string(context.cf, instructions)

    instructions.append(("getstatic", context.argc_ref))
    instructions.append(("invokestatic", context.load_64_method))
    print_long(context.cf, instructions)

    # argv
    push_constant(instructions, context.cf.constants.create_string("argv: "))
    print_string(context.cf, instructions)

    instructions.append(("getstatic", context.argv_ref))
    print_long(context.cf, instructions)

    push_constant(instructions, context.cf.constants.create_string("*argv: "))
    print_string(context.cf, instructions)

    instructions.append(("getstatic", context.argv_ref))
    instructions.append(("invokestatic", context.load_64_method))
    print_long(context.cf, instructions)

    push_constant(instructions, context.cf.constants.create_string("arguments: "))
    print_string(context.cf, instructions)

    push_int(context.cf, instructions, 0)  # Counter
    # Stack: counter
    instructions.append(Label("loop_start"))
    instructions.append(("dup",))
    # Stack: counter, counter
    instructions.append(("getstatic", context.argc_ref))
    # Stack: counter, counter, argc
    instructions.append(("invokestatic", context.load_64_method))
    # Stack: counter, counter, argc
    instructions.append(("l2i",))
    # Stack: counter, counter, argc
    instructions.append(("if_icmpge", Label("loop_end")))
    # Stack: counter
    instructions.append(("dup",))
    # Stack: counter, counter
    push_int(context.cf, instructions, LONG_SIZE)
    # Stack: counter, counter, 8
    instructions.append(("imul",))
    # Stack: counter, counter * 8
    instructions.append(("getstatic", context.argv_ref))
    # Stack: counter, counter * 8, argv
    instructions.append(("l2i",))
    # Stack: counter, counter * 8, argv
    instructions.append(("iadd",))
    # Stack: counter, counter * 8 + argv
    instructions.append(("i2l",))
    # Stack: counter, counter * 8 + argv
    instructions.append(("invokestatic", context.load_64_method))
    # Stack: counter, arg pointer
    instructions.append(("dup2",))
    # Stack: counter, arg pointer, arg pointer
    cstrlen(context, instructions)
    # Stack: counter, arg pointer, arg length
    instructions.append(("i2l",))
    print_long(context.cf, instructions)
    instructions.append(("pop2",))
    push_int(context.cf, instructions, 1)
    instructions.append(("iadd",))
    instructions.append(("goto", Label("loop_start")))

    instructions.append(Label("loop_end"))
    # Stack: counter
    instructions.append(("pop",))
    # Stack: (empty)
