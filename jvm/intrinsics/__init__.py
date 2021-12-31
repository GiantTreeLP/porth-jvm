from enum import Enum
from typing import TypeAlias, Union, Dict, Tuple, List

# Types
from jawa.assemble import Label
from jawa.constants import Constant, MethodReference, InvokeDynamic, FieldReference, InterfaceMethodRef, Reference
from jawa.methods import Method

Instruction: TypeAlias = Union[Label, str]
Operand: TypeAlias = Union[Label, Constant, int, Dict[int, Label]]
InstructionsType: TypeAlias = Union[Label,
                                    Tuple[Instruction],
                                    Tuple[Instruction, Operand],
                                    Tuple[Instruction, Operand, Operand]]
LabelType: TypeAlias = Union[str, Label]


class OperandType(Enum):
    Reference = (1, -1)
    Integer = (1, 10)
    Float = (1, 6)
    Byte = (1, 8)
    Short = (1, 9)
    Char = (1, 5)
    Boolean = (1, 4)
    Long = (2, 11)
    Double = (2, 7)

    def __init__(self, size: int, array_type: int):
        self.size = size
        self.array_type = array_type


INTEGER_TYPES = (
    OperandType.Integer,
    OperandType.Boolean,
    OperandType.Byte,
    OperandType.Short,
    OperandType.Char
)

MNEMONIC_TO_TYPE = {
    'I': OperandType.Integer,
    'J': OperandType.Long,
    'F': OperandType.Float,
    'D': OperandType.Double,
    'B': OperandType.Byte,
    'S': OperandType.Short,
    'C': OperandType.Char,
    'Z': OperandType.Boolean,
    '[': OperandType.Reference,
    'L': OperandType.Reference,
    'V': None,
}


def get_field_type(field_reference: FieldReference) -> List[OperandType]:
    return_type = field_reference.name_and_type.descriptor.value[0]
    if return_type in MNEMONIC_TO_TYPE:
        return [MNEMONIC_TO_TYPE[return_type]]
    else:
        return []


def get_method_return_type(method_reference: Union[MethodReference, InvokeDynamic, InterfaceMethodRef]) \
        -> List[OperandType]:
    return_type = method_reference.name_and_type.descriptor.value.rsplit(")", 1)[-1][0]

    if return_type in MNEMONIC_TO_TYPE:
        return [MNEMONIC_TO_TYPE[return_type]]
    else:
        raise ValueError(f"Unknown return type: {return_type}")


def get_method_input_types(method_reference: Union[Method, MethodReference, InterfaceMethodRef, InvokeDynamic]) \
        -> List[OperandType]:
    if isinstance(method_reference, Method):
        descriptor = method_reference.descriptor.value
    elif isinstance(method_reference, (Reference, InvokeDynamic)):
        descriptor = method_reference.name_and_type.descriptor.value
    else:
        raise ValueError(f"Unknown method reference type: {type(method_reference)}")

    types = []

    i = 0

    while i < len(descriptor):
        if descriptor[i] == '(':
            i += 1
            continue
        elif descriptor[i] == ')':
            break
        elif descriptor[i] == 'L':
            types.append(OperandType.Reference)
            while descriptor[i] != ';':
                i += 1
        elif descriptor[i] == '[':
            types.append(OperandType.Reference)
            i += 1
            if descriptor[i] == 'L':
                while descriptor[i] != ';':
                    i += 1
                i += 1
            else:
                i += 1
            continue
        else:
            if descriptor[i] in MNEMONIC_TO_TYPE:
                types.append(MNEMONIC_TO_TYPE[descriptor[i]])
            else:
                raise Exception(f'Unknown type {descriptor[i]}')
        i += 1

    return types
