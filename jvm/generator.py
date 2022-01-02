import random
from collections import OrderedDict
from pathlib import Path
from typing import Optional, Dict, Set, List

from jawa.assemble import Label
from jawa.attributes.line_number_table import LineNumberTableAttribute, line_number_entry
from jawa.attributes.source_file import SourceFileAttribute
from jawa.cf import ClassFile
from jawa.methods import Method

from extensions.DeduplicatingClassFile import DeduplicatingClassFile
from jvm.commons import count_locals, print_long_method_instructions
from jvm.context import GenerateContext
from jvm.instructions import Instructions
from jvm.intrinsics import get_method_input_types, OperandType
from jvm.intrinsics.args import prepare_argv_method_instructions, prepare_envp_method_instructions
from jvm.intrinsics.init import clinit_method_instructions
from jvm.intrinsics.load import load_64_method_instructions, \
    load_32_method_instructions, load_16_method_instructions, load_8_method_instructions
from jvm.intrinsics.memory import extend_mem_method_instructions, put_string_method_instructions
from jvm.intrinsics.procedures import Procedure
from jvm.intrinsics.store import store_32, store_16, store_8, store_64_method_instructions
from jvm.intrinsics.syscalls import syscall3_method_instructions, syscall1_method_instructions
from porth.porth import Program, OpType, MemAddr, OpAddr, Intrinsic, Op, Token, TokenType, ParseContext, Proc


def generate_jvm_bytecode(parse_context: ParseContext, program: Program, out_file_path: str,
                          input_path: str):
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
    context.program_name = input_path

    main_method = cf.methods.create("main", "([Ljava/lang/String;)V", code=True)
    main_method.access_flags.acc_public = True
    main_method.access_flags.acc_static = True
    main_method.access_flags.acc_synthetic = True

    cf.attributes.create(SourceFileAttribute).source_file = cf.constants.create_utf8(context.program_name)

    add_fields(context)

    add_utility_methods(context)

    called_procedures = scan_called_procedures(parse_context)

    for name in called_procedures:
        procedure = parse_context.procs[name]
        method_name = name
        signature = make_signature(procedure.contract)
        while cf.methods.find_one(name=method_name, f=lambda m: m.descriptor.value == signature):
            method_name = f"{name}{random.randint(-2 ** 32, 2 ** 32)}"

        method = create_method_prototype(cf, method_name, signature)
        context.procedures[name] = Procedure(name, procedure.local_memory_capacity,
                                             cf.constants.create_method_ref(context.cf.this.name.value,
                                                                            method.name.value,
                                                                            method.descriptor.value),
                                             procedure.contract)
        line_numbers: LineNumberTableAttribute = method.code.attributes.create(LineNumberTableAttribute)
        line_numbers.line_no = [
            line_number_entry(0, program.ops[procedure.addr].token.loc[1]),
        ]
        create_method(context, method, procedure, program.ops[procedure.addr:])

    create_method(context, main_method, None, program.ops)

    with open(out_file_path, "wb") as f:
        cf.save(f)


def add_fields(context: GenerateContext):
    context.memory_ref = add_field(context, "memory", "[B")
    context.argc_ref = add_field(context, "argc", "J")
    context.argv_ref = add_field(context, "argv", "J")
    context.envp_ref = add_field(context, "environ", "J")
    context.fd_ref = add_field(context, "fds", "[Ljava/io/FileDescriptor;")


def add_field(context: GenerateContext, name: str, descriptor: str):
    field = context.cf.fields.create(name, descriptor)
    field.access_flags.acc_public = False
    field.access_flags.acc_private = True
    field.access_flags.acc_static = True
    field.access_flags.acc_synthetic = True
    return context.cf.constants.create_field_ref(context.cf.this.name.value, field.name.value, field.descriptor.value)


