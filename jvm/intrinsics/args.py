from collections import deque

from jawa.assemble import Label
from jawa.attributes.bootstrap import BootstrapMethod

from jvm.commons import push_int, LONG_SIZE, push_constant
from jvm.context import GenerateContext


def prepare_argv_method_instructions(context: GenerateContext):
    instructions = deque()
    local_variable_index = 1

    # Variables:
    # local_variable_index + 1: counter
    counter = local_variable_index + 1

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
    bootstrap_method = 0
    bootstrap_methods: list = context.cf.bootstrap_methods

    context.cf.constants.append((15, 6, context.cf.constants.create_method_ref(
        "java/lang/invoke/StringConcatFactory",
        "makeConcatWithConstants",
        "(Ljava/lang/invoke/MethodHandles$Lookup;Ljava/lang/String;Ljava/lang/invoke/MethodType;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/invoke/CallSite;",
    ).index))
    method_handle = context.cf.constants.get(context.cf.constants.raw_count - 1)
    bootstrap_methods.append(
        BootstrapMethod(method_handle.index, (context.cf.constants.create_string("\1=\1\0").index,)))

    context.cf.constants.append((18, bootstrap_method, context.cf.constants.create_name_and_type(
        "makeConcatWithConstants", "(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;").index))
    make_concat_with_constants = context.cf.constants.get(context.cf.constants.raw_count - 1)

    instructions = deque()
    local_variable_index = 0
    # Variables:
    # local_variable_index + 1: counter
    # local_variable_index + 2: offset
    # local_variable_index + 3: iterator
    counter = local_variable_index + 1
    offset = local_variable_index + 2
    iterator = local_variable_index + 3

    # Stack: (empty)
    instructions.append(
        ("invokestatic", context.cf.constants.create_method_ref("java/lang/System", "getenv", "()Ljava/util/Map;")))
    # Stack: env map
    instructions.append(("dup",))
    # Stack: env map, env map
    instructions.append(
        ("invokeinterface", context.cf.constants.create_interface_method_ref("java/util/Map", "size", "()I"), 1, 0))
    # Stack: env map, env map size
    push_int(context.cf, instructions, LONG_SIZE)
    # Stack: env map, env map size, 8
    instructions.append(("imul",))
    # Stack: env map, env map size * 8
    push_int(context.cf, instructions, LONG_SIZE)
    # Stack: env map, env map size * 8, 8
    instructions.append(("iadd",))
    # Stack: env map, env map size * 8 + 8
    instructions.append(("dup",))
    # Stack: env map, env map size * 8, env map size * 8
    instructions.append(("getstatic", context.memory_ref))
    # Stack: env map, env map size * 8, env map size * 8, memory
    instructions.append(("arraylength",))
    # Stack: env map, env map size * 8, env map size * 8, envp offset
    instructions.append(("dup",))
    # Stack: env map, env map size * 8, env map size * 8, envp offset, envp offset
    instructions.append(("dup",))
    # Stack: env map, env map size * 8, env map size * 8, envp offset, envp offset, envp offset
    instructions.append(("i2l",))
    # Stack: env map, env map size * 8, env map size * 8, envp offset, envp offset, envp offset (as long)
    instructions.append(("putstatic", context.envp_ref))
    # Stack: env map, env map size * 8, env map size * 8, envp offset, envp offset
    instructions.append(("dup_x2",))
    # Stack: env map, env map size * 8, envp offset, env map size * 8, envp offset, envp offset
    instructions.append(("pop",))
    # Stack: env map, env map size * 8, envp offset, env map size * 8, envp offset
    instructions.append(("iadd",))
    # Stack: env map, env map size * 8, envp offset, env map size * 8 + envp offset
    instructions.append(("istore", offset))
    # Stack: env map, env map size * 8, envp offset
    instructions.append(("swap",))
    # Stack: env map, envp offset, env map size * 8
    instructions.append(("invokestatic", context.extend_mem_method))
    instructions.append(("pop2",))
    # Stack: env map, envp offset
    instructions.append(("pop",))
    # Stack: env map

    instructions.append(("invokeinterface",
                         context.cf.constants.create_interface_method_ref("java/util/Map", "entrySet",
                                                                          "()Ljava/util/Set;"), 1, 0))
    # Stack: env map entry set
    instructions.append(("invokeinterface",
                         context.cf.constants.create_interface_method_ref("java/util/Set", "iterator",
                                                                          "()Ljava/util/Iterator;"), 1, 0))
    # Stack: env map entry set iterator
    instructions.append(("astore", iterator))
    # Stack: (empty)
    push_int(context.cf, instructions, 0)
    # Stack: 0
    instructions.append(("istore", counter))
    # Stack: (empty))

    # region insertion loop with iterator
    instructions.append(Label("env_loop"))
    # Stack: (empty)
    instructions.append(("aload", iterator))
    # Stack: env map entry set iterator
    instructions.append(("invokeinterface",
                         context.cf.constants.create_interface_method_ref("java/util/Iterator", "hasNext", "()Z"), 1,
                         0))
    # Stack: has next
    instructions.append(("ifeq", Label("env_loop_exit")))
    # Stack: envp offset
    instructions.append(("aload", iterator))
    # Stack: env map entry set iterator
    instructions.append(("invokeinterface",
                         context.cf.constants.create_interface_method_ref("java/util/Iterator", "next",
                                                                          "()Ljava/lang/Object;"), 1, 0))
    # Stack: entry
    instructions.append(("checkcast", context.cf.constants.create_class("java/util/Map$Entry")))
    # Stack: entry
    instructions.append(("dup",))
    # Stack: entry, entry
    instructions.append(("invokeinterface",
                         context.cf.constants.create_interface_method_ref("java/util/Map$Entry", "getKey",
                                                                          "()Ljava/lang/Object;"), 1, 0))
    # Stack: entry, key
    instructions.append(("checkcast", context.cf.constants.create_class("java/lang/String")))
    # Stack: entry, key
    instructions.append(("swap",))
    # Stack: key, entry
    instructions.append(("invokeinterface",
                         context.cf.constants.create_interface_method_ref("java/util/Map$Entry", "getValue",
                                                                          "()Ljava/lang/Object;"), 1, 0))
    # Stack: key, value
    instructions.append(("checkcast", context.cf.constants.create_class("java/lang/String")))
    # Stack: key, value
    instructions.append(
        ("invokedynamic", make_concat_with_constants, 0, 0))
    # Stack: "key=value"
    instructions.append(("invokestatic", context.put_string_method))
    # Stack: index (as long)
    instructions.append(("getstatic", context.envp_ref))
    # Stack: index (as long), envp offset (as long)
    instructions.append(("l2i",))
    # Stack: index (as long), envp offset
    instructions.append(("iload", counter))
    # Stack: index (as long), envp offset, counter
    push_int(context.cf, instructions, LONG_SIZE)
    # Stack: index (as long), envp offset, counter, 8
    instructions.append(("imul",))
    # Stack: index (as long), envp offset, counter * 8
    instructions.append(("iadd",))
    # Stack: index (as long), envp offset + counter * 8
    instructions.append(("i2l",))
    # Stack: index (as long), envp offset + counter * 8 (as long)
    instructions.append(("invokestatic", context.store_64_method))
    # Stack: envp offset
    instructions.append(("iinc", counter, 1))
    # Stack: envp offset
    instructions.append(("goto", Label("env_loop")))
    # endregion

    instructions.append(Label("env_loop_exit"))
    # Stack: envp offset
    # instructions.append(("pop",))
    # Stack: (empty)

    instructions.append(("return",))

    return instructions
