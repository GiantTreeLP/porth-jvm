from typing import Callable, Tuple, Any, Union

from jawa.constants import ConstantPool, InterfaceMethodRef, MethodReference, FieldReference, NameAndType, String, \
    ConstantClass, Double, Long, Float, Integer, _constant_types, Constant, UTF8


class DeduplicatingConstantPool(ConstantPool):

    @staticmethod
    def _equals(other: Constant) -> Callable[[Constant], bool]:
        def test(constant: Constant) -> bool:
            if hasattr(constant, "pack") and hasattr(other, "pack"):
                return constant.pack() == other.pack()
            else:
                return False

        return test

    def append(self, constant: Union[None, Tuple[Any, ...]]):
        found = None
        inserted = False
        if constant is not None:
            found = self.find_one(self.get_constant_type(constant),
                                  self._equals(self.create_constant(constant)))
        if found is None:
            self._pool.append(constant)
            inserted = True
            if constant:
                found = self.get(self.raw_count - 1)
        # else:
        # print("In constant pool")

        return found, inserted

    def create_constant(self, constant):
        return self.get_constant_type(constant)(self._pool, 0, *constant[1:])

    @staticmethod
    def get_constant_type(constant):
        return _constant_types[constant[0]]

    def create_utf8(self, value) -> UTF8:
        return self.append((1, value))[0]

    def create_integer(self, value: int) -> Integer:
        return self.append((3, value))[0]

    def create_float(self, value: float) -> Float:
        return self.append((4, value))[0]

    def create_long(self, value: int) -> Long:
        ret, ins = self.append((5, value))
        if ins:
            self.append(None)
        return ret

    def create_double(self, value: float) -> Double:
        ret, ins = self.append((6, value))
        if ins:
            self.append(None)
        return ret

    def create_class(self, name: str) -> ConstantClass:
        return self.append((
            7,
            self.create_utf8(name).index
        ))[0]

    def create_string(self, value: str) -> String:
        return self.append((
            8,
            self.create_utf8(value).index
        ))[0]

    def create_name_and_type(self, name: str, descriptor: str) -> NameAndType:
        return self.append((
            12,
            self.create_utf8(name).index,
            self.create_utf8(descriptor).index
        ))[0]

    def create_field_ref(self, class_: str, field: str, descriptor: str) -> FieldReference:
        return self.append((
            9,
            self.create_class(class_).index,
            self.create_name_and_type(field, descriptor).index
        ))[0]

    def create_method_ref(self, class_: str, method: str, descriptor: str) -> MethodReference:
        return self.append((
            10,
            self.create_class(class_).index,
            self.create_name_and_type(method, descriptor).index
        ))[0]

    def create_interface_method_ref(self, class_: str, if_method: str, descriptor: str) -> InterfaceMethodRef:
        return self.append((
            11,
            self.create_class(class_).index,
            self.create_name_and_type(if_method, descriptor).index
        ))[0]
