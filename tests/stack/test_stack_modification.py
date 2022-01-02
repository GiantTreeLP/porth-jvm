from jawa.assemble import Label
from jawa.attributes.bootstrap import BootstrapMethod, BootstrapMethodsAttribute
from jawa.constants import MethodHandleKind

from extensions.DeduplicatingClassFile import DeduplicatingClassFile
from jvm.intrinsics import OperandType
from jvm.intrinsics.stack import Stack

cf = DeduplicatingClassFile.create("Test")
cf.attributes.create(BootstrapMethodsAttribute)


def test_aaload():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("anewarray", cf.constants.create_class("java/lang/String"), 1)
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[0] == OperandType.Reference
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("aaload")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference


def test_aastore():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("anewarray", cf.constants.create_class("java/lang/String"), 1)
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[0] == OperandType.Reference
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("ldc", cf.constants.create_string("Hello, World!"))
    assert len(stack._stack) == 3
    assert stack._stack[0] == OperandType.Reference
    assert stack._stack[1] == OperandType.Integer
    assert stack._stack[2] == OperandType.Reference
    stack.update_stack("aastore")
    assert len(stack._stack) == 0


def test_aconst_null():
    stack = Stack()
    stack.update_stack("aconst_null")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference


def test_aload():
    stack = Stack()
    stack.update_stack("aload")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference

    stack = Stack()
    stack.update_stack("aload_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference

    stack = Stack()
    stack.update_stack("aload_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference

    stack = Stack()
    stack.update_stack("aload_2")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference

    stack = Stack()
    stack.update_stack("aload_3")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference


def test_anewarray():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("anewarray", cf.constants.create_class("java/lang/String"), 1)
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference


def test_areturn():
    stack = Stack()
    stack.update_stack("aconst_null")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("areturn")
    assert len(stack._stack) == 0


def test_arraylength():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("anewarray", cf.constants.create_class("java/lang/String"), 1)
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("arraylength")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer


def test_astore():
    stack = Stack()
    stack.update_stack("aconst_null")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("astore")
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("aconst_null")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("astore_0")
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("aconst_null")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("astore_1")
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("aconst_null")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("astore_2")
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("aconst_null")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("astore_3")
    assert len(stack._stack) == 0


def test_athrow():
    stack = Stack()
    stack.update_stack("aconst_null")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("athrow")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference


def test_baload():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("newarray", OperandType.Byte.array_type)
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("baload")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Byte


def test_bastore():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("newarray", OperandType.Byte.array_type)
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 3
    assert stack._stack[2] == OperandType.Integer
    stack.update_stack("bastore")
    assert len(stack._stack) == 0


def test_bipush():
    stack = Stack()
    stack.update_stack("bipush", 1)
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer


def test_caload():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("newarray", OperandType.Char.array_type)
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("caload")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Char


def test_castore():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("newarray", OperandType.Char.array_type)
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 3
    assert stack._stack[2] == OperandType.Integer
    stack.update_stack("castore")
    assert len(stack._stack) == 0


def test_checkcast():
    stack = Stack()
    stack.update_stack("aconst_null")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("checkcast", cf.constants.create_class("java/lang/String"))
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference


def test_d2f():
    stack = Stack()
    stack.update_stack("dconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double
    stack.update_stack("d2f")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float


def test_d2i():
    stack = Stack()
    stack.update_stack("dconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double
    stack.update_stack("d2i")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer


def test_d2l():
    stack = Stack()
    stack.update_stack("dconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double
    stack.update_stack("d2l")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long


def test_dadd():
    stack = Stack()
    stack.update_stack("dconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double
    stack.update_stack("dconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Double
    stack.update_stack("dadd")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double


def test_daload():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("newarray", OperandType.Double.array_type)
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("daload")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double


def test_dastore():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("newarray", OperandType.Double.array_type)
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("dconst_0")
    assert len(stack._stack) == 3
    assert stack._stack[2] == OperandType.Double
    stack.update_stack("dastore")
    assert len(stack._stack) == 0


def test_dcmpg():
    stack = Stack()
    stack.update_stack("dconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double
    stack.update_stack("dconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Double
    stack.update_stack("dcmpg")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer


def test_dcmpl():
    stack = Stack()
    stack.update_stack("dconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double
    stack.update_stack("dconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Double
    stack.update_stack("dcmpl")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer


def test_dconst():
    stack = Stack()
    stack.update_stack("dconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double

    stack = Stack()
    stack.update_stack("dconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double


def test_ddiv():
    stack = Stack()
    stack.update_stack("dconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double
    stack.update_stack("dconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Double
    stack.update_stack("ddiv")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double


def test_dload():
    stack = Stack()
    stack.update_stack("dload", 0)
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double

    stack = Stack()
    stack.update_stack("dload_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double

    stack = Stack()
    stack.update_stack("dload_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double

    stack = Stack()
    stack.update_stack("dload_2")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double

    stack = Stack()
    stack.update_stack("dload_3")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double


def test_dmul():
    stack = Stack()
    stack.update_stack("dconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double
    stack.update_stack("dconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Double
    stack.update_stack("dmul")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double


def test_dneg():
    stack = Stack()
    stack.update_stack("dconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double
    stack.update_stack("dneg")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double


def test_drem():
    stack = Stack()
    stack.update_stack("dconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double
    stack.update_stack("dconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Double
    stack.update_stack("drem")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double


def test_dreturn():
    stack = Stack()
    stack.update_stack("dconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double
    stack.update_stack("dreturn")
    assert len(stack._stack) == 0


def test_dstore():
    stack = Stack()
    stack.update_stack("dconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double
    stack.update_stack("dstore", 0)
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("dconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double
    stack.update_stack("dstore_0")
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("dconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double
    stack.update_stack("dstore_1")
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("dconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double
    stack.update_stack("dstore_2")
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("dconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double
    stack.update_stack("dstore_3")
    assert len(stack._stack) == 0


def test_dsub():
    stack = Stack()
    stack.update_stack("dconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double
    stack.update_stack("dconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Double
    stack.update_stack("dsub")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double


def test_dup():
    stack = Stack()
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("dup")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer


def test_dup_x1():
    stack = Stack()
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("dup_x1")
    assert len(stack._stack) == 3
    assert stack._stack[0] == OperandType.Integer
    assert stack._stack[1] == OperandType.Integer
    assert stack._stack[2] == OperandType.Integer


def test_dup_x2():
    stack = Stack()
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("iconst_2")
    assert len(stack._stack) == 3
    assert stack._stack[2] == OperandType.Integer
    stack.update_stack("dup_x2")
    assert len(stack._stack) == 4
    assert stack._stack[0] == OperandType.Integer
    assert stack._stack[1] == OperandType.Integer
    assert stack._stack[2] == OperandType.Integer
    assert stack._stack[3] == OperandType.Integer

    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("dup_x2")
    assert len(stack._stack) == 3
    assert stack._stack[0] == OperandType.Integer
    assert stack._stack[1] == OperandType.Long
    assert stack._stack[2] == OperandType.Integer


def test_dup2():
    stack = Stack()
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("dup2")
    assert len(stack._stack) == 4
    assert stack._stack[0] == OperandType.Integer
    assert stack._stack[1] == OperandType.Integer
    assert stack._stack[2] == OperandType.Integer
    assert stack._stack[3] == OperandType.Integer

    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long
    stack.update_stack("dup2")
    assert len(stack._stack) == 2
    assert stack._stack[0] == OperandType.Long
    assert stack._stack[1] == OperandType.Long


def test_dup2_x1():
    stack = Stack()
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("iconst_2")
    assert len(stack._stack) == 3
    assert stack._stack[2] == OperandType.Integer
    stack.update_stack("dup2_x1")
    assert len(stack._stack) == 5
    assert stack._stack[0] == OperandType.Integer
    assert stack._stack[1] == OperandType.Integer
    assert stack._stack[2] == OperandType.Integer
    assert stack._stack[3] == OperandType.Integer
    assert stack._stack[4] == OperandType.Integer

    stack = Stack()
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("lconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Long
    stack.update_stack("dup2_x1")
    assert len(stack._stack) == 3
    assert stack._stack[0] == OperandType.Long
    assert stack._stack[1] == OperandType.Integer
    assert stack._stack[2] == OperandType.Long


def test_dup2_x2():
    stack = Stack()
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("iconst_2")
    assert len(stack._stack) == 3
    assert stack._stack[2] == OperandType.Integer
    stack.update_stack("iconst_3")
    assert len(stack._stack) == 4
    assert stack._stack[3] == OperandType.Integer
    stack.update_stack("dup2_x2")
    assert len(stack._stack) == 6
    assert stack._stack[0] == OperandType.Integer
    assert stack._stack[1] == OperandType.Integer
    assert stack._stack[2] == OperandType.Integer
    assert stack._stack[3] == OperandType.Integer
    assert stack._stack[4] == OperandType.Integer
    assert stack._stack[5] == OperandType.Integer

    stack = Stack()
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("lconst_1")
    assert len(stack._stack) == 3
    assert stack._stack[2] == OperandType.Long
    stack.update_stack("dup2_x2")
    assert len(stack._stack) == 4
    assert stack._stack[0] == OperandType.Long
    assert stack._stack[1] == OperandType.Integer
    assert stack._stack[2] == OperandType.Integer
    assert stack._stack[3] == OperandType.Long

    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("iconst_2")
    assert len(stack._stack) == 3
    assert stack._stack[2] == OperandType.Integer
    stack.update_stack("dup2_x2")
    assert len(stack._stack) == 5
    assert stack._stack[0] == OperandType.Integer
    assert stack._stack[1] == OperandType.Integer
    assert stack._stack[2] == OperandType.Long
    assert stack._stack[3] == OperandType.Integer
    assert stack._stack[4] == OperandType.Integer

    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long
    stack.update_stack("lconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Long
    stack.update_stack("dup2_x2")
    assert len(stack._stack) == 3
    assert stack._stack[0] == OperandType.Long
    assert stack._stack[1] == OperandType.Long
    assert stack._stack[2] == OperandType.Long


def test_f2d():
    stack = Stack()
    stack.update_stack("fconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float
    stack.update_stack("f2d")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double


def test_f2i():
    stack = Stack()
    stack.update_stack("fconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float
    stack.update_stack("f2i")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer


def test_f2l():
    stack = Stack()
    stack.update_stack("fconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float
    stack.update_stack("f2l")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long


def test_fadd():
    stack = Stack()
    stack.update_stack("fconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float
    stack.update_stack("fconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Float
    stack.update_stack("fadd")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float


def test_faload():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("newarray", OperandType.Float.array_type)
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("faload")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float


def test_fastore():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("newarray", OperandType.Float.array_type)
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("fconst_0")
    assert len(stack._stack) == 3
    assert stack._stack[2] == OperandType.Float
    stack.update_stack("fastore")
    assert len(stack._stack) == 0


def test_fcmpg():
    stack = Stack()
    stack.update_stack("fconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float
    stack.update_stack("fconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Float
    stack.update_stack("fcmpg")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer


def test_fcmpl():
    stack = Stack()
    stack.update_stack("fconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float
    stack.update_stack("fconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Float
    stack.update_stack("fcmpl")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer


def test_fconst():
    stack = Stack()
    stack.update_stack("fconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float
    stack.update_stack("fconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Float
    stack.update_stack("fconst_2")
    assert len(stack._stack) == 3
    assert stack._stack[2] == OperandType.Float


def test_fdiv():
    stack = Stack()
    stack.update_stack("fconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float
    stack.update_stack("fconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Float
    stack.update_stack("fdiv")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float


def test_fload():
    stack = Stack()
    stack.update_stack("fload_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float
    stack.update_stack("fload_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Float
    stack.update_stack("fload_2")
    assert len(stack._stack) == 3
    assert stack._stack[2] == OperandType.Float
    stack.update_stack("fload_3")
    assert len(stack._stack) == 4
    assert stack._stack[3] == OperandType.Float


def test_fmul():
    stack = Stack()
    stack.update_stack("fconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float
    stack.update_stack("fconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Float
    stack.update_stack("fmul")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float


def test_fneg():
    stack = Stack()
    stack.update_stack("fconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float
    stack.update_stack("fneg")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float


def test_frem():
    stack = Stack()
    stack.update_stack("fconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float
    stack.update_stack("fconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Float
    stack.update_stack("frem")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float


def test_freturn():
    stack = Stack()
    stack.update_stack("fconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float
    stack.update_stack("freturn")
    assert len(stack._stack) == 0


def test_fstore():
    stack = Stack()
    stack.update_stack("fconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float
    stack.update_stack("fstore_0")
    assert len(stack._stack) == 0
    stack.update_stack("fconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float
    stack.update_stack("fstore_1")
    assert len(stack._stack) == 0
    stack.update_stack("fconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float
    stack.update_stack("fstore_2")
    assert len(stack._stack) == 0
    stack.update_stack("fconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float
    stack.update_stack("fstore_3")
    assert len(stack._stack) == 0


def test_fsub():
    stack = Stack()
    stack.update_stack("fconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float
    stack.update_stack("fconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Float
    stack.update_stack("fsub")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float


def test_getfield():
    stack = Stack()
    stack.update_stack("new", cf.constants.create_class("java/lang/String"))
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("getfield", cf.constants.create_field_ref("java/lang/System", "out", "Ljava/io/PrintStream;"))
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference


def test_getstatic():
    stack = Stack()
    stack.update_stack("getstatic", cf.constants.create_field_ref("java/lang/System", "out", "Ljava/io/PrintStream;"))
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference


def test_goto():
    stack = Stack()
    stack.update_stack("goto", Label("label"))
    assert len(stack._stack) == 0


def test_goto_w():
    stack = Stack()
    stack.update_stack("goto_w", Label("label"))
    assert len(stack._stack) == 0


def test_i2b():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("i2b")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Byte


def test_i2c():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("i2c")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Char


def test_i2d():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("i2d")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double


def test_i2f():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("i2f")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float


def test_i2l():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("i2l")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long


def test_i2s():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("i2s")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Short


def test_iadd():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("iadd")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer


def test_iaload():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("newarray", OperandType.Integer.array_type)
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("iaload")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer


def test_iand():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("iand")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer


def test_iastore():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("newarray", OperandType.Integer.array_type)
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 3
    assert stack._stack[2] == OperandType.Integer
    stack.update_stack("iastore")
    assert len(stack._stack) == 0


def test_iconst():
    stack = Stack()
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer

    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer

    stack = Stack()
    stack.update_stack("iconst_2")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer

    stack = Stack()
    stack.update_stack("iconst_3")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer

    stack = Stack()
    stack.update_stack("iconst_4")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer

    stack = Stack()
    stack.update_stack("iconst_5")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer


def test_idiv():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("idiv")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer


def test_if_acmp():
    stack = Stack()
    stack.update_stack("aconst_null")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("aconst_null")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Reference
    stack.update_stack("if_acmpeq")
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("aconst_null")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("aconst_null")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Reference
    stack.update_stack("if_acmpne")
    assert len(stack._stack) == 0


def test_if_icmp():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("if_icmpeq")
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("if_icmpne")
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("if_icmplt")
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("if_icmpge")
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("if_icmpgt")
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("if_icmple")
    assert len(stack._stack) == 0


def test_if():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("ifne")
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("ifeq")
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("iflt")
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("ifge")
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("ifgt")
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("ifle")
    assert len(stack._stack) == 0


def test_ifnonnull():
    stack = Stack()
    stack.update_stack("aconst_null")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("ifnonnull")
    assert len(stack._stack) == 0


def test_ifnull():
    stack = Stack()
    stack.update_stack("aconst_null")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("ifnull")
    assert len(stack._stack) == 0


def test_iinc():
    stack = Stack()
    stack.update_stack("iinc", 0, 0)
    assert len(stack._stack) == 0


def test_iload():
    stack = Stack()
    stack.update_stack("iload", 0)
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer

    stack = Stack()
    stack.update_stack("iload_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer

    stack = Stack()
    stack.update_stack("iload_2")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer

    stack = Stack()
    stack.update_stack("iload_3")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer


def test_imul():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("imul")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer


def test_ineg():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("ineg")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer


def test_instanceof():
    stack = Stack()
    stack.update_stack("aconst_null")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("instanceof", cf.constants.create_class("java/lang/String"))
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Boolean


def test_invokedynamic():
    method_handle = cf.constants.create_method_handle(
        MethodHandleKind.INVOKE_STATIC,
        "java/lang/invoke/StringConcatFactory",
        "makeConcatWithConstants",
        "(Ljava/lang/invoke/MethodHandles$Lookup;"
        "Ljava/lang/String;Ljava/lang/invoke/MethodType;Ljava/lang/String;[Ljava/lang/Object;)"
        "Ljava/lang/invoke/CallSite;"
    )

    cf.bootstrap_methods.append(
        BootstrapMethod(method_handle.index, (cf.constants.create_string("\1=\1\0").index,)))

    make_concat_with_constants = cf.constants.create_invoke_dynamic(
        len(cf.bootstrap_methods) - 1,
        "makeConcatWithConstants",
        "(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"
    )

    stack = Stack()
    stack.update_stack("aconst_null")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("aconst_null")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Reference
    stack.update_stack("invokedynamic", make_concat_with_constants, 0, 0)
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference


def test_invokeinterface():
    stack = Stack()
    stack.update_stack("aconst_null")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("invokeinterface", cf.constants.create_method_ref(
        "java/lang/CharSequence",
        "length",
        "()I"
    ), 0)
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer


def test_invokespecial():
    stack = Stack()
    stack.update_stack("aconst_null")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("invokespecial", cf.constants.create_method_ref(
        "java/lang/Object",
        "<init>",
        "()V"
    ))
    assert len(stack._stack) == 0


def test_invokestatic():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("invokestatic", cf.constants.create_method_ref(
        "java/lang/System",
        "exit",
        "(I)V"
    ))
    assert len(stack._stack) == 0


def test_invokevirtual():
    stack = Stack()
    stack.update_stack("aconst_null")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("invokevirtual", cf.constants.create_method_ref(
        "java/lang/Object",
        "toString",
        "()Ljava/lang/String;"
    ))
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference


def test_ior():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("ior")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer


def test_irem():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("irem")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer


def test_ireturn():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("ireturn")
    assert len(stack._stack) == 0


def test_ishl():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("ishl")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer


def test_ishr():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("ishr")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer


def test_istore():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("istore", 0)
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("istore_0")
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("istore_1")
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("istore_2")
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("istore_3")


def test_isub():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("isub")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer


def test_iushr():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("iushr")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer


def test_ixor():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("ixor")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer


def test_jsr():
    stack = Stack()
    stack.update_stack("jsr")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference


def test_jsr_w():
    stack = Stack()
    stack.update_stack("jsr_w")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference


def test_l2d():
    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long
    stack.update_stack("l2d")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double


def test_l2f():
    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long
    stack.update_stack("l2f")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float


def test_l2i():
    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long
    stack.update_stack("l2i")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer


def test_ladd():
    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Long
    stack.update_stack("ladd")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long


def test_laload():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("newarray", OperandType.Long.array_type)
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("laload")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long


def test_land():
    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Long
    stack.update_stack("land")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long


def test_lastore():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("newarray", OperandType.Long.array_type)
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 3
    assert stack._stack[2] == OperandType.Long
    stack.update_stack("lastore")
    assert len(stack._stack) == 0


def test_lcmp():
    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Long
    stack.update_stack("lcmp")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer


def test_lconst():
    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long

    stack = Stack()
    stack.update_stack("lconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long


def test_ldc():
    stack = Stack()
    stack.update_stack("ldc", cf.constants.create_integer(1))
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer

    stack = Stack()
    stack.update_stack("ldc", cf.constants.create_float(1.0))
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Float

    stack = Stack()
    stack.update_stack("ldc", cf.constants.create_string("test"))
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference

    stack = Stack()
    stack.update_stack("ldc", cf.constants.create_class("java/lang/String"))
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference


def test_ldc2_w():
    stack = Stack()
    stack.update_stack("ldc2_w", cf.constants.create_long(1))
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long

    stack = Stack()
    stack.update_stack("ldc2_w", cf.constants.create_double(1.0))
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Double


def test_ldiv():
    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Long
    stack.update_stack("ldiv")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long


def test_lload():
    stack = Stack()
    stack.update_stack("lload", 0)
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long

    stack = Stack()
    stack.update_stack("lload_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long

    stack = Stack()
    stack.update_stack("lload_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long

    stack = Stack()
    stack.update_stack("lload_2")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long

    stack = Stack()
    stack.update_stack("lload_3")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long


def test_lmul():
    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Long
    stack.update_stack("lmul")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long


def test_lneg():
    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long
    stack.update_stack("lneg")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long


def test_lookupswitch():
    stack = Stack()
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("lookupswitch")
    assert len(stack._stack) == 0


def test_lor():
    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Long
    stack.update_stack("lor")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long


def test_lrem():
    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Long
    stack.update_stack("lrem")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long


def test_lreturn():
    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long
    stack.update_stack("lreturn")
    assert len(stack._stack) == 0


def test_lshl():
    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("lshl")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long


def test_lshr():
    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("lshr")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long


def test_lstore():
    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long
    stack.update_stack("lstore", 0)
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long
    stack.update_stack("lstore_0")
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long
    stack.update_stack("lstore_1")
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long
    stack.update_stack("lstore_2")
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long
    stack.update_stack("lstore_3")
    assert len(stack._stack) == 0


def test_lsub():
    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Long
    stack.update_stack("lsub")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long


def test_lushr():
    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("lushr")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long


def test_lxor():
    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Long
    stack.update_stack("lxor")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long


def test_monitorenter():
    stack = Stack()
    stack.update_stack("aconst_null")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("monitorenter")
    assert len(stack._stack) == 0


def test_monitorexit():
    stack = Stack()
    stack.update_stack("aconst_null")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("monitorexit")
    assert len(stack._stack) == 0


def test_multianewarray():
    stack = Stack()
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("multianewarray", cf.constants.create_class("java/lang/String"), 1)
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference


def test_new():
    stack = Stack()
    stack.update_stack("new", cf.constants.create_class("java/lang/String"))
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference


def test_newarray():
    stack = Stack()
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("newarray", OperandType.Integer.array_type)
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference


def test_nop():
    stack = Stack()
    stack.update_stack("nop")
    assert len(stack._stack) == 0


def test_pop():
    stack = Stack()
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("pop")
    assert len(stack._stack) == 0


def test_pop2():
    stack = Stack()
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("pop2")
    assert len(stack._stack) == 0

    stack = Stack()
    stack.update_stack("lconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Long
    stack.update_stack("pop2")
    assert len(stack._stack) == 0


def test_putfield():
    stack = Stack()
    stack.update_stack("aconst_null")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("putfield", cf.constants.create_field_ref("java/lang/String", "value", "I"))
    assert len(stack._stack) == 0


def test_putstatic():
    stack = Stack()
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("putstatic", cf.constants.create_field_ref("java/lang/String", "value", "I"))
    assert len(stack._stack) == 0


def test_ret():
    stack = Stack()
    stack.update_stack("ret")
    assert len(stack._stack) == 0


def test_return():
    stack = Stack()
    stack.update_stack("return")
    assert len(stack._stack) == 0


def test_saload():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("newarray", OperandType.Short.array_type)
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("saload")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Short


def test_sastore():
    stack = Stack()
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("newarray", OperandType.Short.array_type)
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Reference
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 3
    assert stack._stack[2] == OperandType.Integer
    stack.update_stack("sastore")
    assert len(stack._stack) == 0


def test_sipush():
    stack = Stack()
    stack.update_stack("sipush", 1)
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer


def test_swap():
    stack = Stack()
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("iconst_1")
    assert len(stack._stack) == 2
    assert stack._stack[1] == OperandType.Integer
    stack.update_stack("swap")
    assert len(stack._stack) == 2
    assert stack._stack[0] == OperandType.Integer
    assert stack._stack[1] == OperandType.Integer


def test_tableswitch():
    stack = Stack()
    stack.update_stack("iconst_0")
    assert len(stack._stack) == 1
    assert stack._stack[0] == OperandType.Integer
    stack.update_stack("tableswitch", 0, 0, 0, 0)
    assert len(stack._stack) == 0
