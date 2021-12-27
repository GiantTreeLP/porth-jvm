from collections import deque

from jawa.assemble import Label

from jvm.commons import push_int
from jvm.context import GenerateContext

SYSCALL_READ = 0x0
SYSCALL_WRITE = 0x1

STDIN = 0
STDOUT = 1
STDERR = 2


def syscall3_method_instructions(context: GenerateContext):
    instructions = deque()

    instructions.append(("lload", 6))
    instructions.append(("l2i",))
    # Stack: syscall id
    instructions.append(("lookupswitch", {
        SYSCALL_READ: Label("read"),
        SYSCALL_WRITE: Label("write"),
    }, Label("exit0")))

    # region: read
    instructions.append(Label("read"))

    instructions.append(("lload", 4))
    # Stack: fd
    instructions.append(("l2i",))
    # Stack: fd

    instructions.append(("getstatic", context.fd_ref))
    # Stack: fd, fd_ref
    instructions.append(("swap",))
    # Stack: fd_ref, fd
    instructions.append(("aaload",))
    # Stack: file descriptor
    instructions.append(("new", context.cf.constants.create_class("java/io/FileInputStream")))
    # Stack: file descriptor, FileOutputStream
    instructions.append(("dup_x1",))
    # Stack: FileOutputStream, file descriptor, FileOutputStream
    instructions.append(("dup_x1",))
    # Stack: FileOutputStream, FileOutputStream, file descriptor, FileOutputStream
    instructions.append(("pop",))
    # Stack: FileOutputStream, FileOutputStream, file descriptor
    instructions.append(("invokespecial", context.cf.constants.create_method_ref("java/io/FileInputStream", "<init>",
                                                                                 "(Ljava/io/FileDescriptor;)V")))
    # Stack: FileOutputStream

    instructions.append(Label("read_printstream"))
    instructions.append(("getstatic", context.memory_ref))
    # Stack: string, string, memory
    instructions.append(("lload_2",))
    # Stack: string, string, memory, offset
    instructions.append(("l2i",))
    # Stack: string, string, memory, offset
    instructions.append(("lload_0",))
    # Stack: string, string, memory, offset, length
    instructions.append(("l2i",))
    # Stack: string, string, memory, offset, length

    instructions.append(("invokevirtual", context.cf.constants.create_method_ref(
        "java/io/InputStream",
        "read",
        "([BII)I"
    )))
    # Stack: read byte count

    # Match the behavior of the JVM to the behavior of the kernel (i.e. return 0 on EOF)

    instructions.append(("dup",))
    # Stack: read byte count, read byte count
    push_int(context.cf, instructions, -1)
    # Stack: read byte count, read byte count, -1
    instructions.append(("if_icmpne", Label("read_return_value")))
    # Stack: read byte count
    push_int(context.cf, instructions, 0)
    instructions.append(("swap",))
    # Stack: 0, read byte count
    instructions.append(("pop",))

    instructions.append(Label("read_return_value"))
    instructions.append(("i2l",))

    instructions.append(("goto", Label("exit")))
    # endregion

    # region: write
    instructions.append(Label("write"))

    instructions.append(("lload", 4))
    # Stack: fd
    instructions.append(("l2i",))
    # Stack: fd

    instructions.append(("getstatic", context.fd_ref))
    # Stack: fd, fd_ref
    instructions.append(("swap",))
    # Stack: fd_ref, fd
    instructions.append(("aaload",))
    # Stack: file descriptor
    instructions.append(("new", context.cf.constants.create_class("java/io/FileOutputStream")))
    # Stack: file descriptor, FileOutputStream
    instructions.append(("dup_x1",))
    # Stack: FileOutputStream, file descriptor, FileOutputStream
    instructions.append(("dup_x1",))
    # Stack: FileOutputStream, FileOutputStream, file descriptor, FileOutputStream
    instructions.append(("pop",))
    # Stack: FileOutputStream, FileOutputStream, file descriptor
    instructions.append(("invokespecial", context.cf.constants.create_method_ref("java/io/FileOutputStream", "<init>",
                                                                                 "(Ljava/io/FileDescriptor;)V")))
    # Stack: FileOutputStream

    instructions.append(Label("write_printstream"))
    instructions.append(("getstatic", context.memory_ref))
    # Stack: string, string, memory
    instructions.append(("lload_2",))
    # Stack: string, string, memory, offset
    instructions.append(("l2i",))
    # Stack: string, string, memory, offset
    instructions.append(("lload_0",))
    # Stack: string, string, memory, offset, length
    instructions.append(("l2i",))
    # Stack: string, string, memory, offset, length

    instructions.append(("invokevirtual", context.cf.constants.create_method_ref(
        "java/io/OutputStream",
        "write",
        "([BII)V"
    )))

    instructions.append(("lload_0",))

    instructions.append(("goto", Label("exit")))
    # endregion

    instructions.append(Label("exit0"))
    instructions.append(("lconst_0",))

    instructions.append(Label("exit"))

    instructions.append(("lreturn",))

    return instructions
