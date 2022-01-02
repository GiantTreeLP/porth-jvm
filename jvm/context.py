from dataclasses import dataclass
from typing import Dict, OrderedDict, Tuple

from jawa.constants import MethodReference, FieldReference

from extensions.DeduplicatingClassFile import DeduplicatingClassFile
from jvm.intrinsics.procedures import Procedure
from porth.porth import Program


@dataclass(init=False)
class GenerateContext:
    program: Program
    program_name: str
    procedures: Dict[str, Procedure]
    strings: OrderedDict[str, int]

    cf: DeduplicatingClassFile

    print_long_method: MethodReference
    prepare_argv_method: MethodReference
    prepare_envp_method: MethodReference
    syscall1_method: MethodReference
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

    def get_string(self, string: str) -> int:
        if string not in self.strings:
            if len(self.strings) > 0:
                # noinspection PyTypeChecker
                last_string: Tuple[str, int] = next(reversed(self.strings.items()))

                self.strings[string] = last_string[1] + len(last_string[0].encode("utf-8"))
            else:
                self.strings[string] = 0

        return self.strings[string]

    def get_strings_size(self) -> int:
        # noinspection PyTypeChecker
        last_string: Tuple[str, int] = next(reversed(self.strings.items()))
        size = last_string[1] + len(last_string[0].encode("utf-8"))
        assert size == sum(len(s.encode("utf-8")) for s in self.strings)
        return size
