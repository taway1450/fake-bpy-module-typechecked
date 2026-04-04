from docutils import nodes

from fake_bpy_module.analyzer.nodes import (
    ArgumentListNode,
    ArgumentNode,
    DataTypeListNode,
    DataTypeNode,
    DefaultValueNode,
    FunctionNode,
    FunctionReturnNode,
    ModuleNode,
    NameNode,
    make_data_type_node,
)
from fake_bpy_module.utils import (
    append_child,
    find_children,
    get_first_child,
)

from .transformer_base import TransformerBase

# FloatVectorProperty type constants.
_FLOAT_VECTOR_BASE_RETURN = "bpy.types.bpy_prop_array[float]"
_VECTOR_SIZED_LITERAL = "typing.Literal[2, 3, 4]"
_COLOR_SIZED_LITERAL = "typing.Literal[3]"
_EULER_SIZED_LITERAL = "typing.Literal[3]"
_QUATERNION_SIZED_LITERAL = "typing.Literal[4]"
_MATRIX_SIZED_LITERAL = "typing.Literal[9, 16]"
_VECTOR_SIZE_LITERAL_RANGE = (
    "typing.Literal["
    "1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, "
    "17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31"
    "]"
)


# FloatVectorProperty specialized overloads.
# Each entry: (subtype literals, return type, required size literals).
_FLOAT_VECTOR_SPECIALIZED_OVERLOADS: list[tuple[tuple[str, ...], str, str]] = [
    (
        (
            "TRANSLATION",
            "DIRECTION",
            "VELOCITY",
            "ACCELERATION",
            "XYZ",
            "XYZ_LENGTH",
            "COORDINATES",
        ),
        "`mathutils.Vector`",
        _VECTOR_SIZED_LITERAL,
    ),
    (
        ("COLOR", "COLOR_GAMMA"),
        "`mathutils.Color`",
        _COLOR_SIZED_LITERAL,
    ),
    (
        ("EULER",),
        "`mathutils.Euler`",
        _EULER_SIZED_LITERAL,
    ),
    (
        ("QUATERNION",),
        "`mathutils.Quaternion`",
        _QUATERNION_SIZED_LITERAL,
    ),
    (
        ("MATRIX",),
        "`mathutils.Matrix`",
        _MATRIX_SIZED_LITERAL,
    ),
]


_FLOAT_VECTOR_BASE_SUBTYPES: tuple[str, ...] = (
    "NONE",
    "COLOR",
    "AXISANGLE",
    "MATRIX",
    "LAYER",
    "LAYER_MEMBER",
)


# EnumProperty option literals.
_ENUM_PROP_OPTIONS_COMMON: tuple[str, ...] = (
    "HIDDEN",
    "SKIP_SAVE",
    "ANIMATABLE",
    "LIBRARY_EDITABLE",
)
_ENUM_PROP_OPTIONS_ALL: tuple[str, ...] = (
    *_ENUM_PROP_OPTIONS_COMMON,
    "ENUM_FLAG",
)


