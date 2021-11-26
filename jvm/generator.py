from collections import deque
from pathlib import Path
from typing import Optional, Union, Iterable

from jawa.assemble import assemble, Label
from jawa.attributes.source_file import SourceFileAttribute
from jawa.cf import ClassFile
from jawa.methods import Method

from extensions.DeduplicatingClassFile import DeduplicatingClassFile
from jvm.commons import count_locals, push_long, push_int, string_get_bytes, \
    ARGC_OFFSET, ARGV_OFFSET, MAX_STACK, print_long_method_instructions, push_constant
from jvm.context import GenerateContext
from jvm.intrinsics.args import add_prepare_argv, add_prepare_envp
from jvm.intrinsics.init import add_init
from jvm.intrinsics.load import load_64, load_64_method_instructions, \
    load_32_method_instructions, load_16_method_instructions, load_8_method_instructions
from jvm.intrinsics.memory import add_increase_mem_method, add_put_string
from jvm.intrinsics.procedures import Procedure
from jvm.intrinsics.store import store_32, store_16, store_8, add_store_64_method
from jvm.intrinsics.syscalls import add_syscall3
from porth.porth import Program, OpType, MemAddr, OpAddr, Intrinsic, Op, Token, TokenType, ParseContext, Proc

PROC_LOAD_16 = "load_16"
PROC_LOAD_8 = "load_8"


def generate_jvm_bytecode(parse_context: ParseContext, program: Program, out_file_path: str):
    context = GenerateContext()
    context.procedures = dict()

    if not program.ops:
        program.ops.append(
            Op(OpType.INTRINSIC, Token(TokenType.KEYWORD, "stop", ("auto-generated", 0, 0), "stop"), Intrinsic.STOP))

    context.program = program

    out_file_path = Path(out_file_path)
    class_name = out_file_path.stem
    out_file_path = out_file_path.with_stem(class_name)

    cf = DeduplicatingClassFile.create(class_name)
    context.cf = cf

    main_method = cf.methods.create("main", "([Ljava/lang/String;)V", code=True)
    main_method.access_flags.acc_public = True
    main_method.access_flags.acc_static = True
    main_method.access_flags.acc_synthetic = True

    cf.attributes.create(SourceFileAttribute).source_file = cf.constants.create_utf8(program.ops[0].token.loc[0])

    memory = cf.fields.create("memory", "[B")
    memory.access_flags.acc_public = False
    memory.access_flags.acc_private = True
    memory.access_flags.acc_static = True
    memory.access_flags.acc_synthetic = True
    context.memory_ref = cf.constants.create_field_ref(cf.this.name.value, memory.name.value, memory.descriptor.value)

    environ = cf.fields.create("environ", "J")
    environ.access_flags.acc_public = False
    environ.access_flags.acc_private = True
    environ.access_flags.acc_static = True
    environ.access_flags.acc_synthetic = True
    context.environ_ref = cf.constants.create_field_ref(cf.this.name.value, environ.name.value,
                                                        environ.descriptor.value)

    context.extend_mem_method = add_increase_mem_method(context)
    context.put_string_method = add_put_string(context)
    context.store_64_method = add_store_64_method(context)
    context.prepare_argv_method = add_prepare_argv(context)
    context.prepare_envp_method = add_prepare_envp(context)
    context.syscall3_method = add_syscall3(context)
    context.clinit_method = add_init(context)

    # Variables:
    # 0: argument array
    # 1: Return pointers
    # 2: Return pointers index

    print_long_method = create_method_prototype(cf, "print_long", "(J)V")
    context.print_long_method = cf.constants.create_method_ref(context.cf.this.name.value,
                                                               print_long_method.name.value,
                                                               print_long_method.descriptor.value)
    create_method_direct(context, print_long_method, print_long_method_instructions(context.cf))

    load_64_method = create_method_prototype(cf, "load_64", "(J)J")
    context.load_64_method = cf.constants.create_method_ref(context.cf.this.name.value,
                                                            load_64_method.name.value,
                                                            load_64_method.descriptor.value)
    create_method_direct(context, load_64_method, load_64_method_instructions(context))

    load_32_method = create_method_prototype(cf, "load_32", "(J)J")
    context.load_32_method = cf.constants.create_method_ref(context.cf.this.name.value,
                                                            load_32_method.name.value,
                                                            load_32_method.descriptor.value)
    create_method_direct(context, load_32_method, load_32_method_instructions(context))

    load_16_method = create_method_prototype(cf, "load_16", "(J)J")
    context.load_16_method = cf.constants.create_method_ref(context.cf.this.name.value,
                                                            load_16_method.name.value,
                                                            load_16_method.descriptor.value)
    create_method_direct(context, load_16_method, load_16_method_instructions(context))

    load_8_method = create_method_prototype(cf, "load_8", "(J)J")
    context.load_8_method = cf.constants.create_method_ref(context.cf.this.name.value,
                                                           load_8_method.name.value,
                                                           load_8_method.descriptor.value)
    create_method_direct(context, load_8_method, load_8_method_instructions(context))

    for name, procedure in parse_context.procs.items():
        method = create_method_prototype(cf, name, make_signature(procedure.contract))
        context.procedures[name] = Procedure(name, procedure.local_memory_capacity,
                                             cf.constants.create_method_ref(context.cf.this.name.value,
                                                                            method.name.value,
                                                                            method.descriptor.value),
                                             procedure.contract)
        create_method(context, method, procedure, program.ops[procedure.addr:])

    create_method(context, main_method, None, program.ops)

    with open(out_file_path, "wb") as f:
        cf.save(f)


