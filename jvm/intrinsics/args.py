from collections import deque

from jawa.assemble import Label, assemble
from jawa.attributes.bootstrap import BootstrapMethod
from jawa.constants import MethodReference

from jvm.commons import push_int, push_long, ARGC_OFFSET, ARGV_OFFSET, LONG_SIZE, count_locals, \
    calculate_max_stack
from jvm.context import GenerateContext


def add_prepare_argv(context: GenerateContext) -> MethodReference:
    prepare_argv_method = context.cf.methods.create("prepare_argv", "([Ljava/lang/String;)V", code=True)
    prepare_argv_method.access_flags.acc_public = False
    prepare_argv_method.access_flags.acc_private = True
    prepare_argv_method.access_flags.acc_static = True
    prepare_argv_method.access_flags.acc_synthetic = True

    instructions = deque()
    local_variable_index = 1
    # Variables:
    # local_variable_index + 1: counter
    # local_variable_index + 2: offset
    counter = local_variable_index + 1
    offset = local_variable_index + 2

    # Store argc
    push_int(context.cf, instructions, LONG_SIZE)
    # Stack: 1
    instructions.append(("invokestatic", context.extend_mem_method))
    # Stack: (empty)
    instructions.append(("aload_0",))
    # Stack: args array
    instructions.append(("arraylength",))
    # Stack: args array length (argc)
    instructions.append(("dup",))
    # Stack: args array length (argc), args array length (argc)
    instructions.append(("i2l",))
    # Stack: args array length (argc), args array length (argc, as long)
    push_long(context.cf, instructions, ARGC_OFFSET + context.program.memory_capacity)
    # Stack: args array length (argc), args array length (argc, as long), 0
    instructions.append(("invokestatic", context.store_64_method))

    # Stack: args array length (argc)
    instructions.append(("dup",))
    # Stack: args array length (argc), args array length (argc)
    push_int(context.cf, instructions, LONG_SIZE)  # 8 bytes
    # Stack: args array length (argc), args array length (argc), 8
    instructions.append(("imul",))
    # Stack: args array length (argc), args array length (argc) * 8
    instructions.append(("invokestatic", context.extend_mem_method))
    # Stack: args array length (argc)

    # Store offset
    instructions.append(("getstatic", context.memory_ref))
    # Stack: args array length (argc), memory
    instructions.append(("arraylength",))
    # Stack: args array length (argc), memory capacity
    instructions.append(("istore", offset))

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
    # Stack: args array length (argc), offset
    push_int(context.cf, instructions, ARGV_OFFSET + context.program.memory_capacity)
    # Stack: args array length (argc), offset, 1
    instructions.append(("iload", counter))
    # Stack: args array length (argc), offset (as long), ARGV_OFFSET, index
    push_int(context.cf, instructions, LONG_SIZE)
    # Stack: args array length (argc), offset (as long), ARGV_OFFSET, index, 8
    instructions.append(("imul",))
    # Stack: args array length (argc), offset (as long), ARGV_OFFSET, index * 8
    instructions.append(("iadd",))
    # Stack: args array length (argc), offset (as long), ARGV_OFFSET + index * 8
    instructions.append(("i2l",))
    # Stack: args array length (argc), offset (as long), ARGV_OFFSET + index * 8 (as long)
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
    instructions.append(("return",))

    prepare_argv_method.code.assemble(assemble(instructions))
    prepare_argv_method.code.max_stack = calculate_max_stack(context, assemble(instructions))
    prepare_argv_method.code.max_locals = count_locals(prepare_argv_method.descriptor.value, instructions)

    return context.cf.constants.create_method_ref(context.cf.this.name.value, prepare_argv_method.name.value,
                                                  prepare_argv_method.descriptor.value)


def add_prepare_envp(context: GenerateContext) -> MethodReference:
    method = context.cf.methods.create("prepare_envp", "()V", code=True)
    method.access_flags.acc_public = False
    method.access_flags.acc_private = True
    method.access_flags.acc_static = True
    method.access_flags.acc_synthetic = True

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
    instructions.append(("putstatic", context.environ_ref))
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
    instructions.append(("getstatic", context.environ_ref))
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

    method.code.assemble(assemble(instructions))
    method.code.max_stack = calculate_max_stack(context, assemble(instructions))
    method.code.max_locals = count_locals(method.descriptor.value, instructions)

    return context.cf.constants.create_method_ref(context.cf.this.name.value, method.name.value,
                                                  method.descriptor.value)