def add_utility_methods(context: GenerateContext):
    print_long_method = create_method_prototype(context.cf, "print_long", "(J)V")
    context.print_long_method = context.cf.constants.create_method_ref(context.cf.this.name.value,
                                                                       print_long_method.name.value,
                                                                       print_long_method.descriptor.value)
    create_method_direct(print_long_method, print_long_method_instructions(context))

    load_64_method = create_method_prototype(context.cf, "load_64", "(J)J")
    context.load_64_method = context.cf.constants.create_method_ref(context.cf.this.name.value,
                                                                    load_64_method.name.value,
                                                                    load_64_method.descriptor.value)
    create_method_direct(load_64_method, load_64_method_instructions(context))

    load_32_method = create_method_prototype(context.cf, "load_32", "(J)J")
    context.load_32_method = context.cf.constants.create_method_ref(context.cf.this.name.value,
                                                                    load_32_method.name.value,
                                                                    load_32_method.descriptor.value)
    create_method_direct(load_32_method, load_32_method_instructions(context))

    load_16_method = create_method_prototype(context.cf, "load_16", "(J)J")
    context.load_16_method = context.cf.constants.create_method_ref(context.cf.this.name.value,
                                                                    load_16_method.name.value,
                                                                    load_16_method.descriptor.value)
    create_method_direct(load_16_method, load_16_method_instructions(context))

    load_8_method = create_method_prototype(context.cf, "load_8", "(J)J")
    context.load_8_method = context.cf.constants.create_method_ref(context.cf.this.name.value,
                                                                   load_8_method.name.value,
                                                                   load_8_method.descriptor.value)
    create_method_direct(load_8_method, load_8_method_instructions(context))

    extend_mem_method = create_method_prototype(context.cf, "extend_mem", "(I)J")
    context.extend_mem_method = context.cf.constants.create_method_ref(context.cf.this.name.value,
                                                                       extend_mem_method.name.value,
                                                                       extend_mem_method.descriptor.value)
    create_method_direct(extend_mem_method, extend_mem_method_instructions(context))

    put_string_method = create_method_prototype(context.cf, "put_string", "(Ljava/lang/String;)J")
    context.put_string_method = context.cf.constants.create_method_ref(context.cf.this.name.value,
                                                                       put_string_method.name.value,
                                                                       put_string_method.descriptor.value)
    create_method_direct(put_string_method, put_string_method_instructions(context))

    store_64_method = create_method_prototype(context.cf, "store_64", "(JJ)V")
    context.store_64_method = context.cf.constants.create_method_ref(context.cf.this.name.value,
                                                                     store_64_method.name.value,
                                                                     store_64_method.descriptor.value)
    create_method_direct(store_64_method, store_64_method_instructions(context))

    prepare_argv_method = create_method_prototype(context.cf, "prepare_argv", "([Ljava/lang/String;)V")
    context.prepare_argv_method = context.cf.constants.create_method_ref(context.cf.this.name.value,
                                                                         prepare_argv_method.name.value,
                                                                         prepare_argv_method.descriptor.value)
    create_method_direct(prepare_argv_method, prepare_argv_method_instructions(context))

    prepare_envp_method = create_method_prototype(context.cf, "prepare_envp", "()V")
    context.prepare_envp_method = context.cf.constants.create_method_ref(context.cf.this.name.value,
                                                                         prepare_envp_method.name.value,
                                                                         prepare_envp_method.descriptor.value)
    create_method_direct(prepare_envp_method, prepare_envp_method_instructions(context))

    syscall1_method = create_method_prototype(context.cf, "syscall1", "(JJ)J")
    context.syscall1_method = context.cf.constants.create_method_ref(context.cf.this.name.value,
                                                                     syscall1_method.name.value,
                                                                     syscall1_method.descriptor.value)
    create_method_direct(syscall1_method, syscall1_method_instructions(context))

    syscall3_method = create_method_prototype(context.cf, "syscall3", "(JJJJ)J")
    context.syscall3_method = context.cf.constants.create_method_ref(context.cf.this.name.value,
                                                                     syscall3_method.name.value,
                                                                     syscall3_method.descriptor.value)
    create_method_direct(syscall3_method, syscall3_method_instructions(context))

    clinit_method = create_method_prototype(context.cf, "<clinit>", "()V")
    create_method_direct(clinit_method, clinit_method_instructions(context))


