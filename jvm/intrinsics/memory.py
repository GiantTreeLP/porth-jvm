from typing import MutableSequence

from jawa.assemble import Label

from jvm.commons import push_int, print_string, push_constant, print_long, \
    LONG_SIZE
from jvm.context import GenerateContext
from jvm.instructions import Instructions
from jvm.intrinsics import OperandType


def extend_mem_method_instructions(context: GenerateContext) -> Instructions:
    return (
        Instructions(context)
        .get_static_field(context.memory_ref)
        .array_length()
        .duplicate_top_of_stack()
        .load_integer(0)
        .add_integer()
        .new_array(OperandType.Byte.array_type)
        .duplicate_top_of_stack()
        .get_static_field(context.memory_ref)
        .swap()
        .push_integer(0)
        .swap()
        .push_integer(0)
        .get_static_field(context.memory_ref)
        .array_length()
        .duplicate_top_of_stack()
        .push_integer(0)
        .add_integer()
        .invoke_static(context.cf.constants.create_method_ref("java/lang/Math", "min", "(II)I"))
        .array_copy()
        .put_static_field(context.memory_ref)
        .convert_integer_to_long()
        .return_long()
    )


def put_string_method_instructions(context: GenerateContext) -> Instructions:
    return (
        Instructions(context)
        .load_reference(0)
        .invoke_virtual(context.cf.constants.create_method_ref(
            "java/lang/String",
            "getBytes",
            "()[B"
        ))
        .duplicate_top_of_stack()
        .array_length()
        .duplicate_top_of_stack()
        .invoke_static(context.extend_mem_method)
        .convert_long_to_integer()
        .duplicate_behind_top_2_of_stack()
        .swap()
        .push_integer(0)
        .duplicate_behind_top_2_of_stack()
        .pop()
        .get_static_field(context.memory_ref)
        .duplicate_behind_top_2_of_stack()
        .pop()
        .array_copy()
        .convert_integer_to_long()
        .return_long()
    )


def cstrlen(context: GenerateContext, instructions: MutableSequence):
    # Stack: cstr pointer
    instructions.append(("l2i",))
    # Stack: cstr pointer (as int)
    instructions.append(("dup",))
    # Stack: cstr pointer, cstr pointer
    instructions.append(Label("cstrlen_loop"))
    instructions.append(("dup",))
    # Stack: cstr pointer, cstr pointer, cstr pointer
    instructions.append(("i2l",))
    # Stack: cstr pointer, cstr pointer, cstr pointer (as long)
    instructions.append(("invokestatic", context.load_8_method))
    # Stack: cstr pointer, cstr pointer, byte
    instructions.append(("l2i",))
    # Stack: cstr pointer, cstr pointer, byte (as int)
    instructions.append(("ifeq", Label("cstrlen_loop_end")))
    push_int(context.cf, instructions, 1)
    # Stack: cstr pointer, cstr pointer, 1
    instructions.append(("iadd",))
    # Stack: cstr pointer, cstr pointer + 1
    instructions.append(("goto", Label("cstrlen_loop")))
    instructions.append(Label("cstrlen_loop_end"))
    instructions.append(("swap",))
    # Stack: cstr pointer + 1, cstr pointer
    instructions.append(("isub",))
    # Stack: cstr length
    instructions.append(("i2l",))
    # Stack: cstr length (as long)


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
    # Stack: counter, counter * 8, argv pointer
    instructions.append(("invokestatic", context.load_64_method))
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
    print_long(context.cf, instructions)
    instructions.append(("pop2",))
    push_int(context.cf, instructions, 1)
    instructions.append(("iadd",))
    instructions.append(("goto", Label("loop_start")))

    instructions.append(Label("loop_end"))
    # Stack: counter
    instructions.append(("pop",))
    # Stack: (empty)


def cstring_to_string_method_instructions(context: GenerateContext) -> Instructions:
    return (
        Instructions(context)
        .load_long(0)
        # Stack: cstr pointer
        .convert_long_to_integer()
        # Stack: cstr pointer (as int)
        .new(context.cf.constants.create_class("java/lang/String"))
        # Stack: cstr pointer (as int), String
        .duplicate_top_of_stack()
        # Stack: cstr pointer (as int), String, String
        .duplicate_top_2_behind_top_3_of_stack()
        # Stack: String, String, cstr pointer (as int), String, String
        .pop2()
        # Stack: String, String, cstr pointer (as int)
        .duplicate_top_of_stack()
        # Stack: String, String, cstr pointer, cstr pointer
        .cstrlen(0)
        # Stack: String, String, cstr pointer, length
        .get_static_field(context.memory_ref)
        # Stack: String, String, cstr pointer, length, memory
        .move_short_behind_top_2_of_stack()
        # Stack: String, String, memory, cstr pointer, length
        .get_static_field(
            context.cf.constants.create_field_ref("java/nio/charset/StandardCharsets", "UTF_8",
                                                  "Ljava/nio/charset/Charset;")
        )
        # Stack: String, String, memory, cstr pointer, length, charset
        .invoke_special(context.cf.constants.create_method_ref("java/lang/String", "<init>",
                                                               "([BIILjava/nio/charset/Charset;)V"))
        # Stack: string
        .return_reference()
    )
