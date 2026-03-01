from dataclasses import dataclass

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
    FunctionReturnNode,
    ModuleNode,
    NameNode,
)
from fake_bpy_module.analyzer.roles import ClassRef
from fake_bpy_module.utils import find_children, get_first_child

from .transformer_base import TransformerBase


@dataclass
class _ClassInfo:
    fqn: str
    document: nodes.document
    class_node: ClassNode
    module_name: str


class CommonMemberHoister(TransformerBase):
    # --- Comparison helpers (mirrored from DuplicationRemover) ---

    def _is_same_datatype(
        self, dtype_node_1: DataTypeNode, dtype_node_2: DataTypeNode
    ) -> bool:
        return dtype_node_1.to_string() == dtype_node_2.to_string()

    def _is_same_attribute(
        self, attr_node_1: AttributeNode, attr_node_2: AttributeNode
    ) -> bool:
        name_1 = attr_node_1.element(NameNode).astext()
        name_2 = attr_node_2.element(NameNode).astext()
        if name_1 != name_2:
            return False

        dtype_nodes_1 = find_children(
            attr_node_1.element(DataTypeListNode), DataTypeNode
        )
        dtype_nodes_2 = find_children(
            attr_node_2.element(DataTypeListNode), DataTypeNode
        )
        if len(dtype_nodes_1) != len(dtype_nodes_2):
            return False
        for dt1, dt2 in zip(dtype_nodes_1, dtype_nodes_2, strict=True):
            if not self._is_same_datatype(dt1, dt2):
                return False

        return True

    def _is_same_argument(
        self, arg_node_1: ArgumentNode, arg_node_2: ArgumentNode
    ) -> bool:
        name_1 = arg_node_1.element(NameNode).astext()
        name_2 = arg_node_2.element(NameNode).astext()
        if name_1 != name_2:
            return False

        dtype_nodes_1 = find_children(
            arg_node_1.element(DataTypeListNode), DataTypeNode
        )
        dtype_nodes_2 = find_children(
            arg_node_2.element(DataTypeListNode), DataTypeNode
        )
        if len(dtype_nodes_1) != len(dtype_nodes_2):
            return False
        for dt1, dt2 in zip(dtype_nodes_1, dtype_nodes_2, strict=True):
            if not self._is_same_datatype(dt1, dt2):
                return False

        return True

    def _is_same_function_return(
        self, ret_node_1: FunctionReturnNode, ret_node_2: FunctionReturnNode
    ) -> bool:
        dtype_nodes_1 = find_children(
            ret_node_1.element(DataTypeListNode), DataTypeNode
        )
        dtype_nodes_2 = find_children(
            ret_node_2.element(DataTypeListNode), DataTypeNode
        )
        if len(dtype_nodes_1) != len(dtype_nodes_2):
            return False
        for dt1, dt2 in zip(dtype_nodes_1, dtype_nodes_2, strict=True):
            if not self._is_same_datatype(dt1, dt2):
                return False

        return True

    def _is_same_function(
        self, func_node_1: FunctionNode, func_node_2: FunctionNode
    ) -> bool:
        name_1 = func_node_1.element(NameNode).astext()
        name_2 = func_node_2.element(NameNode).astext()
        if name_1 != name_2:
            return False

        func_type_1 = func_node_1.attributes.get("function_type", "")
        func_type_2 = func_node_2.attributes.get("function_type", "")
        if func_type_1 != func_type_2:
            return False

        arg_nodes_1 = find_children(
            func_node_1.element(ArgumentListNode), ArgumentNode
        )
        arg_nodes_2 = find_children(
            func_node_2.element(ArgumentListNode), ArgumentNode
        )
        if len(arg_nodes_1) != len(arg_nodes_2):
            return False
        for a1, a2 in zip(arg_nodes_1, arg_nodes_2, strict=True):
            if not self._is_same_argument(a1, a2):
                return False

        ret_1 = func_node_1.element(FunctionReturnNode)
        ret_2 = func_node_2.element(FunctionReturnNode)
        return self._is_same_function_return(ret_1, ret_2)

    # --- Phase 1: Build global class registry ---

    def _build_class_registry(self) -> dict[str, _ClassInfo]:
        registry: dict[str, _ClassInfo] = {}
        for document in self.documents:
            module_node = get_first_child(document, ModuleNode)
            if module_node is None:
                continue
            module_name = module_node.element(NameNode).astext()
            for class_node in find_children(document, ClassNode):
                class_name = class_node.element(NameNode).astext()
                fqn = f"{module_name}.{class_name}"
                registry[fqn] = _ClassInfo(
                    fqn=fqn,
                    document=document,
                    class_node=class_node,
                    module_name=module_name,
                )
        return registry

    # --- Phase 2: Build parent-children map ---

    def _resolve_base_class_fqn(self, dtype_node: DataTypeNode) -> str | None:
        class_refs = [c for c in dtype_node.children if isinstance(c, ClassRef)]
        if class_refs:
            return class_refs[0].to_string()
        text = dtype_node.to_string()
        if text and text != "object":
            return text
        return None

    def _build_parent_children_map(
        self, registry: dict[str, _ClassInfo]
    ) -> dict[str, list[str]]:
        parent_children: dict[str, list[str]] = {}
        for fqn, info in registry.items():
            base_class_list_node = info.class_node.element(BaseClassListNode)
            for bc_node in find_children(base_class_list_node, BaseClassNode):
                dtype_list_node = bc_node.element(DataTypeListNode)
                for dtype_node in find_children(dtype_list_node, DataTypeNode):
                    parent_fqn = self._resolve_base_class_fqn(dtype_node)
                    if parent_fqn and parent_fqn in registry:
                        parent_children.setdefault(parent_fqn, []).append(fqn)
        return parent_children

    # --- Phase 3: Bottom-up ordering ---

    def _compute_depths(
        self,
        registry: dict[str, _ClassInfo],
        parent_children: dict[str, list[str]],
    ) -> dict[str, int]:
        child_parents: dict[str, list[str]] = {}
        for parent_fqn, children in parent_children.items():
            for child_fqn in children:
                child_parents.setdefault(child_fqn, []).append(parent_fqn)

        depths: dict[str, int] = {}

        def get_depth(fqn: str, visited: set[str] | None = None) -> int:
            if fqn in depths:
                return depths[fqn]
            if visited is None:
                visited = set()
            if fqn in visited:
                return 0
            visited.add(fqn)
            parents = child_parents.get(fqn, [])
            if not parents:
                depths[fqn] = 0
            else:
                depths[fqn] = 1 + max(get_depth(p, visited) for p in parents)
            return depths[fqn]

        for fqn in registry:
            get_depth(fqn)
        return depths

    def _get_processing_order(
        self, parent_children: dict[str, list[str]], depths: dict[str, int]
    ) -> list[str]:
        parents = [
            fqn
            for fqn, children in parent_children.items()
            if len(children) >= 2
        ]
        parents.sort(key=lambda fqn: -depths.get(fqn, 0))
        return parents

    # --- Phase 4: Hoist common members ---

    def _find_common_attributes(
        self,
        parent_fqn: str,
        children_fqns: list[str],
        registry: dict[str, _ClassInfo],
    ) -> list[dict[str, AttributeNode]]:
        parent_info = registry[parent_fqn]
        parent_attr_names = {
            attr.element(NameNode).astext()
            for attr in find_children(
                parent_info.class_node.element(AttributeListNode), AttributeNode
            )
        }

        first_child = registry[children_fqns[0]]
        first_child_attrs = find_children(
            first_child.class_node.element(AttributeListNode), AttributeNode
        )

        attrs_to_hoist: list[dict[str, AttributeNode]] = []
        for candidate_attr in first_child_attrs:
            attr_name = candidate_attr.element(NameNode).astext()
            if attr_name in parent_attr_names:
                continue

            matching: dict[str, AttributeNode] = {
                children_fqns[0]: candidate_attr
            }
            all_match = True
            for other_fqn in children_fqns[1:]:
                other_attrs = find_children(
                    registry[other_fqn].class_node.element(AttributeListNode),
                    AttributeNode,
                )
                found = False
                for other_attr in other_attrs:
                    if self._is_same_attribute(candidate_attr, other_attr):
                        matching[other_fqn] = other_attr
                        found = True
                        break
                if not found:
                    all_match = False
                    break

            if all_match:
                attrs_to_hoist.append(matching)

        return attrs_to_hoist

    def _find_common_functions(
        self,
        parent_fqn: str,
        children_fqns: list[str],
        registry: dict[str, _ClassInfo],
    ) -> list[dict[str, FunctionNode]]:
        parent_info = registry[parent_fqn]
        parent_func_names = {
            func.element(NameNode).astext()
            for func in find_children(
                parent_info.class_node.element(FunctionListNode), FunctionNode
            )
        }

        first_child = registry[children_fqns[0]]
        first_child_funcs = find_children(
            first_child.class_node.element(FunctionListNode), FunctionNode
        )

        funcs_to_hoist: list[dict[str, FunctionNode]] = []
        for candidate_func in first_child_funcs:
            func_name = candidate_func.element(NameNode).astext()
            if func_name in parent_func_names:
                continue

            matching: dict[str, FunctionNode] = {
                children_fqns[0]: candidate_func
            }
            all_match = True
            for other_fqn in children_fqns[1:]:
                other_funcs = find_children(
                    registry[other_fqn].class_node.element(FunctionListNode),
                    FunctionNode,
                )
                found = False
                for other_func in other_funcs:
                    if self._is_same_function(candidate_func, other_func):
                        matching[other_fqn] = other_func
                        found = True
                        break
                if not found:
                    all_match = False
                    break

            if all_match:
                funcs_to_hoist.append(matching)

        return funcs_to_hoist

    def _hoist_common_members(
        self,
        parent_fqn: str,
        parent_children: dict[str, list[str]],
        registry: dict[str, _ClassInfo],
    ) -> None:
        children_fqns = parent_children[parent_fqn]
        parent_info = registry[parent_fqn]

        # Hoist attributes
        common_attrs = self._find_common_attributes(
            parent_fqn, children_fqns, registry
        )
        parent_attr_list = parent_info.class_node.element(AttributeListNode)
        for matching_attrs in common_attrs:
            first_attr = next(iter(matching_attrs.values()))
            new_attr = first_attr.deepcopy()
            parent_attr_list.append_child(new_attr)
            for child_fqn, attr_node in matching_attrs.items():
                child_attr_list = registry[child_fqn].class_node.element(
                    AttributeListNode
                )
                child_attr_list.remove(attr_node)

        # Hoist functions
        common_funcs = self._find_common_functions(
            parent_fqn, children_fqns, registry
        )
        parent_func_list = parent_info.class_node.element(FunctionListNode)
        for matching_funcs in common_funcs:
            first_func = next(iter(matching_funcs.values()))
            new_func = first_func.deepcopy()
            parent_func_list.append_child(new_func)
            for child_fqn, func_node in matching_funcs.items():
                child_func_list = registry[child_fqn].class_node.element(
                    FunctionListNode
                )
                child_func_list.remove(func_node)

    # --- Main entry ---

    @classmethod
    def name(cls) -> str:
        return "common_member_hoister"

    def apply(self, **kwargs: dict) -> None:  # noqa: ARG002
        registry = self._build_class_registry()
        parent_children = self._build_parent_children_map(registry)
        depths = self._compute_depths(registry, parent_children)
        processing_order = self._get_processing_order(parent_children, depths)
        for parent_fqn in processing_order:
            self._hoist_common_members(parent_fqn, parent_children, registry)
