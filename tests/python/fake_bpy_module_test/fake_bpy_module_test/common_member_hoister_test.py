"""Tests for the CommonMemberHoister transformer.

Tests build documents programmatically to mirror the node structure
that exists at the point in the pipeline where the hoister runs
(after data_type_refiner, duplication_remover, default_value_filler).
Base class references use ClassRef nodes with fully-qualified names.
"""

from docutils.frontend import OptionParser
from docutils.parsers.rst import Parser as RstParser
from docutils.utils import new_document

from fake_bpy_module.analyzer.nodes import (
    ArgumentListNode,
    ArgumentNode,
    AttributeListNode,
    AttributeNode,
    BaseClassListNode,
    BaseClassNode,
    ClassNode,
    DataTypeListNode,
    DataTypeNode,
    FunctionListNode,
    FunctionNode,
    FunctionReturnNode,
    ModuleNode,
    NameNode,
)
from fake_bpy_module.analyzer.roles import ClassRef
from fake_bpy_module.transformer.transformer import Transformer
from fake_bpy_module.utils import append_child, find_children

from . import common


def _make_document():
    """Create a fresh empty docutils document."""
    settings = OptionParser(components=(RstParser,)).get_default_values()
    return new_document("<test>", settings)


def _add_module(doc, module_name):
    """Add a ModuleNode to a document."""
    mod = ModuleNode.create_template()
    mod.element(NameNode).add_text(module_name)
    append_child(doc, mod)
    return mod


def _make_base_class_node(parent_fqn):
    """Create a BaseClassNode with a ClassRef pointing to a FQN."""
    bc = BaseClassNode.create_template()
    dt = DataTypeNode()
    cr = ClassRef("", parent_fqn)
    append_child(dt, cr)
    bc.element(DataTypeListNode).append_child(dt)
    return bc


def _add_class(doc, class_name, base_class_fqns=None):
    """Add a ClassNode to a document, optionally with base classes."""
    cls = ClassNode.create_template()
    cls.element(NameNode).add_text(class_name)
    if base_class_fqns:
        bcl = cls.element(BaseClassListNode)
        for fqn in base_class_fqns:
            bcl.append_child(_make_base_class_node(fqn))
    append_child(doc, cls)
    return cls


def _add_attribute(class_node, attr_name, attr_type):
    """Add an AttributeNode to a class."""
    attr = AttributeNode.create_template()
    attr.element(NameNode).add_text(attr_name)
    dt = DataTypeNode(text=attr_type)
    attr.element(DataTypeListNode).append_child(dt)
    class_node.element(AttributeListNode).append_child(attr)
    return attr


def _add_method(
    class_node, method_name, args=None, return_type=None, function_type="method"
):
    """Add a FunctionNode (method) to a class.

    args: list of (name, type_str) tuples
    return_type: str or None
    """
    func = FunctionNode.create_template()
    func.attributes["function_type"] = function_type
    func.element(NameNode).add_text(method_name)
    if args:
        arg_list = func.element(ArgumentListNode)
        for arg_name, arg_type in args:
            arg = ArgumentNode.create_template()
            arg.attributes["argument_type"] = "arg"
            arg.element(NameNode).add_text(arg_name)
            dt = DataTypeNode(text=arg_type)
            arg.element(DataTypeListNode).append_child(dt)
            arg_list.append_child(arg)
    if return_type:
        ret = func.element(FunctionReturnNode)
        dt = DataTypeNode(text=return_type)
        ret.element(DataTypeListNode).append_child(dt)
    class_node.element(FunctionListNode).append_child(func)
    return func


def _get_attr_names(class_node):
    """Get set of attribute names in a class."""
    return {
        attr.element(NameNode).astext()
        for attr in find_children(
            class_node.element(AttributeListNode), AttributeNode
        )
    }


def _get_func_names(class_node):
    """Get set of function names in a class."""
    return {
        func.element(NameNode).astext()
        for func in find_children(
            class_node.element(FunctionListNode), FunctionNode
        )
    }


