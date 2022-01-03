from jvm.commons import LONG_SIZE
from jvm.context import GenerateContext
from jvm.instructions import Instructions
from jvm.syscalls import SysCalls


def syscall3_method_instructions(context: GenerateContext):
    return (
        Instructions(context)
        .load_long(6)
        .convert_long_to_integer()
        .lookup_switch("exit0", {
            SysCalls.READ: "read",
            SysCalls.WRITE: "write",
            SysCalls.EXECVE: "execve",
        })
        .label("read")
        .load_long(4)
        .convert_long_to_integer()
        .get_static_field(context.fd_ref)
        .swap()
        .load_array_reference()
        .new(context.cf.constants.create_class("java/io/FileInputStream"))
        .duplicate_behind_top_of_stack()
        .duplicate_behind_top_of_stack()
        .pop()
        .invoke_special(context.cf.constants.create_method_ref("java/io/FileInputStream",
                                                               "<init>",
                                                               "(Ljava/io/FileDescriptor;)V"))
        .get_static_field(context.memory_ref)
        .load_long(2)
        .convert_long_to_integer()
        .load_long(0)
        .convert_long_to_integer()
        .invoke_virtual(context.cf.constants.create_method_ref("java/io/FileInputStream",
                                                               "read",
                                                               "([BII)I"))
        .duplicate_top_of_stack()
        .push_integer(-1)
        .branch_if_integer_not_equal("read_return_value")  # if read() != -1, goto read_return_value
        .push_integer(0)
        .swap()
        .pop()
        .label("read_return_value")
        .convert_integer_to_long()
        .return_long()
        .end_branch()

        .label("write")
        .load_long(4)
        .convert_long_to_integer()
        .get_static_field(context.fd_ref)
        .swap()
        .load_array_reference()
        .new(context.cf.constants.create_class("java/io/FileOutputStream"))
        .duplicate_behind_top_of_stack()
        .duplicate_behind_top_of_stack()
        .pop()
        .invoke_special(context.cf.constants.create_method_ref("java/io/FileOutputStream",
                                                               "<init>",
                                                               "(Ljava/io/FileDescriptor;)V"))
        .duplicate_top_of_stack()
        .get_static_field(context.memory_ref)
        .load_long(2)
        .convert_long_to_integer()
        .load_long(0)
        .convert_long_to_integer()
        .invoke_virtual(context.cf.constants.create_method_ref("java/io/OutputStream",
                                                               "write",
                                                               "([BII)V"))
        .invoke_virtual(context.cf.constants.create_method_ref("java/io/OutputStream",
                                                               "flush",
                                                               "()V"))
        .load_long(0)
        .return_long()
        .end_branch()

        .label("execve")
        .new(context.cf.constants.create_class("java/lang/ProcessBuilder"))
        # Stack: process builder
        .duplicate_top_of_stack()
        # Stack: process builder, process builder

        # Add command and args to this list
        .new(context.cf.constants.create_class("java/util/LinkedList"))
        .duplicate_top_of_stack()
        .invoke_special(context.cf.constants.create_method_ref("java/util/LinkedList",
                                                               "<init>",
                                                               "()V"))
        .duplicate_top_of_stack()

        # Add command to the list
        .load_long(4)
        .invoke_static(context.cstring_to_string_method)
        .invoke_interface(context.cf.constants.create_interface_method_ref("java/util/List",
                                                                           "add",
                                                                           "(Ljava/lang/Object;)Z"))

        .drop()

        # Add args to the list
        .load_long(2)
        # Stack: list, *argv
        .label("add_args_loop")
        .duplicate_long()
        # Stack: list, *argv, *argv
        .invoke_static(context.load_64_method)
        # Stack: list, *argv, memory[*argv]
        .duplicate_long()
        # Stack: list, *argv, memory[*argv], memory[*argv]
        .push_long(0)
        # Stack: list, *argv, memory[*argv], memory[*argv], 0
        .compare_long()
        # Stack: list, *argv, memory[*argv], result (int)
        .branch_if_equal("add_args_end")
        # Stack: list, *argv, memory[*argv]
        # .duplicate_long()
        # .invoke_static(context.print_long_method)
        .invoke_static(context.cstring_to_string_method)
        # Stack: list, *argv, string
        .move_short_behind_long()
        # Stack: list, string, *argv
        .move_top_2_behind_long()  # Moves a long behind two shorts (behind list)
        # Stack: *argv, list, string
        .swap()
        # Stack: *argv, string, list
        .duplicate_behind_top_of_stack()
        # Stack: *argv, list, string, list
        .swap()
        # Stack: *argv, list, list, string
        .invoke_interface(context.cf.constants.create_interface_method_ref("java/util/List",
                                                                           "add",
                                                                           "(Ljava/lang/Object;)Z"))
        # Stack: *argv, list, result (boolean)
        .drop()
        # Stack: *argv, list
        .move_short_behind_long()
        # Stack: list, *argv
        .push_long(LONG_SIZE)
        # Stack: list, *argv, 8
        .add_long()
        # Stack: list, *argv + 8
        .branch("add_args_loop")
        .end_branch()
        .label("add_args_end")
        .end_branch()
        # Stack: list, *argv
        .drop_long()
        .drop_long()

        # Construct the process builder and start the process
        .invoke_special(context.cf.constants.create_method_ref("java/lang/ProcessBuilder",
                                                               "<init>",
                                                               "(Ljava/util/List;)V"))

        # Add the environment variables
        .duplicate_top_of_stack()
        .invoke_virtual(context.cf.constants.create_method_ref("java/lang/ProcessBuilder",
                                                               "environment",
                                                               "()Ljava/util/Map;"))
        .duplicate_top_of_stack()
        .invoke_interface(context.cf.constants.create_interface_method_ref("java/util/Map",
                                                                           "clear",
                                                                           "()V"))
        # Stack: process env map
        # Stack: process env map
        .get_static_field(context.envp_ref)
        # Stack: process env map, envp
        .convert_long_to_integer()
        # Stack: process env map, envp (as int)
        .label("add_env_loop")
        .duplicate_top_of_stack()
        # Stack: process env map, envp, envp
        .convert_integer_to_long()
        .invoke_static(context.load_64_method)
        # Stack: process env map, envp, memory[envp]
        .duplicate_long()
        # Stack: process env map, envp, memory[envp], memory[envp]
        .push_long(0)
        # Stack: process env map, envp, memory[envp], memory[envp], 0
        .compare_long()
        # Stack: process env map, envp, memory[envp], result (int)
        .branch_if_equal("add_env_end")
        # Stack: process env map, envp, memory[envp]
        .invoke_static(context.cstring_to_string_method)
        # Stack: process env map, envp, string
        .push_constant(context.cf.constants.create_string("="))
        # Stack: process env map, envp, string, "="
        .push_integer(2)
        # Stack: process env map, envp, string, "=", 2
        .invoke_virtual(context.cf.constants.create_method_ref("java/lang/String",
                                                               "split",
                                                               "(Ljava/lang/String;I)[Ljava/lang/String;"))
        # Stack: process env map, envp, array[key, value]
        .duplicate_top_of_stack()
        # Stack: process env map, envp, array[key, value], array[key, value]
        .push_integer(0)
        # Stack: process env map, envp, array[key, value], array[key, value], 0
        .load_array_reference()
        # Stack: process env map, envp, array[key, value], key
        .swap()
        # Stack: process env map, envp, key, array[key, value]
        .push_integer(1)
        # Stack: process env map, envp, key, array[key, value], 1
        .load_array_reference()
        # Stack: process env map, envp, key, value
        .move_top_2_behind_long()
        # Stack: key, value, process env map, envp
        .duplicate_top_2_behind_top_4_of_stack()
        # Stack: process env map, envp, key, value, process env map, envp
        .drop()
        # Stack: process env map, envp, key, value, process env map
        .move_short_behind_top_2_of_stack()
        # Stack: process env map, envp, process env map, key, value
        .invoke_interface(context.cf.constants.create_interface_method_ref("java/util/Map",
                                                                           "put",
                                                                           "(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;"))
        .drop()
        # Stack: process env map, envp
        .push_integer(LONG_SIZE)
        # Stack: process env map, envp, 8
        .add_integer()
        # Stack: process env map, envp + 8
        .branch("add_env_loop")
        .end_branch()
        .label("add_env_end")
        # Stack: process env map, envp, memory[envp]
        .end_branch()
        .drop_long()
        # Stack: process env map, envp
        .pop2()
        # Stack: (empty)

        .duplicate_top_of_stack()
        .invoke_virtual(context.cf.constants.create_method_ref("java/lang/ProcessBuilder",
                                                               "inheritIO",
                                                               "()Ljava/lang/ProcessBuilder;"))
        .invoke_virtual(context.cf.constants.create_method_ref("java/lang/ProcessBuilder",
                                                               "start",
                                                               "()Ljava/lang/Process;"))
        .invoke_virtual(context.cf.constants.create_method_ref("java/lang/Process",
                                                               "waitFor",
                                                               "()I"))
        .convert_integer_to_long()
        .push_long(SysCalls.EXIT)
        .invoke_static(context.syscall1_method)
        .return_long()
        .end_branch()

        .label("exit0")
        .end_branch()
        .push_long(0)
        .return_long()
    )