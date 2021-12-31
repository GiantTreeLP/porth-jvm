from collections import deque

from jawa.assemble import Label
from jawa.attributes.bootstrap import BootstrapMethod
from jawa.constants import MethodHandleKind

from jvm.commons import push_int, LONG_SIZE, push_constant
from jvm.context import GenerateContext
from jvm.instructions import Instructions


def prepare_argv_method_instructions(context: GenerateContext):
    local_variable_index = 1

    # Variables:
    # local_variable_index + 1: counter
    counter = local_variable_index + 1

    return (
        Instructions(context)
        .push_integer(LONG_SIZE)
        # Stack: 8
        .invoke_static(context.extend_mem_method)
        # Stack: argc
        .put_static_field(context.argc_ref)
        # Stack: (empty)
        .load_reference(0)
        # Stack: argument array
        .array_length()
        # Stack: argument array length
        .duplicate_top_of_stack()
        # Stack: argument array length, argument array length
        .push_integer(1)
        # Stack: argument array length, argument array length, 1
        .add_integer()
        # Stack: argument array length, argument array length + 1
        .convert_integer_to_long()
        # Stack: argument array length, argument array length + 1 (as long)
        .get_static_field(context.argc_ref)
        # Stack: argument array length, argument array length + 1 (as long), *argc
        .invoke_static(context.store_64_method)
        # Stack: argument array length

        .push_integer(LONG_SIZE)
        # Stack: argument array length, 8
        .invoke_static(context.extend_mem_method)
        # Stack: argument array length, argv
        .put_static_field(context.argv_ref)
        # Stack: argument array length

        .duplicate_top_of_stack()
        # Stack: argument array length, argument array length
        .push_integer(2)
        # Stack: argument array length, argument array length, 2
        .add_integer()
        # Stack: argument array length, argument array length + 2
        .push_integer(LONG_SIZE)
        # Stack: argument array length, argument array length + 2, 8
        .multiply_integer()
        # Stack: argument array length, (argument array length + 2) * 8
        .invoke_static(context.extend_mem_method)
        # Stack: argument array length, argv
        .get_static_field(context.argv_ref)
        # Stack: argument array length, argv, *argv
        .invoke_static(context.store_64_method)
        # Stack: argument array length
        .push_constant(context.cf.constants.create_string(context.program_name + "\0"))
        # Stack: argument array length, program name
        .invoke_static(context.put_string_method)
        # Stack: argument array length, string pointer
        .get_static_field(context.argv_ref)
        # Stack: argument array length, string pointer, *argv
        .invoke_static(context.load_64_method)
        # Stack: argument array length, string pointer, **argv
        .invoke_static(context.store_64_method)
        # Stack: argument array length

        .push_integer(0)
        # Stack: argument array length, 0
        .store_integer(counter)
        # Stack: argument array length

        .label("arg_loop")
        .duplicate_top_of_stack()
        # Stack: argument array length, argument array length
        .load_integer(counter)
        # Stack: argument array length, argument array length, counter
        .branch_if_integer_less_or_equal("arg_loop_exit")  # argc <= counter / while argc > counter
        # Stack: argument array length
        .load_reference(0)
        # Stack: argument array length, argument array
        .load_integer(counter)
        # Stack: argument array length, argument array, counter
        .load_array_reference()
        # Stack: argument array length, args[counter]
        .invoke_static(context.put_string_method)
        # Stack: argument array length, string pointer
        .push_integer(1)
        # Stack: argument array length, string pointer, 1
        .invoke_static(context.extend_mem_method)
        # Stack: argument array length, string pointer, null byte pointer
        .drop_long()
        # Stack: argument array length, string pointer
        .get_static_field(context.argv_ref)
        # Stack: argument array length, string pointer, argv
        .invoke_static(context.load_64_method)
        # Stack: argument array length, string pointer, *argv
        .convert_long_to_integer()
        # Stack: argument array length, string pointer, *argv (as int)
        .load_integer(counter)
        # Stack: argument array length, string pointer, *argv (as int), counter
        .push_integer(1)
        # Stack: argument array length, string pointer, *argv (as int), counter, 1
        .add_integer()
        # Stack: argument array length, string pointer, *argv (as int), counter + 1
        .push_integer(LONG_SIZE)
        # Stack: argument array length, string pointer, *argv (as int), counter + 1, 8
        .multiply_integer()
        # Stack: argument array length, string pointer, *argv (as int), (counter + 1) * 8
        .add_integer()
        # Stack: argument array length, string pointer, (counter + 1) * 8 + *argv
        .convert_integer_to_long()
        # Stack: argument array length, string pointer, (counter + 1) * 8 + *argv (as long)
        .invoke_static(context.store_64_method)
        # Stack: argument array length
        .increment_integer(counter)
        # Stack: argument array length
        .branch("arg_loop")
        .label("arg_loop_exit")
        .drop()
        # Stack: (empty)
        .return_void()
    )

    instructions = deque()
    # Store argc
    push_int(context.cf, instructions, LONG_SIZE)
    # Stack: 1
    instructions.append(("invokestatic", context.extend_mem_method))
    instructions.append(("putstatic", context.argc_ref))
    # Stack: (empty)
    instructions.append(("aload_0",))
    # Stack: args array
    instructions.append(("arraylength",))
    # Stack: args array length (argc)
    instructions.append(("dup",))
    # Stack: args array length (argc), args array length (argc)
    # Account for the implicit first argument (executable name)
    push_int(context.cf, instructions, 1)
    # Stack: args array length (argc), args array length (argc), 1
    instructions.append(("iadd",))
    # Stack: args array length (argc), args array length (argc) + 1
    instructions.append(("i2l",))
    # Stack: args array length (argc), args array length + 1 (argc, as long)
    instructions.append(("getstatic", context.argc_ref))
    # Stack: args array length (argc), args array length (argc, as long), 0
    instructions.append(("invokestatic", context.store_64_method))

    # Allocate argv pointer
    # Stack: args array length (argc)
    push_int(context.cf, instructions, LONG_SIZE)
    # Stack: args array length (argc), 8
    instructions.append(("invokestatic", context.extend_mem_method))
    # Stack: args array length (argc), argv location
    instructions.append(("putstatic", context.argv_ref))
    # Stack: args array length (argc)

    instructions.append(("dup",))
    # Stack: args array length (argc), args array length (argc)
    # Account for the terminating null value and the implicit first argument (executable name)
    push_int(context.cf, instructions, 2)
    # Stack: args array length (argc), args array length (argc), 1
    instructions.append(("iadd",))
    # Stack: args array length (argc), args array length (argc) + 1
    push_int(context.cf, instructions, LONG_SIZE)  # 8 bytes
    # Stack: args array length (argc), args array length (argc), 8
    instructions.append(("imul",))
    # Stack: args array length (argc), args array length (argc) * 8
    instructions.append(("invokestatic", context.extend_mem_method))
    # Stack: args array length (argc), argv table pointer
    instructions.append(("getstatic", context.argv_ref))
    # Stack: args array length (argc), argv table pointer, argv pointer
    instructions.append(("invokestatic", context.store_64_method))
    # Stack: args array length (argc)

    push_constant(instructions, context.cf.constants.create_string(context.program_name + "\0"))
    # Stack: args array length (argc), program name
    instructions.append(("invokestatic", context.put_string_method))
    # Stack: args array length (argc), insertion pointer
    instructions.append(("getstatic", context.argv_ref))
    instructions.append(("invokestatic", context.load_64_method))
    # Stack: args array length (argc), insertion pointer, argv
    instructions.append(("invokestatic", context.store_64_method))
    # Stack: args array length (argc)

    push_int(context.cf, instructions, 0)
    # Stack: args array length (argc), 0
    instructions.append(("istore", counter))
    # Stack: args array length (argc)

    instructions.append(Label("arg_loop"))
    instructions.append(("dup",))
    # Stack: args array length (argc), args array length (argc)
    instructions.append(("iload", counter))
    # Stack: args array length (argc), args array length (argc), index
    instructions.append(("if_icmple", Label("arg_loop_exit")))
    # Stack: args array length (argc)
    instructions.append(("aload_0",))
    # Stack: args array length (argc), args array
    instructions.append(("iload", counter))

    # Stack: args array length (argc), args array, index
    instructions.append(("aaload",))
    # Stack: args array length (argc), args array[index]
    instructions.append(("invokestatic", context.put_string_method))
    # Stack: args array length (argc), offset
    push_int(context.cf, instructions, 1)
    # Stack: args array length (argc), offset, 1
    instructions.append(("invokestatic", context.extend_mem_method))
    instructions.append(("pop2",))
    # Stack: args array length (argc), offset
    instructions.append(("getstatic", context.argv_ref))
    instructions.append(("invokestatic", context.load_64_method))
    instructions.append(("l2i",))
    # Stack: args array length (argc), offset, argv
    instructions.append(("iload", counter))
    # Stack: args array length (argc), offset, argv, counter

    # Account for the implicit first argument (executable name)
    push_int(context.cf, instructions, 1)
    # Stack: args array length (argc), offset, argv, counter, 1
    instructions.append(("iadd",))
    # Stack: args array length (argc), offset, argv, counter + 1

    push_int(context.cf, instructions, LONG_SIZE)
    # Stack: args array length (argc), offset, argv, counter + 1, 8
    instructions.append(("imul",))
    # Stack: args array length (argc), offset, argv, (counter + 1) * 8
    instructions.append(("iadd",))
    # Stack: args array length (argc), offset, ((counter + 1) * 8) + argv
    instructions.append(("i2l",))
    # Stack: args array length (argc), offset, ((counter + 1) * 8) + argv (as long)
    instructions.append(("invokestatic", context.store_64_method))
    # Stack: args array length (argc)
    instructions.append(("iinc", counter, 1))
    # Stack: args array length (argc)
    instructions.append(("goto", Label("arg_loop")))
    # Stack: args array length (argc)
    instructions.append(Label("arg_loop_exit"))
    # Stack: args array length (argc)
    instructions.append(("pop",))
    # Stack: (empty)

    # print_memory(context, instructions)

    instructions.append(("return",))

    return instructions