def create_method_prototype(cf: ClassFile, name: str, descriptor: str):
    method = cf.methods.create(name, descriptor, code=True)
    method.access_flags.acc_public = False
    method.access_flags.acc_private = True
    method.access_flags.acc_static = True
    method.access_flags.acc_synthetic = True
    return method


def create_method(context: GenerateContext, method: Method, procedure: Optional[Proc], ops: list[Op]):
    # Variables:
    # 0: argument array

    instructions = Instructions(context)
    current_proc: Optional[OpAddr] = None

    local_variable_index = count_locals(method.descriptor.value, ()) - 1
    local_memory_var: Optional[int] = None

    if not procedure:  # We are in the main method
        instructions.load_reference(0)
        instructions.invoke_static(context.prepare_argv_method)
        instructions.invoke_static(context.prepare_envp_method)
        # print_memory(context, instructions)

    if procedure and procedure.local_memory_capacity != 0:
        local_memory_var = local_variable_index
        local_variable_index += 1
        instructions.push_integer(procedure.local_memory_capacity)
        instructions.invoke_static(context.extend_mem_method)
        instructions.convert_long_to_integer()
        instructions.store_integer(local_memory_var)

    for ip, op in enumerate(ops, 0 if not procedure else procedure.addr):
        # print(ip, op)
        current_label = Label(f"addr_{ip}")

        # Skip procedures inside the code
        if not procedure and current_proc and op.typ != OpType.RET:
            continue

        instructions.label(current_label)

        if op.typ in [OpType.PUSH_INT, OpType.PUSH_PTR]:
            assert isinstance(op.operand, int), f"This could be a bug in the parsing step {op.operand}"
            instructions.push_long(op.operand)
        elif op.typ == OpType.PUSH_BOOL:
            assert isinstance(op.operand, int), f"This could be a bug in the parsing step {op.operand}"
            instructions.push_long(op.operand)
        elif op.typ == OpType.PUSH_STR:
            assert isinstance(op.operand, str), "This could be a bug in the parsing step"

            string_constant = context.cf.constants.create_string(op.operand)

            instructions.push_constant(string_constant)
            # Stack: string
            instructions.duplicate_top_of_stack()
            # Stack: string, string
            instructions.string_get_bytes()
            # Stack: string, bytes
            instructions.array_length()
            # Stack: string, length
            instructions.convert_integer_to_long()
            # Stack: string, length (as long)
            instructions.move_long_behind_short()
            # Stack: length (as long), string

            instructions.invoke_static(context.put_string_method)
            # Stack: length (as long), pointer to string

            # print_memory(context, instructions)
        elif op.typ == OpType.PUSH_CSTR:
            assert isinstance(op.operand, str), "This could be a bug in the parsing step"
            string_constant = context.cf.constants.create_string(op.operand + "\0")

            instructions.push_constant(string_constant)
            instructions.invoke_static(context.put_string_method)

            # print_memory(context.cf, instructions)

        elif op.typ == OpType.PUSH_MEM:
            assert isinstance(op.operand, MemAddr), "This could be a bug in the parsing step"
            instructions.push_long(op.operand)
        elif op.typ == OpType.PUSH_LOCAL_MEM:
            assert isinstance(op.operand, MemAddr), "This could be a bug in the parsing step"
            assert procedure, "No local memory outside a procedure"
            assert local_memory_var is not None, "No local memory defined"

            instructions.load_integer(local_memory_var)
            instructions.push_integer(op.operand)
            instructions.add_integer()
            instructions.convert_integer_to_long()

        elif op.typ in [OpType.IF, OpType.IFSTAR]:
            assert isinstance(op.operand, OpAddr), f"This could be a bug in the parsing step {op.operand}"
            instructions.push_long(0)
            instructions.compare_long()
            instructions.branch_if_false(f"addr_{op.operand}")
        elif op.typ == OpType.WHILE:
            pass
        elif op.typ == OpType.ELSE:
            assert isinstance(op.operand, OpAddr), "This could be a bug in the parsing step"
            instructions.end_branch()
            instructions.branch(f"addr_{op.operand}")
            instructions.end_branch()
        elif op.typ == OpType.END:
            assert isinstance(op.operand, int), "This could be a bug in the parsing step"
            if ip + 1 != op.operand:
                instructions.end_branch()
                instructions.branch(f"addr_{op.operand}")
        elif op.typ == OpType.DO:
            assert isinstance(op.operand, int), "This could be a bug in the parsing step"
            instructions.push_long(0)
            instructions.compare_long()
            instructions.branch_if_false(f"addr_{op.operand}")
        elif op.typ == OpType.SKIP_PROC:
            assert isinstance(op.operand, OpAddr), f"This could be a bug in the parsing step: {op.operand}"
        elif op.typ == OpType.PREP_PROC:
            assert isinstance(op.operand, int)

            if procedure:
                for i in range(len(procedure.contract.ins)):
                    instructions.load_long(i * 2)

            current_proc = ip

        elif op.typ == OpType.CALL:
            assert isinstance(op.operand, OpAddr), f"This could be a bug in the parsing step: {op.operand}"

            proc = context.procedures[op.token.value]
            instructions.invoke_static(proc.method_ref)

            if len(proc.contract.outs) > 1:
                for i in range(len(proc.contract.outs) - 1, -1, -1):
                    instructions.duplicate_top_of_stack()
                    instructions.push_integer(i)
                    instructions.load_array_long()
                    instructions.move_long_behind_short()
                instructions.drop()

        elif op.typ == OpType.RET:
            assert isinstance(op.operand, int)

            current_proc = None
            if procedure:
                break

        elif op.typ == OpType.INTRINSIC:
            if op.operand == Intrinsic.PLUS:
                instructions.add_long()
            elif op.operand == Intrinsic.MINUS:
                instructions.subtract_long()
            elif op.operand == Intrinsic.MUL:
                instructions.multiply_long()
            elif op.operand == Intrinsic.MAX:
                instructions.invoke_static(context.cf.constants.create_method_ref("java/lang/Math", "max", "(JJ)J"))
            elif op.operand == Intrinsic.DIVMOD:
                # Stack: dividend, divisor
                instructions.duplicate_long_behind_long()
                # Stack: divisor, dividend, divisor
                instructions.swap_longs()
                # Stack: divisor, divisor, dividend
                instructions.duplicate_long_behind_long()
                # Stack: divisor, dividend, divisor, dividend
                instructions.swap_longs()
                # Stack: divisor, dividend, dividend, divisor
                instructions.divide_long()
                # Stack: divisor, dividend, dividend / divisor
                instructions.store_long(local_variable_index + 2)
                # Stack: divisor, dividend
                instructions.swap_longs()
                # Stack: dividend, divisor
                instructions.remainder_long()
                # Stack: dividend % divisor
                instructions.load_long(local_variable_index + 2)
                # Stack: dividend % divisor, dividend / divisor
                instructions.swap_longs()
                # Stack: dividend / divisor, dividend % divisor
            elif op.operand == Intrinsic.SHR:
                instructions.convert_long_to_integer()
                instructions.shift_right_long()
            elif op.operand == Intrinsic.SHL:
                instructions.convert_long_to_integer()
                instructions.shift_left_long()
            elif op.operand == Intrinsic.OR:
                instructions.or_long()
            elif op.operand == Intrinsic.AND:
                instructions.and_long()
            elif op.operand == Intrinsic.NOT:
                instructions.negate_long()
                instructions.push_long(1)
                instructions.subtract_long()
            elif op.operand == Intrinsic.PRINT:
                instructions.invoke_static(context.print_long_method)
            elif op.operand == Intrinsic.EQ:
                instructions.compare_long()
                instructions.branch_if_not_equal(f"ne_{ip}")
                instructions.push_long(1)
                instructions.branch(f"skip_{ip}")
                instructions.label(f"ne_{ip}")
                instructions.push_long(0)
                instructions.label(f"skip_{ip}")
            elif op.operand == Intrinsic.GT:
                instructions.compare_long()
                instructions.branch_if_less_or_equal(f"le_{ip}")
                instructions.push_long(1)
                instructions.branch(f"skip_{ip}")
                instructions.label(f"le_{ip}")
                instructions.push_long(0)
                instructions.label(f"skip_{ip}")
            elif op.operand == Intrinsic.LT:
                instructions.compare_long()
                instructions.branch_if_greater_or_equal(f"ge_{ip}")
                instructions.push_long(1)
                instructions.branch(f"skip_{ip}")
                instructions.label(f"ge_{ip}")
                instructions.push_long(0)
                instructions.label(f"skip_{ip}")
            elif op.operand == Intrinsic.GE:
                instructions.compare_long()
                instructions.branch_if_less(f"lt_{ip}")
                instructions.push_long(1)
                instructions.branch(f"skip_{ip}")
                instructions.label(f"lt_{ip}")
                instructions.push_long(0)
                instructions.label(f"skip_{ip}")
            elif op.operand == Intrinsic.LE:
                instructions.compare_long()
                instructions.branch_if_greater(f"gt_{ip}")
                instructions.push_long(1)
                instructions.branch(f"skip_{ip}")
                instructions.label(f"gt_{ip}")
                instructions.push_long(0)
                instructions.label(f"skip_{ip}")
            elif op.operand == Intrinsic.NE:
                instructions.compare_long()
                instructions.branch_if_equal(f"eq_{ip}")
                instructions.push_long(1)
                instructions.branch(f"skip_{ip}")
                instructions.label(f"eq_{ip}")
                instructions.push_long(0)
                instructions.label(f"skip_{ip}")
            elif op.operand == Intrinsic.DUP:
                instructions.duplicate_long()
            elif op.operand == Intrinsic.SWAP:
                instructions.swap_longs()
            elif op.operand == Intrinsic.DROP:
                instructions.drop_long()
            elif op.operand == Intrinsic.OVER:
                instructions.swap_longs()
                instructions.duplicate_long_behind_long()
            elif op.operand == Intrinsic.ROT:
                instructions.store_long(local_variable_index + 2)
                instructions.store_long(local_variable_index + 4)
                instructions.store_long(local_variable_index + 6)
                instructions.load_long(local_variable_index + 4)
                instructions.load_long(local_variable_index + 2)
                instructions.load_long(local_variable_index + 6)
            elif op.operand == Intrinsic.LOAD8:
                instructions.invoke_static(context.load_8_method)
            elif op.operand == Intrinsic.STORE8:
                store_8(context, instructions)
            elif op.operand == Intrinsic.LOAD16:
                instructions.invoke_static(context.load_16_method)
            elif op.operand == Intrinsic.STORE16:
                store_16(context, instructions)
            elif op.operand == Intrinsic.LOAD32:
                instructions.invoke_static(context.load_32_method)
            elif op.operand == Intrinsic.STORE32:
                store_32(context, instructions)
            elif op.operand == Intrinsic.LOAD64:
                instructions.invoke_static(context.load_64_method)
            elif op.operand == Intrinsic.STORE64:
                instructions.invoke_static(context.store_64_method)
            elif op.operand == Intrinsic.ARGC:
                instructions.get_static_field(context.argc_ref)
                instructions.invoke_static(context.load_64_method)
            elif op.operand == Intrinsic.ARGV:
                instructions.get_static_field(context.argv_ref)
                instructions.invoke_static(context.load_64_method)
            elif op.operand == Intrinsic.ENVP:
                instructions.get_static_field(context.envp_ref)
                pass
            elif op.operand == Intrinsic.HERE:
                value = ("%s:%d:%d" % op.token.loc)
                string_constant = context.cf.constants.create_string(value)

                instructions.push_constant(string_constant)
                # Stack: string
                instructions.duplicate_top_of_stack()
                # Stack: string, string
                instructions.string_get_bytes()
                # Stack: string, bytes
                instructions.array_length()
                # Stack: string, length
                instructions.convert_integer_to_long()
                # Stack: string, length (as long)
                instructions.move_long_behind_short()
                # Stack: length (as long), string

                instructions.invoke_static(context.put_string_method)
                # Stack: length (as long), pointer to string
            elif op.operand in [Intrinsic.CAST_PTR, Intrinsic.CAST_INT, Intrinsic.CAST_BOOL]:
                pass
            elif op.operand == Intrinsic.SYSCALL0:
                # raise NotImplementedError("SYSCALL0")
                instructions.drop_long()
                instructions.push_long(0)
                pass
            elif op.operand == Intrinsic.SYSCALL1:
                instructions.invoke_static(context.syscall1_method)
            elif op.operand == Intrinsic.SYSCALL2:
                instructions.drop_long()
                instructions.drop_long()
                instructions.drop_long()
                instructions.push_long(0)
                pass
            elif op.operand == Intrinsic.SYSCALL3:
                instructions.invoke_static(context.syscall3_method)
            elif op.operand == Intrinsic.SYSCALL4:
                instructions.drop_long()
                instructions.drop_long()
                instructions.drop_long()
                instructions.drop_long()
                instructions.drop_long()
                instructions.push_long(0)
                pass
            elif op.operand == Intrinsic.SYSCALL5:
                instructions.drop_long()
                instructions.drop_long()
                instructions.drop_long()
                instructions.drop_long()
                instructions.drop_long()
                instructions.drop_long()
                instructions.push_long(0)
                pass
            elif op.operand == Intrinsic.SYSCALL6:
                instructions.drop_long()
                instructions.drop_long()
                instructions.drop_long()
                instructions.drop_long()
                instructions.drop_long()
                instructions.drop_long()
                instructions.drop_long()
                instructions.push_long(0)
                pass
            elif op.operand == Intrinsic.STOP:
                pass
            else:
                raise NotImplementedError(op.operand)

    instructions.label(f"addr_{len(ops)}")

    if procedure and procedure.local_memory_capacity != 0:
        instructions.get_static_field(context.memory_ref)
        instructions.array_length()
        instructions.load_integer(local_memory_var)
        instructions.subtract_integer()
        instructions.invoke_static(context.extend_mem_method)
        instructions.drop_long()

    if procedure:
        if len(procedure.contract.outs) == 0:
            instructions.return_void()
        elif len(procedure.contract.outs) == 1:
            instructions.return_long()
        else:
            instructions.push_integer(len(procedure.contract.outs))
            instructions.new_array(OperandType.Long.array_type)

            for i in range(len(procedure.contract.outs)):
                instructions.duplicate_short_behind_long()
                instructions.push_integer(i)
                instructions.move_top_2_behind_long()
                instructions.store_array_long()

            instructions.return_reference()

    else:
        instructions.return_void()

    return create_method_direct(method, instructions)


