from dataclasses import dataclass

from jawa.cf import ClassFile
from jawa.constants import MethodReference, FieldReference

from jvm.intrinsics.procedures import Procedure
from porth.porth import Program


@dataclass(init=False)
class GenerateContext:
    program: Program
    program_name: str
    procedures: dict[str, Procedure]

    cf: ClassFile

    clinit_method: MethodReference
    print_long_method: MethodReference
    prepare_argv_method: MethodReference
    prepare_envp_method: MethodReference
    syscall3_method: MethodReference
    extend_mem_method: MethodReference
    store_64_method: MethodReference
    load_64_method: MethodReference
    load_32_method: MethodReference
    load_16_method: MethodReference
    load_8_method: MethodReference
    put_string_method: MethodReference

    memory_ref: FieldReference
    argc_ref: FieldReference
    argv_ref: FieldReference
    envp_ref: FieldReference
    fd_ref: FieldReference