class CommonMemberHoisterTest(common.FakeBpyModuleTestBase):
    name = "CommonMemberHoisterTest"
    module_name = __module__

    def _run_hoister(self, documents):
        transformer = Transformer(["common_member_hoister"])
        return transformer.transform(documents)

    # ----------------------------------------------------------------
    # Test 1: Basic same-module hoisting.
    #   Parent with two children in the same module.
    #   Both children share an attribute and a method.
    #   Expect: hoisted to parent, removed from children.
    # ----------------------------------------------------------------
    def test_basic_same_module(self):
        doc = _make_document()
        _add_module(doc, "mod_a")
        parent = _add_class(doc, "Parent")
        child_a = _add_class(doc, "ChildA", base_class_fqns=["mod_a.Parent"])
        child_b = _add_class(doc, "ChildB", base_class_fqns=["mod_a.Parent"])

        # Both children have common_attr: int
        _add_attribute(child_a, "common_attr", "int")
        _add_attribute(child_b, "common_attr", "int")

        # Both children have common_method(self, x: int) -> bool
        _add_method(
            child_a, "common_method", args=[("x", "int")], return_type="bool"
        )
        _add_method(
            child_b, "common_method", args=[("x", "int")], return_type="bool"
        )

        # Child A also has a unique attribute
        _add_attribute(child_a, "unique_a", "str")

        self._run_hoister([doc])

        # Parent should now have common_attr and common_method
        self.assertEqual(_get_attr_names(parent), {"common_attr"})
        self.assertEqual(_get_func_names(parent), {"common_method"})

        # Children should no longer have common_attr / common_method
        self.assertEqual(_get_attr_names(child_a), {"unique_a"})
        self.assertEqual(_get_attr_names(child_b), set())
        self.assertEqual(_get_func_names(child_a), set())
        self.assertEqual(_get_func_names(child_b), set())

    # ----------------------------------------------------------------
    # Test 2: Cross-module hoisting.
    #   Parent in module_a, children in module_b.
    # ----------------------------------------------------------------
    def test_cross_module(self):
        doc_a = _make_document()
        _add_module(doc_a, "mod_a")
        parent = _add_class(doc_a, "Parent")

        doc_b = _make_document()
        _add_module(doc_b, "mod_b")
        child_a = _add_class(doc_b, "ChildA", base_class_fqns=["mod_a.Parent"])
        child_b = _add_class(doc_b, "ChildB", base_class_fqns=["mod_a.Parent"])

        _add_attribute(child_a, "shared_attr", "str")
        _add_attribute(child_b, "shared_attr", "str")

        self._run_hoister([doc_a, doc_b])

        self.assertEqual(_get_attr_names(parent), {"shared_attr"})
        self.assertEqual(_get_attr_names(child_a), set())
        self.assertEqual(_get_attr_names(child_b), set())

    # ----------------------------------------------------------------
    # Test 3: Skip if parent already has the member.
    # ----------------------------------------------------------------
    def test_skip_existing_parent_member(self):
        doc = _make_document()
        _add_module(doc, "mod_a")
        parent = _add_class(doc, "Parent")
        child_a = _add_class(doc, "ChildA", base_class_fqns=["mod_a.Parent"])
        child_b = _add_class(doc, "ChildB", base_class_fqns=["mod_a.Parent"])

        # Parent already has existing_attr
        _add_attribute(parent, "existing_attr", "int")

        # Children also have existing_attr
        _add_attribute(child_a, "existing_attr", "int")
        _add_attribute(child_b, "existing_attr", "int")

        self._run_hoister([doc])

        # Parent still has exactly one existing_attr (not duplicated)
        self.assertEqual(_get_attr_names(parent), {"existing_attr"})
        attr_count = len(
            find_children(parent.element(AttributeListNode), AttributeNode)
        )
        self.assertEqual(attr_count, 1)

        # Children still have their copies (not removed since parent
        # already had it, no hoisting happened)
        self.assertEqual(_get_attr_names(child_a), {"existing_attr"})
        self.assertEqual(_get_attr_names(child_b), {"existing_attr"})

    # ----------------------------------------------------------------
    # Test 4: No hoisting when not all children share the member.
    # ----------------------------------------------------------------
    def test_no_hoist_partial_common(self):
        doc = _make_document()
        _add_module(doc, "mod_a")
        parent = _add_class(doc, "Parent")
        child_a = _add_class(doc, "ChildA", base_class_fqns=["mod_a.Parent"])
        child_b = _add_class(doc, "ChildB", base_class_fqns=["mod_a.Parent"])
        child_c = _add_class(doc, "ChildC", base_class_fqns=["mod_a.Parent"])

        # Only ChildA and ChildB have partial_attr (ChildC does NOT)
        _add_attribute(child_a, "partial_attr", "int")
        _add_attribute(child_b, "partial_attr", "int")

        self._run_hoister([doc])

        # Parent should NOT have partial_attr
        self.assertEqual(_get_attr_names(parent), set())
        # Children keep their attributes
        self.assertEqual(_get_attr_names(child_a), {"partial_attr"})
        self.assertEqual(_get_attr_names(child_b), {"partial_attr"})
        self.assertEqual(_get_attr_names(child_c), set())

    # ----------------------------------------------------------------
    # Test 5: No hoisting when signatures differ.
    # ----------------------------------------------------------------
    def test_no_hoist_different_signatures(self):
        doc = _make_document()
        _add_module(doc, "mod_a")
        parent = _add_class(doc, "Parent")
        child_a = _add_class(doc, "ChildA", base_class_fqns=["mod_a.Parent"])
        child_b = _add_class(doc, "ChildB", base_class_fqns=["mod_a.Parent"])

        # Same name but different argument types
        _add_method(
            child_a, "method_x", args=[("x", "int")], return_type="bool"
        )
        _add_method(
            child_b, "method_x", args=[("x", "str")], return_type="bool"
        )

        # Same name but different attribute types
        _add_attribute(child_a, "typed_attr", "int")
        _add_attribute(child_b, "typed_attr", "str")

        self._run_hoister([doc])

        # Parent should NOT have anything
        self.assertEqual(_get_attr_names(parent), set())
        self.assertEqual(_get_func_names(parent), set())

        # Children keep everything
        self.assertEqual(_get_attr_names(child_a), {"typed_attr"})
        self.assertEqual(_get_attr_names(child_b), {"typed_attr"})
        self.assertEqual(_get_func_names(child_a), {"method_x"})
        self.assertEqual(_get_func_names(child_b), {"method_x"})

    # ----------------------------------------------------------------
    # Test 6: No hoisting for different function_type.
    #   method vs classmethod should not be considered the same.
    # ----------------------------------------------------------------
    def test_no_hoist_different_function_type(self):
        doc = _make_document()
        _add_module(doc, "mod_a")
        parent = _add_class(doc, "Parent")
        child_a = _add_class(doc, "ChildA", base_class_fqns=["mod_a.Parent"])
        child_b = _add_class(doc, "ChildB", base_class_fqns=["mod_a.Parent"])

        _add_method(
            child_a,
            "do_thing",
            args=[("x", "int")],
            return_type="bool",
            function_type="method",
        )
        _add_method(
            child_b,
            "do_thing",
            args=[("x", "int")],
            return_type="bool",
            function_type="classmethod",
        )

        self._run_hoister([doc])

        self.assertEqual(_get_func_names(parent), set())
        self.assertEqual(_get_func_names(child_a), {"do_thing"})
        self.assertEqual(_get_func_names(child_b), {"do_thing"})

    # ----------------------------------------------------------------
    # Test 7: Single child — no hoisting (need >= 2).
    # ----------------------------------------------------------------
    def test_single_child_no_hoist(self):
        doc = _make_document()
        _add_module(doc, "mod_a")
        parent = _add_class(doc, "Parent")
        child = _add_class(doc, "OnlyChild", base_class_fqns=["mod_a.Parent"])

        _add_attribute(child, "lonely_attr", "int")

        self._run_hoister([doc])

        self.assertEqual(_get_attr_names(parent), set())
        self.assertEqual(_get_attr_names(child), {"lonely_attr"})

    # ----------------------------------------------------------------
    # Test 8: No children at all — no changes.
    # ----------------------------------------------------------------
    def test_no_children(self):
        doc = _make_document()
        _add_module(doc, "mod_a")
        parent = _add_class(doc, "Standalone")
        _add_attribute(parent, "own_attr", "float")

        self._run_hoister([doc])

        self.assertEqual(_get_attr_names(parent), {"own_attr"})

    # ----------------------------------------------------------------
    # Test 9: Multi-level inheritance (Grandparent -> Parent -> Kids).
    #   Children share an attribute; Parent and Uncle also share one.
    #   Bottom-up processing should hoist from children first, then
    #   from parent+uncle to grandparent.
    # ----------------------------------------------------------------
    def test_multi_level_hoisting(self):
        doc = _make_document()
        _add_module(doc, "mod_a")
        grandparent = _add_class(doc, "GrandParent")
        parent = _add_class(
            doc, "Parent", base_class_fqns=["mod_a.GrandParent"]
        )
        uncle = _add_class(doc, "Uncle", base_class_fqns=["mod_a.GrandParent"])
        child_a = _add_class(doc, "ChildA", base_class_fqns=["mod_a.Parent"])
        child_b = _add_class(doc, "ChildB", base_class_fqns=["mod_a.Parent"])

        # Both children share deep_attr -> hoisted to Parent
        _add_attribute(child_a, "deep_attr", "int")
        _add_attribute(child_b, "deep_attr", "int")

        # Parent and Uncle share shallow_attr -> hoisted to GrandParent
        _add_attribute(parent, "shallow_attr", "str")
        _add_attribute(uncle, "shallow_attr", "str")

        self._run_hoister([doc])

        # deep_attr should have been hoisted to Parent
        self.assertIn("deep_attr", _get_attr_names(parent))
        self.assertEqual(_get_attr_names(child_a), set())
        self.assertEqual(_get_attr_names(child_b), set())

        # shallow_attr hoisted to GrandParent
        self.assertIn("shallow_attr", _get_attr_names(grandparent))
        # Parent might still have deep_attr; shallow_attr removed
        self.assertNotIn("shallow_attr", _get_attr_names(parent))
        self.assertNotIn("shallow_attr", _get_attr_names(uncle))

    # ----------------------------------------------------------------
    # Test 10: Complex cross-module with multiple modules and files.
    #   module_a: BaseA
    #   module_b: ChildB1(BaseA), ChildB2(BaseA)
    #   module_c: ChildC1(BaseA), SubBase
    #   module_d: ChildD1(SubBase), ChildD2(SubBase)
    #   All of BaseA's children (B1, B2, C1) share attr_all: int
    #   B1 and B2 (but not C1) share attr_partial: float -> no hoist
    #   D1 and D2 share sub_attr: str -> hoisted to SubBase
    # ----------------------------------------------------------------
    def test_complex_cross_module(self):
        doc_a = _make_document()
        _add_module(doc_a, "mod_a")
        base_a = _add_class(doc_a, "BaseA")

        doc_b = _make_document()
        _add_module(doc_b, "mod_b")
        child_b1 = _add_class(doc_b, "ChildB1", base_class_fqns=["mod_a.BaseA"])
        child_b2 = _add_class(doc_b, "ChildB2", base_class_fqns=["mod_a.BaseA"])

        doc_c = _make_document()
        _add_module(doc_c, "mod_c")
        child_c1 = _add_class(doc_c, "ChildC1", base_class_fqns=["mod_a.BaseA"])
        sub_base = _add_class(doc_c, "SubBase")

        doc_d = _make_document()
        _add_module(doc_d, "mod_d")
        child_d1 = _add_class(
            doc_d, "ChildD1", base_class_fqns=["mod_c.SubBase"]
        )
        child_d2 = _add_class(
            doc_d, "ChildD2", base_class_fqns=["mod_c.SubBase"]
        )

        # All BaseA children share attr_all
        _add_attribute(child_b1, "attr_all", "int")
        _add_attribute(child_b2, "attr_all", "int")
        _add_attribute(child_c1, "attr_all", "int")

        # Only B1 and B2 share attr_partial (C1 doesn't)
        _add_attribute(child_b1, "attr_partial", "float")
        _add_attribute(child_b2, "attr_partial", "float")

        # D1 and D2 share sub_attr
        _add_attribute(child_d1, "sub_attr", "str")
        _add_attribute(child_d2, "sub_attr", "str")

        # All BaseA children share common_method
        _add_method(
            child_b1, "common_method", args=[("x", "int")], return_type="bool"
        )
        _add_method(
            child_b2, "common_method", args=[("x", "int")], return_type="bool"
        )
        _add_method(
            child_c1, "common_method", args=[("x", "int")], return_type="bool"
        )

        self._run_hoister([doc_a, doc_b, doc_c, doc_d])

        # attr_all and common_method should be hoisted to BaseA
        self.assertEqual(_get_attr_names(base_a), {"attr_all"})
        self.assertEqual(_get_func_names(base_a), {"common_method"})

        # Children should not have attr_all or common_method anymore
        self.assertNotIn("attr_all", _get_attr_names(child_b1))
        self.assertNotIn("attr_all", _get_attr_names(child_b2))
        self.assertNotIn("attr_all", _get_attr_names(child_c1))
        self.assertNotIn("common_method", _get_func_names(child_b1))

        # attr_partial not hoisted (only 2 of 3 children have it)
        self.assertNotIn("attr_partial", _get_attr_names(base_a))
        self.assertIn("attr_partial", _get_attr_names(child_b1))
        self.assertIn("attr_partial", _get_attr_names(child_b2))

        # sub_attr hoisted to SubBase
        self.assertEqual(_get_attr_names(sub_base), {"sub_attr"})
        self.assertEqual(_get_attr_names(child_d1), set())
        self.assertEqual(_get_attr_names(child_d2), set())

    # ----------------------------------------------------------------
    # Test 11: External base class (not in our documents).
    #   Children inherit from "ext_module.ExternalClass" which is not
    #   in any of our documents. Should not crash.
    # ----------------------------------------------------------------
    def test_external_base_class(self):
        doc = _make_document()
        _add_module(doc, "mod_a")
        child_a = _add_class(
            doc, "ChildA", base_class_fqns=["ext_module.ExternalClass"]
        )
        child_b = _add_class(
            doc, "ChildB", base_class_fqns=["ext_module.ExternalClass"]
        )

        _add_attribute(child_a, "attr", "int")
        _add_attribute(child_b, "attr", "int")

        # Should not crash; no hoisting since parent is external
        self._run_hoister([doc])

        self.assertEqual(_get_attr_names(child_a), {"attr"})
        self.assertEqual(_get_attr_names(child_b), {"attr"})

    # ----------------------------------------------------------------
    # Test 12: Mixed hoisting — some attributes hoisted, some not.
    # ----------------------------------------------------------------
    def test_mixed_hoisting(self):
        doc = _make_document()
        _add_module(doc, "mod_a")
        parent = _add_class(doc, "Parent")
        child_a = _add_class(doc, "ChildA", base_class_fqns=["mod_a.Parent"])
        child_b = _add_class(doc, "ChildB", base_class_fqns=["mod_a.Parent"])

        # Shared by both -> hoisted
        _add_attribute(child_a, "shared", "int")
        _add_attribute(child_b, "shared", "int")

        # Only on child_a -> not hoisted
        _add_attribute(child_a, "only_a", "str")

        # Only on child_b -> not hoisted
        _add_attribute(child_b, "only_b", "float")

        # Shared method
        _add_method(
            child_a,
            "shared_method",
            args=[("a", "int"), ("b", "str")],
            return_type="float",
        )
        _add_method(
            child_b,
            "shared_method",
            args=[("a", "int"), ("b", "str")],
            return_type="float",
        )

        # Unique methods
        _add_method(child_a, "unique_method_a", args=[], return_type="int")

        self._run_hoister([doc])

        self.assertEqual(_get_attr_names(parent), {"shared"})
        self.assertEqual(_get_func_names(parent), {"shared_method"})

        self.assertEqual(_get_attr_names(child_a), {"only_a"})
        self.assertEqual(_get_attr_names(child_b), {"only_b"})
        self.assertEqual(_get_func_names(child_a), {"unique_method_a"})
        self.assertEqual(_get_func_names(child_b), set())

    # ----------------------------------------------------------------
    # Test 13: Hoisted attribute preserves type information.
    # ----------------------------------------------------------------
    def test_hoisted_attribute_preserves_type(self):
        doc = _make_document()
        _add_module(doc, "mod_a")
        parent = _add_class(doc, "Parent")
        child_a = _add_class(doc, "ChildA", base_class_fqns=["mod_a.Parent"])
        child_b = _add_class(doc, "ChildB", base_class_fqns=["mod_a.Parent"])

        _add_attribute(child_a, "typed_attr", "float")
        _add_attribute(child_b, "typed_attr", "float")

        self._run_hoister([doc])

        # Verify the hoisted attribute has correct type
        parent_attrs = find_children(
            parent.element(AttributeListNode), AttributeNode
        )
        self.assertEqual(len(parent_attrs), 1)
        hoisted_attr = parent_attrs[0]
        self.assertEqual(hoisted_attr.element(NameNode).astext(), "typed_attr")
        dtype_nodes = find_children(
            hoisted_attr.element(DataTypeListNode), DataTypeNode
        )
        self.assertEqual(len(dtype_nodes), 1)
        self.assertEqual(dtype_nodes[0].to_string(), "float")

    # ----------------------------------------------------------------
    # Test 14: Hoisted method preserves full signature.
    # ----------------------------------------------------------------
    def test_hoisted_method_preserves_signature(self):
        doc = _make_document()
        _add_module(doc, "mod_a")
        parent = _add_class(doc, "Parent")
        child_a = _add_class(doc, "ChildA", base_class_fqns=["mod_a.Parent"])
        child_b = _add_class(doc, "ChildB", base_class_fqns=["mod_a.Parent"])

        _add_method(
            child_a,
            "calc",
            args=[("x", "int"), ("y", "float")],
            return_type="str",
        )
        _add_method(
            child_b,
            "calc",
            args=[("x", "int"), ("y", "float")],
            return_type="str",
        )

        self._run_hoister([doc])

        parent_funcs = find_children(
            parent.element(FunctionListNode), FunctionNode
        )
        self.assertEqual(len(parent_funcs), 1)
        hoisted_func = parent_funcs[0]
        self.assertEqual(hoisted_func.element(NameNode).astext(), "calc")

        # Check arguments
        args = find_children(
            hoisted_func.element(ArgumentListNode), ArgumentNode
        )
        self.assertEqual(len(args), 2)
        self.assertEqual(args[0].element(NameNode).astext(), "x")
        self.assertEqual(args[1].element(NameNode).astext(), "y")

        dt_x = find_children(args[0].element(DataTypeListNode), DataTypeNode)
        self.assertEqual(dt_x[0].to_string(), "int")
        dt_y = find_children(args[1].element(DataTypeListNode), DataTypeNode)
        self.assertEqual(dt_y[0].to_string(), "float")

        # Check return type
        ret = hoisted_func.element(FunctionReturnNode)
        ret_dtypes = find_children(ret.element(DataTypeListNode), DataTypeNode)
        self.assertEqual(len(ret_dtypes), 1)
        self.assertEqual(ret_dtypes[0].to_string(), "str")

    # ----------------------------------------------------------------
    # Test 15: Deep multi-level chain (A -> B -> C -> D1, D2).
    #   D1 and D2 share an attribute -> hoisted to C.
    #   C is the only child of B, so nothing hoists from C to B.
    # ----------------------------------------------------------------
    def test_deep_chain(self):
        doc = _make_document()
        _add_module(doc, "m")
        a = _add_class(doc, "A")
        b = _add_class(doc, "B", base_class_fqns=["m.A"])
        c = _add_class(doc, "C", base_class_fqns=["m.B"])
        d1 = _add_class(doc, "D1", base_class_fqns=["m.C"])
        d2 = _add_class(doc, "D2", base_class_fqns=["m.C"])

        _add_attribute(d1, "deep_val", "int")
        _add_attribute(d2, "deep_val", "int")

        self._run_hoister([doc])

        # deep_val hoisted to C
        self.assertIn("deep_val", _get_attr_names(c))
        self.assertEqual(_get_attr_names(d1), set())
        self.assertEqual(_get_attr_names(d2), set())

        # B has only one child (C) so nothing hoists to B
        self.assertEqual(_get_attr_names(b), set())
        self.assertEqual(_get_attr_names(a), set())

    # ----------------------------------------------------------------
    # Test 16: Children across many different modules.
    #   Parent in mod_a, children spread across mod_b, mod_c, mod_d.
    # ----------------------------------------------------------------
    def test_children_across_many_modules(self):
        doc_a = _make_document()
        _add_module(doc_a, "mod_a")
        parent = _add_class(doc_a, "Base")

        doc_b = _make_document()
        _add_module(doc_b, "mod_b")
        c1 = _add_class(doc_b, "Child1", base_class_fqns=["mod_a.Base"])

        doc_c = _make_document()
        _add_module(doc_c, "mod_c")
        c2 = _add_class(doc_c, "Child2", base_class_fqns=["mod_a.Base"])

        doc_d = _make_document()
        _add_module(doc_d, "mod_d")
        c3 = _add_class(doc_d, "Child3", base_class_fqns=["mod_a.Base"])

        # All three children have the same attribute and method
        for child in [c1, c2, c3]:
            _add_attribute(child, "universal", "bool")
            _add_method(
                child, "do_work", args=[("n", "int")], return_type="str"
            )

        self._run_hoister([doc_a, doc_b, doc_c, doc_d])

        self.assertEqual(_get_attr_names(parent), {"universal"})
        self.assertEqual(_get_func_names(parent), {"do_work"})

        for child in [c1, c2, c3]:
            self.assertEqual(_get_attr_names(child), set())
            self.assertEqual(_get_func_names(child), set())

    # ----------------------------------------------------------------
    # Test 17: No hoisting when different return types.
    # ----------------------------------------------------------------
    def test_no_hoist_different_return_type(self):
        doc = _make_document()
        _add_module(doc, "mod_a")
        parent = _add_class(doc, "Parent")
        child_a = _add_class(doc, "ChildA", base_class_fqns=["mod_a.Parent"])
        child_b = _add_class(doc, "ChildB", base_class_fqns=["mod_a.Parent"])

        _add_method(child_a, "get_val", args=[], return_type="int")
        _add_method(child_b, "get_val", args=[], return_type="str")

        self._run_hoister([doc])

        self.assertEqual(_get_func_names(parent), set())
        self.assertEqual(_get_func_names(child_a), {"get_val"})
        self.assertEqual(_get_func_names(child_b), {"get_val"})

    # ----------------------------------------------------------------
    # Test 18: No hoisting when argument count differs.
    # ----------------------------------------------------------------
    def test_no_hoist_different_arg_count(self):
        doc = _make_document()
        _add_module(doc, "mod_a")
        parent = _add_class(doc, "Parent")
        child_a = _add_class(doc, "ChildA", base_class_fqns=["mod_a.Parent"])
        child_b = _add_class(doc, "ChildB", base_class_fqns=["mod_a.Parent"])

        _add_method(child_a, "compute", args=[("x", "int")], return_type="int")
        _add_method(
            child_b,
            "compute",
            args=[("x", "int"), ("y", "int")],
            return_type="int",
        )

        self._run_hoister([doc])

        self.assertEqual(_get_func_names(parent), set())

    # ----------------------------------------------------------------
    # Test 19: Empty documents — no crash.
    # ----------------------------------------------------------------
    def test_empty_documents(self):
        doc = _make_document()
        self._run_hoister([doc])  # Should not crash

    # ----------------------------------------------------------------
    # Test 20: Multi-level cross-module hoisting.
    #   mod_a: GrandParent
    #   mod_b: Parent(GrandParent), Uncle(GrandParent)
    #   mod_c: ChildA(Parent), ChildB(Parent)
    #   ChildA and ChildB share child_attr -> hoisted to Parent.
    #   Parent and Uncle share sibling_attr -> hoisted to GrandParent.
    # ----------------------------------------------------------------
    def test_multi_level_cross_module(self):
        doc_a = _make_document()
        _add_module(doc_a, "mod_a")
        grandparent = _add_class(doc_a, "GrandParent")

        doc_b = _make_document()
        _add_module(doc_b, "mod_b")
        parent = _add_class(
            doc_b, "Parent", base_class_fqns=["mod_a.GrandParent"]
        )
        uncle = _add_class(
            doc_b, "Uncle", base_class_fqns=["mod_a.GrandParent"]
        )

        doc_c = _make_document()
        _add_module(doc_c, "mod_c")
        child_a = _add_class(doc_c, "ChildA", base_class_fqns=["mod_b.Parent"])
        child_b = _add_class(doc_c, "ChildB", base_class_fqns=["mod_b.Parent"])

        # Children share child_attr
        _add_attribute(child_a, "child_attr", "int")
        _add_attribute(child_b, "child_attr", "int")

        # Parent and Uncle share sibling_attr
        _add_attribute(parent, "sibling_attr", "str")
        _add_attribute(uncle, "sibling_attr", "str")

        self._run_hoister([doc_a, doc_b, doc_c])

        # child_attr hoisted from ChildA/ChildB to Parent
        self.assertIn("child_attr", _get_attr_names(parent))
        self.assertEqual(_get_attr_names(child_a), set())
        self.assertEqual(_get_attr_names(child_b), set())

        # sibling_attr hoisted from Parent/Uncle to GrandParent
        self.assertIn("sibling_attr", _get_attr_names(grandparent))
        self.assertNotIn("sibling_attr", _get_attr_names(parent))
        self.assertNotIn("sibling_attr", _get_attr_names(uncle))