def create_method_direct(method: Method,
                         instructions: Instructions):
    assembly = instructions.assemble()
    method.code.assemble(assembly)
    input_variable_count = sum(map(lambda op: op.size, get_method_input_types(method)))
    method.code.max_locals = max(input_variable_count, instructions.stack.local_count)
    method.code.max_stack = instructions.stack.max_stack_size


def make_signature(contract):
    if len(contract.outs) == 0:
        return "(" + "J" * len(contract.ins) + ")" + "V"
    elif len(contract.outs) == 1:
        return "(" + "J" * len(contract.ins) + ")" + "J"
    else:
        return "(" + "J" * len(contract.ins) + ")" + "[J"


def scan_called_procedures(
        context: ParseContext,
) -> List[str]:
    procedures_by_addr: Dict[OpAddr, str] = dict(map(lambda item: (item[1].addr, item[0]), context.procs.items()))
    called_procedures: OrderedDict[str, Set[str]] = OrderedDict()
    current_proc: Optional[str] = None

    for ip, op in enumerate(context.ops):
        if op.typ == OpType.SKIP_PROC:
            current_proc = procedures_by_addr[ip + 1]
            assert current_proc is not None
            called_procedures[current_proc] = set()
        elif op.typ == OpType.RET:
            current_proc = None
        elif op.typ == OpType.CALL:
            called_procedures[op.token.value].add(current_proc)

    while any(len(called_procedures[proc]) == 0 for proc in called_procedures):
        for proc in list(called_procedures.keys()):
            if len(called_procedures[proc]) == 0:
                for called_proc in called_procedures:
                    call_sites = called_procedures[called_proc]
                    if proc in call_sites:
                        call_sites.remove(proc)
                called_procedures.pop(proc)

    return list(called_procedures.keys())
