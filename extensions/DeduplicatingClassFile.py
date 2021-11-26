from typing import IO

from jawa.cf import ClassFile, ClassVersion

from extensions.DeduplicatingConstantPool import DeduplicatingConstantPool


class DeduplicatingClassFile(ClassFile):
    def __init__(self, source: IO = None):
        super().__init__(source)
        self._version = ClassVersion(51, 3)
        self._constants = DeduplicatingConstantPool()

    @classmethod
    def create(cls, this: str, super_: str = u'java/lang/Object') -> 'ClassFile':
        cf = DeduplicatingClassFile()
        cf.access_flags.acc_public = True
        cf.access_flags.acc_super = True

        cf.this = cf.constants.create_class(this)
        cf.super_ = cf.constants.create_class(super_)

        return cf


