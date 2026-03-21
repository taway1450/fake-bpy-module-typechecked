import re

from docutils import nodes

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
    ModuleNode,
    NameNode,
)
from fake_bpy_module.utils import append_child, find_children, get_first_child

from .transformer_base import TransformerBase


class BpyOperatorPropertiesGenerator(TransformerBase):

    @staticmethod
    def _class_name_from_operator_id(operator_id: str) -> str:
        sanitized = re.sub(r"[^0-9a-zA-Z_]", "_", operator_id)
        sanitized = re.sub(r"_+", "_", sanitized).strip("_")
        return f"OperatorProperties_{sanitized}"

    @staticmethod
    def _escaped_literal(value: str) -> str:
        return value.replace("\\", "\\\\").replace("'", "\\'")

    def _get_module_name(self, document: nodes.document) -> str | None:
        module_node = get_first_child(document, ModuleNode)
        if not module_node:
            return None
        return module_node.element(NameNode).astext()

    def _collect_operator_specs(
        self,
    ) -> list[tuple[str, str, list[ArgumentNode]]]:
        specs: list[tuple[str, str, list[ArgumentNode]]] = []

        for document in self.documents:
            module_name = self._get_module_name(document)
            if not module_name or not module_name.startswith("bpy.ops."):
                continue

            module_suffix = module_name[len("bpy.ops.") :]
            function_nodes = find_children(document, FunctionNode)
            for function_node in function_nodes:
                if function_node.attributes.get("function_type") != "function":
                    continue

                func_name = function_node.element(NameNode).astext()
                operator_id = f"{module_suffix}.{func_name}"
                class_name = self._class_name_from_operator_id(operator_id)

                arg_nodes = find_children(
                    function_node.element(ArgumentListNode),
                    ArgumentNode,
                )
                kwonly_args = [
                    arg_node
                    for arg_node in arg_nodes
                    if arg_node.attributes.get("argument_type") == "kwonlyarg"
                ]

                specs.append((operator_id, class_name, kwonly_args))

        specs.sort(key=lambda item: item[0])
        return specs

    def _find_bpy_types_targets(
        self,
    ) -> tuple[
        nodes.document | None,
        ClassNode | None,
        ClassNode | None,
        FunctionNode | None,
    ]:
        bpy_types_document: nodes.document | None = None
        for document in self.documents:
            module_name = self._get_module_name(document)
            if module_name == "bpy.types":
                bpy_types_document = document
                break

        if bpy_types_document is None:
            return None, None, None, None

        operator_properties_class: ClassNode | None = None
        ui_layout_class: ClassNode | None = None
        ui_layout_operator_method: FunctionNode | None = None

        class_nodes = find_children(bpy_types_document, ClassNode)
        for class_node in class_nodes:
            class_name = class_node.element(NameNode).astext()
            if class_name == "OperatorProperties":
                operator_properties_class = class_node
            elif class_name == "UILayout":
                ui_layout_class = class_node

        if ui_layout_class is not None:
            method_nodes = find_children(
                ui_layout_class.element(FunctionListNode), FunctionNode
            )
            for method_node in method_nodes:
                if method_node.element(NameNode).astext() != "operator":
                    continue
                if method_node.attributes.get("option") == "overload":
                    continue
                ui_layout_operator_method = method_node
                break

        return (
            bpy_types_document,
            operator_properties_class,
            ui_layout_class,
            ui_layout_operator_method,
        )

    def _build_operator_properties_class(
        self,
        class_name: str,
        kwonly_args: list[ArgumentNode],
    ) -> ClassNode:
        class_node = ClassNode.create_template()
        class_node.element(NameNode).add_text(class_name)

        base_class_list_node = class_node.element(BaseClassListNode)
        base_class = BaseClassNode.create_template()
        base_class_dtype = DataTypeNode()
        append_child(base_class_dtype, nodes.Text("OperatorProperties"))
        base_class.element(DataTypeListNode).append_child(base_class_dtype)
        base_class_list_node.append_child(base_class)

        attr_list_node = class_node.element(AttributeListNode)
        for arg_node in kwonly_args:
            attr_node = AttributeNode.create_template()
            attr_name = arg_node.element(NameNode).astext()
            attr_node.element(NameNode).add_text(attr_name)

            src_dtype_list = arg_node.element(DataTypeListNode)
            dst_dtype_list = attr_node.element(DataTypeListNode)
            if src_dtype_list.empty():
                dtype_node = DataTypeNode()
                append_child(dtype_node, nodes.Text("typing.Any"))
                dst_dtype_list.append_child(dtype_node)
            else:
                for dtype_node in find_children(src_dtype_list, DataTypeNode):
                    dst_dtype_list.append_child(dtype_node.deepcopy())

            attr_list_node.append_child(attr_node)

        return class_node

    def _build_operator_properties_map_literal(
        self,
        operator_pairs: list[tuple[str, str]],
    ) -> str:
        items = [
            (
                f"'{self._escaped_literal(operator_id)}': "
                f"{return_class_name}"
            )
            for operator_id, return_class_name in operator_pairs
        ]
        return "{" + ", ".join(items) + "}"

    def _apply(self) -> None:
        (
            bpy_types_document,
            operator_properties_class,
            ui_layout_class,
            ui_layout_operator_method,
        ) = self._find_bpy_types_targets()

        if (
            bpy_types_document is None
            or operator_properties_class is None
            or ui_layout_class is None
            or ui_layout_operator_method is None
        ):
            return

        specs = self._collect_operator_specs()
        if not specs:
            return

        existing_class_names = {
            class_node.element(NameNode).astext()
            for class_node in find_children(bpy_types_document, ClassNode)
        }

        insertion_index = (
            bpy_types_document.index(operator_properties_class) + 1
        )
        generated_specs: list[tuple[str, str]] = []
        for operator_id, class_name, kwonly_args in specs:
            unique_class_name = class_name
            suffix = 2
            while unique_class_name in existing_class_names:
                unique_class_name = f"{class_name}_{suffix}"
                suffix += 1

            existing_class_names.add(unique_class_name)
            generated_specs.append((operator_id, unique_class_name))

            class_node = self._build_operator_properties_class(
                unique_class_name, kwonly_args
            )
            bpy_types_document.insert(insertion_index, class_node)
            insertion_index += 1

        operator_map = self._build_operator_properties_map_literal(
            generated_specs
        )
        ui_layout_operator_method.attributes[
            "operator-properties-map"
        ] = operator_map

    @classmethod
    def name(cls) -> str:
        return "bpy_operator_properties_generator"

    def apply(self, **kwargs: dict[str, object]) -> None:  # noqa: ARG002
        self._apply()