class BpyPropsOverloadGenerator(TransformerBase):
    """Generate ``@typing.overload`` variants for ``bpy.props`` functions.

    * **EnumProperty** - distinguishes ``str`` vs ``set[str]`` return type
      based on whether ``'ENUM_FLAG'`` is present in the ``options``
      parameter Literal set.
        * **FloatVectorProperty** - distinguishes specialized mathutils
            return types based on ``subtype`` and constrained ``size``
            Literals; defaults to ``bpy.types.bpy_prop_array[float]``.
    """

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _find_argument(
        func_node: FunctionNode, arg_name: str
    ) -> ArgumentNode | None:
        """Return the *ArgumentNode* with the given name, or ``None``."""
        arg_list_node = func_node.element(ArgumentListNode)
        for arg_node in find_children(arg_list_node, ArgumentNode):
            if arg_node.element(NameNode).astext() == arg_name:
                return arg_node
        return None

    @staticmethod
    def _replace_data_type_list(
        dtype_list_node: DataTypeListNode,
        new_types: list[DataTypeNode],
    ) -> None:
        """Clear *dtype_list_node* and fill it with *new_types*."""
        for child in list(dtype_list_node.children):
            dtype_list_node.remove(child)
        for dtype_node in new_types:
            dtype_list_node.append_child(dtype_node)

    @staticmethod
    def _make_skip_refine_dtype(type_str: str) -> DataTypeNode:
        """Create a plain-text ``DataTypeNode`` marked *skip-refine*."""
        dtype_node = DataTypeNode()
        append_child(dtype_node, nodes.Text(type_str))
        dtype_node.attributes["mod-option"] = "skip-refine"
        return dtype_node

    def _set_return_type(
        self,
        func_node: FunctionNode,
        type_specs: list[str | DataTypeNode],
    ) -> None:
        """Replace the return type of *func_node*."""
        return_node = func_node.element(FunctionReturnNode)
        dtype_list_node = return_node.element(DataTypeListNode)
        new_nodes = [
            t
            if isinstance(t, DataTypeNode)
            else self._make_skip_refine_dtype(t)
            for t in type_specs
        ]
        self._replace_data_type_list(dtype_list_node, new_nodes)

    def _set_arg_type(
        self,
        arg_node: ArgumentNode,
        type_specs: list[str | DataTypeNode],
    ) -> None:
        """Replace the data-type list of *arg_node*."""
        dtype_list_node = arg_node.element(DataTypeListNode)
        new_nodes = [
            t
            if isinstance(t, DataTypeNode)
            else self._make_skip_refine_dtype(t)
            for t in type_specs
        ]
        self._replace_data_type_list(dtype_list_node, new_nodes)

    @staticmethod
    def _set_arg_default(
        arg_node: ArgumentNode,
        default_value: str | None,
    ) -> None:
        """Set or clear the default value of *arg_node*."""
        default_node = arg_node.element(DefaultValueNode)
        for child in list(default_node.children):
            default_node.remove(child)
        if default_value is not None:
            append_child(default_node, nodes.Text(default_value))

    def _set_subtype_literal(
        self,
        func_node: FunctionNode,
        literal_values: tuple[str, ...],
        *,
        clear_default: bool,
    ) -> None:
        subtype_arg = self._find_argument(func_node, "subtype")
        if subtype_arg is None:
            return

        literal_csv = ", ".join(f"'{v}'" for v in literal_values)
        self._set_arg_type(subtype_arg, [f"typing.Literal[{literal_csv}]"])
        if clear_default:
            self._set_arg_default(subtype_arg, None)

    def _set_float_vector_size_type(
        self,
        func_node: FunctionNode,
        size_literal: str,
    ) -> None:
        size_arg = self._find_argument(func_node, "size")
        if size_arg is None:
            return
        self._set_arg_type(
            size_arg,
            [f"{size_literal} | collections.abc.Sequence[int] | None"],
        )

    @staticmethod
    def _normalize_list_to_sequence(type_str: str) -> str:
        """Replace ``list[...]`` with ``collections.abc.Sequence[...]``."""
        return type_str.replace("list[", "collections.abc.Sequence[")

    # ------------------------------------------------------------------
    # EnumProperty
    # ------------------------------------------------------------------

    @staticmethod
    def _make_options_literal(values: tuple[str, ...]) -> str:
        """Build ``set[typing.Literal['A', 'B', ...]]`` type string."""
        csv = ", ".join(f"'{v}'" for v in values)
        return f"set[typing.Literal[{csv}]]"

    def _generate_enum_property_overloads(
        self, document: nodes.document
    ) -> None:
        func_nodes = find_children(document, FunctionNode)
        target_node: FunctionNode | None = None
        for func_node in func_nodes:
            if func_node.element(NameNode).astext() == "EnumProperty":
                target_node = func_node
                break
        if target_node is None:
            return

        # We need the 'options' argument to distinguish the overloads.
        if self._find_argument(target_node, "options") is None:
            return

        index = list(document.children).index(target_node)

        # Overload 1 - no ENUM_FLAG -> str
        str_overload = target_node.deepcopy()
        str_overload.attributes["option"] = "overload"
        options_arg = self._find_argument(str_overload, "options")
        default_arg = self._find_argument(str_overload, "default")
        if default_arg is not None:
            self._set_arg_type(default_arg, ["str | int | None"])
        if options_arg is not None:
            self._set_arg_type(
                options_arg,
                [self._make_options_literal(_ENUM_PROP_OPTIONS_COMMON)],
            )
        self._set_return_type(str_overload, ["str"])

        # Overload 2 - ENUM_FLAG present -> set[str]
        set_overload = target_node.deepcopy()
        set_overload.attributes["option"] = "overload"
        default_arg = self._find_argument(set_overload, "default")
        if default_arg is not None:
            self._set_arg_type(default_arg, ["set[str] | None"])
        options_arg = self._find_argument(set_overload, "options")
        if options_arg is not None:
            self._set_arg_type(
                options_arg,
                [self._make_options_literal(_ENUM_PROP_OPTIONS_ALL)],
            )
        self._set_return_type(set_overload, ["set[str]"])

        # Replace the original node with both overloads.
        document.remove(target_node)
        document.insert(index, set_overload)
        document.insert(index, str_overload)

    # ------------------------------------------------------------------
    # FloatVectorProperty
    # ------------------------------------------------------------------

    def _generate_float_vector_property_overloads(
        self, document: nodes.document
    ) -> None:
        func_nodes = find_children(document, FunctionNode)
        target_node: FunctionNode | None = None
        for func_node in func_nodes:
            if func_node.element(NameNode).astext() == "FloatVectorProperty":
                target_node = func_node
                break
        if target_node is None:
            return

        if self._find_argument(target_node, "subtype") is None:
            return

        index = list(document.children).index(target_node)
        overload_nodes: list[FunctionNode] = []

        # Subtype and size-specific overloads.
        for (
            literal_values,
            return_type_str,
            size_literal,
        ) in _FLOAT_VECTOR_SPECIALIZED_OVERLOADS:
            overload = target_node.deepcopy()
            overload.attributes["option"] = "overload"
            self._set_subtype_literal(
                overload,
                literal_values,
                clear_default=True,
            )
            self._set_float_vector_size_type(overload, size_literal)

            ret_dtype = make_data_type_node(return_type_str)
            ret_dtype.attributes["mod-option"] = "skip-refine"
            self._set_return_type(overload, [ret_dtype])

            overload_nodes.append(overload)

        # Base subtype overloads -> bpy_prop_array[float].
        base_overload = target_node.deepcopy()
        base_overload.attributes["option"] = "overload"
        self._set_subtype_literal(
            base_overload,
            _FLOAT_VECTOR_BASE_SUBTYPES,
            clear_default=False,
        )
        self._set_float_vector_size_type(
            base_overload,
            _VECTOR_SIZE_LITERAL_RANGE,
        )
        self._set_return_type(base_overload, [_FLOAT_VECTOR_BASE_RETURN])
        overload_nodes.append(base_overload)

        # Default overload - catches any other subtype -> bpy_prop_array[float]
        default_overload = target_node.deepcopy()
        default_overload.attributes["option"] = "overload"
        self._set_float_vector_size_type(
            default_overload,
            _VECTOR_SIZE_LITERAL_RANGE,
        )
        self._set_return_type(default_overload, [_FLOAT_VECTOR_BASE_RETURN])
        overload_nodes.append(default_overload)

        # Replace the original node with all overloads.
        document.remove(target_node)
        for i, overload in enumerate(overload_nodes):
            document.insert(index + i, overload)

    def _sync_overload_signatures(self, document: nodes.document) -> None:
        """Ensure overload callback/default args match overload return type."""
        func_nodes = find_children(document, FunctionNode)
        for func_node in func_nodes:
            if func_node.attributes.get("option") != "overload":
                continue

            name = func_node.element(NameNode).astext()
            if name not in ("EnumProperty", "FloatVectorProperty"):
                continue

            return_node = func_node.element(FunctionReturnNode)
            if not return_node:
                continue

            dtype_list_node = return_node.element(DataTypeListNode)
            if not dtype_list_node.children:
                continue

            ret_types = [
                self._normalize_list_to_sequence(
                    child.astext().replace("`", "")
                )
                for child in dtype_list_node.children
                if isinstance(child, DataTypeNode)
            ]
            if not ret_types:
                continue
            ret_type_str = " | ".join(ret_types)

            callback_value_type = ret_type_str
            if name == "FloatVectorProperty":
                base_array = "bpy.types.bpy_prop_array[float]"
                if ret_type_str == base_array:
                    callback_value_type = ret_type_str
                else:
                    callback_value_type = f"{ret_type_str} | {base_array}"
                default_arg = self._find_argument(func_node, "default")
                if default_arg is not None:
                    self._set_arg_type(
                        default_arg,
                        [f"{callback_value_type} | None"],
                    )

            tags_arg = self._find_argument(func_node, "tags")
            if tags_arg is not None:
                self._set_arg_type(tags_arg, ["set[str] | None"])

            get_arg = self._find_argument(func_node, "get")
            if get_arg is not None:
                get_arg_type = (
                    "collections.abc.Callable[[_GenericType1], "
                    f"{callback_value_type}] | None"
                )
                self._set_arg_type(
                    get_arg,
                    [get_arg_type],
                )

            set_arg = self._find_argument(func_node, "set")
            if set_arg is not None:
                set_arg_type = (
                    "collections.abc.Callable[[_GenericType1, "
                    f"{callback_value_type}], None] | None"
                )
                self._set_arg_type(
                    set_arg,
                    [set_arg_type],
                )

    # ------------------------------------------------------------------
    # entry points
    # ------------------------------------------------------------------

    def _apply(self, document: nodes.document) -> None:
        module_node = get_first_child(document, ModuleNode)
        if not module_node:
            return

        module_name = module_node.element(NameNode).astext()
        if module_name != "bpy.props":
            return

        self._generate_enum_property_overloads(document)
        self._generate_float_vector_property_overloads(document)
        self._sync_overload_signatures(document)

    @classmethod
    def name(cls) -> str:
        return "bpy_props_overload_generator"

    def apply(self, **kwargs: dict[str, object]) -> None:  # noqa: ARG002
        for document in self.documents:
            self._apply(document)