def prepare_envp_method_instructions(context: GenerateContext):
    bootstrap_methods: list = context.cf.bootstrap_methods

    method_handle = context.cf.constants.create_method_handle(
        MethodHandleKind.INVOKE_STATIC,
        "java/lang/invoke/StringConcatFactory",
        "makeConcatWithConstants",
        "(Ljava/lang/invoke/MethodHandles$Lookup;Ljava/lang/String;Ljava/lang/invoke/MethodType;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/invoke/CallSite;"
    )

    bootstrap_methods.append(
        BootstrapMethod(method_handle.index, (context.cf.constants.create_string("\1=\1\0").index,)))

    make_concat_with_constants = context.cf.constants.create_invoke_dynamic(
        len(bootstrap_methods) - 1,
        "makeConcatWithConstants",
        "(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"
    )

    local_variable_index = 0
    # Variables:
    # local_variable_index + 1: counter
    # local_variable_index + 2: offset
    # local_variable_index + 3: iterator
    counter = local_variable_index + 1
    offset = local_variable_index + 2
    iterator = local_variable_index + 3

    return (
        Instructions(context)
        .invoke_static(context.cf.constants.create_method_ref("java/lang/System", "getenv", "()Ljava/util/Map;"))
        .duplicate_top_of_stack()
        .invoke_interface(context.cf.constants.create_interface_method_ref("java/util/Map", "size", "()I"))
        .push_integer(LONG_SIZE)
        .multiply_integer()
        .push_integer(LONG_SIZE)
        .add_integer()
        .duplicate_top_of_stack()
        .get_static_field(context.memory_ref)
        .array_length()
        .duplicate_top_of_stack()
        .duplicate_top_of_stack()
        .convert_integer_to_long()
        .put_static_field(context.envp_ref)
        .duplicate_behind_top_2_of_stack()
        .pop()
        .add_integer()
        .store_integer(offset)
        .swap()
        .invoke_static(context.extend_mem_method)
        .drop_long()
        .pop()
        .invoke_interface(context.cf.constants.create_interface_method_ref("java/util/Map", "entrySet",
                                                                          "()Ljava/util/Set;"))
        .invoke_interface(context.cf.constants.create_interface_method_ref("java/util/Set", "iterator",
                                                                          "()Ljava/util/Iterator;"))
        .store_reference(iterator)
        .push_integer(0)
        .label("env_loop")
        .load_reference(iterator)
        .invoke_interface(context.cf.constants.create_interface_method_ref("java/util/Iterator", "hasNext",
                                                                          "()Z"))
        .branch_if_false("env_loop_exit")
        .load_reference(iterator)
        .invoke_interface(context.cf.constants.create_interface_method_ref("java/util/Iterator", "next",
                                                                          "()Ljava/lang/Object;"))
        .check_cast(context.cf.constants.create_class("java/util/Map$Entry"))
        .duplicate_top_of_stack()
        .invoke_interface(context.cf.constants.create_interface_method_ref("java/util/Map$Entry", "getKey",
                                                                          "()Ljava/lang/Object;"))
        .check_cast(context.cf.constants.create_class("java/lang/String"))
        .swap()
        .invoke_interface(context.cf.constants.create_interface_method_ref("java/util/Map$Entry", "getValue",
                                                                          "()Ljava/lang/Object;"))
        .check_cast(context.cf.constants.create_class("java/lang/String"))
        .invoke_dynamic(make_concat_with_constants)
        .invoke_static(context.put_string_method)
        .get_static_field(context.envp_ref)
        .convert_long_to_integer()
        .load_integer(counter)
        .push_integer(LONG_SIZE)
        .multiply_integer()
        .add_integer()
        .convert_integer_to_long()
        .invoke_static(context.store_64_method)
        .increment_integer(counter)
        .branch("env_loop")
        .label("env_loop_exit")
        .return_void()
    )