def create_method_prototype(cf: ClassFile, name: str, descriptor: str):
    method = cf.methods.create(name, descriptor, code=True)
    method.access_flags.acc_public = False
    method.access_flags.acc_private = True
    method.access_flags.acc_static = True
    method.access_flags.acc_synthetic = True
    return method


def create_method(context: GenerateContext, method: Method, procedure: Optional[Proc], ops: list[Op]):
    instructions = deque()
    current_proc: Optional[OpAddr] = None

    local_variable_index = 0

    if method.name.value == "main":
        instructions.append(("aload_0",))
        instructions.append(("invokestatic", context.prepare_argv_method))
        instructions.append(("invokestatic", context.prepare_envp_method))
    # print_memory(context, instructions)

    if procedure and procedure.local_memory_capacity != 0:
        push_int(context.cf, instructions, procedure.local_memory_capacity)
        instructions.append(("invokestatic", context.extend_mem_method))

    for ip, op in enumerate(ops, 0 if not procedure else procedure.addr):
        # print(ip, op)
        current_label = Label(f"addr_{ip}")

        # Skip procedures inside the code
        if not procedure and current_proc and op.typ != OpType.RET:
            continue

        instructions.append(current_label)

        if op.typ in [OpType.PUSH_INT, OpType.PUSH_PTR]:
            assert isinstance(op.operand, int), f"This could be a bug in the parsing step {op.operand}"
            push_long(context.cf, instructions, op.operand)
        elif op.typ == OpType.PUSH_BOOL:
            assert isinstance(op.operand, int), f"This could be a bug in the parsing step {op.operand}"
            push_long(context.cf, instructions, op.operand)
        elif op.typ == OpType.PUSH_STR:
            assert isinstance(op.operand, str), "This could be a bug in the parsing step"

            string_constant = context.cf.constants.create_string(op.operand)

            push_constant(instructions, string_constant)
            string_get_bytes(context.cf, instructions)
            instructions.append(("arraylength",))
            instructions.append(("i2l",))
            # Stack: string length

            string_get_bytes(context.cf, instructions)
            instructions.append(("invokestatic", context.put_string_method))

            # print_memory(context, instructions)
        elif op.typ == OpType.PUSH_CSTR:
            assert isinstance(op.operand, str), "This could be a bug in the parsing step"
            string_constant = context.cf.constants.create_string(op.operand + "\0")

            string_get_bytes(context.cf, instructions)
            instructions.append(("invokestatic", context.put_string_method))

            # print_memory(context.cf, instructions)

        elif op.typ == OpType.PUSH_MEM:
            assert isinstance(op.operand, MemAddr), "This could be a bug in the parsing step"
            push_long(context.cf, instructions, op.operand)
        elif op.typ == OpType.PUSH_LOCAL_MEM:
            assert isinstance(op.operand, MemAddr), "This could be a bug in the parsing step"
            assert procedure, "No local memory outside a procedure"

            instructions.append(("getstatic", context.memory_ref))
            instructions.append(("arraylength",))
            push_int(context.cf, instructions, procedure.local_memory_capacity)
            instructions.append(("isub",))
            push_int(context.cf, instructions, op.operand)
            instructions.append(("iadd",))
            instructions.append(("i2l",))

        elif op.typ in [OpType.IF, OpType.IFSTAR]:
            assert isinstance(op.operand, OpAddr), f"This could be a bug in the parsing step {op.operand}"
            push_long(context.cf, instructions, 0)
            instructions.append(("lcmp",))
            instructions.append(("ifeq", Label(f"addr_{op.operand}")))
        elif op.typ == OpType.WHILE:
            pass
        elif op.typ == OpType.ELSE:
            assert isinstance(op.operand, OpAddr), "This could be a bug in the parsing step"
            instructions.append(("goto", Label(f"addr_{op.operand}")))
        elif op.typ == OpType.END:
            assert isinstance(op.operand, int), "This could be a bug in the parsing step"
            if ip + 1 != op.operand:
                instructions.append(("goto", Label(f"addr_{op.operand}")))
        elif op.typ == OpType.DO:
            assert isinstance(op.operand, int), "This could be a bug in the parsing step"
            push_long(context.cf, instructions, 0)
            instructions.append(("lcmp",))
            instructions.append(("ifeq", Label(f"addr_{op.operand}")))
        elif op.typ == OpType.SKIP_PROC:
            assert isinstance(op.operand, OpAddr), f"This could be a bug in the parsing step: {op.operand}"

        elif op.typ == OpType.PREP_PROC:
            assert isinstance(op.operand, int)

            if procedure:
                for i in range(len(procedure.contract.ins)):
                    instructions.append(("lload", i * 2))

            current_proc = ip

        elif op.typ == OpType.CALL:
            assert isinstance(op.operand, OpAddr), f"This could be a bug in the parsing step: {op.operand}"

            proc = context.procedures[op.token.value]
            instructions.append(("invokestatic", proc.method_ref))

            if len(proc.contract.outs) > 1:
                instructions.append(("astore", local_variable_index + 1))
                for i in range(len(proc.contract.outs) - 1, -1, -1):
                    instructions.append(("aload", local_variable_index + 1))
                    push_int(context.cf, instructions, i)
                    instructions.append(("laload",))

        elif op.typ == OpType.RET:
            assert isinstance(op.operand, int)

            current_proc = None
            if procedure:
                break

        elif op.typ == OpType.INTRINSIC:
            if op.operand == Intrinsic.PLUS:
                instructions.append(("ladd",))
            elif op.operand == Intrinsic.MINUS:
                instructions.append(("lsub",))
            elif op.operand == Intrinsic.MUL:
                instructions.append(("lmul",))
            elif op.operand == Intrinsic.MAX:
                raise NotImplementedError()
            elif op.operand == Intrinsic.DIVMOD:
                instructions.append(("lstore", local_variable_index + 2))
                instructions.append(("lstore", local_variable_index + 4))
                instructions.append(("lload", local_variable_index + 4))
                instructions.append(("lload", local_variable_index + 2))
                instructions.append(("ldiv",))
                instructions.append(("lload", local_variable_index + 4))
                instructions.append(("lload", local_variable_index + 2))
                instructions.append(("lrem",))
            elif op.operand == Intrinsic.SHR:
                instructions.append(("l2i",))
                instructions.append(("lshr",))
            elif op.operand == Intrinsic.SHL:
                instructions.append(("l2i",))
                instructions.append(("lshl",))
            elif op.operand == Intrinsic.OR:
                instructions.append(("lor",))
            elif op.operand == Intrinsic.AND:
                instructions.append(("land",))
            elif op.operand == Intrinsic.NOT:
                instructions.append(("lneg",))
            elif op.operand == Intrinsic.PRINT:
                instructions.append(("invokestatic", context.print_long_method))
            elif op.operand == Intrinsic.EQ:
                instructions.append(("lcmp",))
                instructions.append(("ifne", Label(f"ne_{ip}")))
                push_long(context.cf, instructions, 1)
                instructions.append(("goto", Label(f"skip_{ip}")))
                instructions.append(Label(f"ne_{ip}"))
                push_long(context.cf, instructions, 0)
                instructions.append(Label(f"skip_{ip}"))
            elif op.operand == Intrinsic.GT:
                instructions.append(("lcmp",))
                instructions.append(("ifle", Label(f"le_{ip}")))
                push_long(context.cf, instructions, 1)
                instructions.append(("goto", Label(f"skip_{ip}")))
                instructions.append(Label(f"le_{ip}"))
                push_long(context.cf, instructions, 0)
                instructions.append(Label(f"skip_{ip}"))
            elif op.operand == Intrinsic.LT:
                instructions.append(("lcmp",))
                instructions.append(("ifge", Label(f"ge_{ip}")))
                push_long(context.cf, instructions, 1)
                instructions.append(("goto", Label(f"skip_{ip}")))
                instructions.append(Label(f"ge_{ip}"))
                push_long(context.cf, instructions, 0)
                instructions.append(Label(f"skip_{ip}"))
            elif op.operand == Intrinsic.GE:
                instructions.append(("lcmp",))
                instructions.append(("iflt", Label(f"lt_{ip}")))
                push_long(context.cf, instructions, 1)
                instructions.append(("goto", Label(f"skip_{ip}")))
                instructions.append(Label(f"lt_{ip}"))
                push_long(context.cf, instructions, 0)
                instructions.append(Label(f"skip_{ip}"))
            elif op.operand == Intrinsic.LE:
                instructions.append(("lcmp",))
                instructions.append(("ifgt", Label(f"gt_{ip}")))
                push_long(context.cf, instructions, 1)
                instructions.append(("goto", Label(f"skip_{ip}")))
                instructions.append(Label(f"gt_{ip}"))
                push_long(context.cf, instructions, 0)
                instructions.append(Label(f"skip_{ip}"))
            elif op.operand == Intrinsic.NE:
                instructions.append(("lcmp",))
                instructions.append(("ifeq", Label(f"eq_{ip}")))
                push_long(context.cf, instructions, 1)
                instructions.append(("goto", Label(f"skip_{ip}")))
                instructions.append(Label(f"eq_{ip}"))
                push_long(context.cf, instructions, 0)
                instructions.append(Label(f"skip_{ip}"))
            elif op.operand == Intrinsic.DUP:
                instructions.append(("dup2",))
            elif op.operand == Intrinsic.SWAP:
                instructions.append(("dup2_x2",))
                instructions.append(("pop2",))
            elif op.operand == Intrinsic.DROP:
                instructions.append(("pop2",))
            elif op.operand == Intrinsic.OVER:
                instructions.append(("dup2_x2",))
                instructions.append(("pop2",))
                instructions.append(("dup2_x2",))
            elif op.operand == Intrinsic.ROT:
                instructions.append(("lstore", local_variable_index + 2))
                instructions.append(("lstore", local_variable_index + 4))
                instructions.append(("lstore", local_variable_index + 6))
                instructions.append(("lload", local_variable_index + 4))
                instructions.append(("lload", local_variable_index + 2))
                instructions.append(("lload", local_variable_index + 6))
            elif op.operand == Intrinsic.LOAD8:
                instructions.append(("invokestatic", context.load_8_method))
            elif op.operand == Intrinsic.STORE8:
                store_8(context, instructions)
            elif op.operand == Intrinsic.LOAD16:
                instructions.append(("invokestatic", context.load_16_method))
            elif op.operand == Intrinsic.STORE16:
                store_16(context, instructions)
            elif op.operand == Intrinsic.LOAD32:
                instructions.append(("invokestatic", context.load_32_method))
            elif op.operand == Intrinsic.STORE32:
                store_32(context, instructions)
            elif op.operand == Intrinsic.LOAD64:
                instructions.append(("invokestatic", context.load_64_method))
            elif op.operand == Intrinsic.STORE64:
                instructions.append(("invokestatic", context.store_64_method))
            elif op.operand == Intrinsic.ARGC:
                instructions.append(("getstatic", context.memory_ref))
                push_long(context.cf, instructions, ARGC_OFFSET + context.program.memory_capacity)
                load_64(context, instructions)
            elif op.operand == Intrinsic.ARGV:
                push_long(context.cf, instructions, ARGV_OFFSET + context.program.memory_capacity)
            elif op.operand == Intrinsic.ENVP:
                instructions.append(("getstatic", context.environ_ref))
                pass
            elif op.operand == Intrinsic.HERE:
                value = ("%s:%d:%d" % op.token.loc)
                push_constant(instructions, context.cf.constants.create_string(value))
                instructions.append(("invokestatic", context.put_string_method))
            elif op.operand in [Intrinsic.CAST_PTR, Intrinsic.CAST_INT, Intrinsic.CAST_BOOL]:
                pass
            elif op.operand == Intrinsic.SYSCALL0:
                # raise NotImplementedError("SYSCALL0")
                instructions.append(("pop2",))
                push_long(context.cf, instructions, 0)
                pass
            elif op.operand == Intrinsic.SYSCALL1:
                # raise NotImplementedError("SYSCALL1")
                instructions.append(("pop2",))
                instructions.append(("pop2",))
                push_long(context.cf, instructions, 0)
                pass
            elif op.operand == Intrinsic.SYSCALL2:
                instructions.append(("pop2",))
                instructions.append(("pop2",))
                instructions.append(("pop2",))
                push_long(context.cf, instructions, 0)
                # raise NotImplementedError("SYSCALL2")
                pass
            elif op.operand == Intrinsic.SYSCALL3:
                instructions.append(("invokestatic", context.syscall3_method))
            elif op.operand == Intrinsic.SYSCALL4:
                instructions.append(("pop2",))
                instructions.append(("pop2",))
                instructions.append(("pop2",))
                instructions.append(("pop2",))
                instructions.append(("pop2",))
                push_long(context.cf, instructions, 0)
                # raise NotImplementedError("SYSCALL4")
                pass
            elif op.operand == Intrinsic.SYSCALL5:
                instructions.append(("pop2",))
                instructions.append(("pop2",))
                instructions.append(("pop2",))
                instructions.append(("pop2",))
                instructions.append(("pop2",))
                instructions.append(("pop2",))
                push_long(context.cf, instructions, 0)
                # raise NotImplementedError("SYSCALL5")
            elif op.operand == Intrinsic.SYSCALL6:
                instructions.append(("pop2",))
                instructions.append(("pop2",))
                instructions.append(("pop2",))
                instructions.append(("pop2",))
                instructions.append(("pop2",))
                instructions.append(("pop2",))
                instructions.append(("pop2",))
                push_long(context.cf, instructions, 0)
                # raise NotImplementedError("SYSCALL6")
                pass
            elif op.operand == Intrinsic.STOP:
                pass
            else:
                raise NotImplementedError(op.operand)

    instructions.append(Label(f"addr_{len(ops)}"))

    if procedure and procedure.local_memory_capacity != 0:
        push_int(context.cf, instructions, -procedure.local_memory_capacity)
        instructions.append(("invokestatic", context.extend_mem_method))

    if procedure:
        if len(procedure.contract.outs) == 0:
            instructions.append(("return",))
        elif len(procedure.contract.outs) == 1:
            instructions.append(("lreturn",))
        else:
            push_int(context.cf, instructions, len(procedure.contract.outs))
            instructions.append(("newarray", 11))
            instructions.append(("astore", local_variable_index + 1))

            for i in range(len(procedure.contract.outs)):
                instructions.append(("aload", local_variable_index + 1))
                push_int(context.cf, instructions, i)
                instructions.append(("dup2_x2",))
                instructions.append(("pop2",))
                instructions.append(("lastore",))

            instructions.append(("aload", local_variable_index + 1))
            instructions.append(("areturn",))

    else:
        instructions.append(("return",))

    method.code.assemble(assemble(instructions))
    method.code.max_locals = count_locals(method.descriptor.value, instructions)
    method.code.max_stack = MAX_STACK


def create_method_direct(context: GenerateContext, method: Method,
                         instructions: Iterable[Union[Label, tuple]]):
    method.code.assemble(assemble(instructions))
    method.code.max_locals = count_locals(method.descriptor.value, instructions)
    method.code.max_stack = MAX_STACK


def make_signature(contract):
    if len(contract.outs) == 0:
        return "(" + "J" * len(contract.ins) + ")" + "V"
    elif len(contract.outs) == 1:
        return "(" + "J" * len(contract.ins) + ")" + "J"
    else:
        return "(" + "J" * len(contract.ins) + ")" + "[J"
