from pathlib import Path

from docutils import nodes

from fake_bpy_module.analyzer.nodes import FunctionNode


def has_overload_mapping_usage(documents: list[nodes.document]) -> bool:
    return any(
        "operator-properties-map" in func_node.attributes
        for doc in documents
        for func_node in doc.findall(FunctionNode)
    )


def generate_overload_mapping_helper(
    output_dir: str,
    output_format: str,
) -> None:
    helper_dir = Path(f"{output_dir}/bpy/stub_internal")
    helper_dir.mkdir(parents=True, exist_ok=True)
    helper_ext = "pyi" if output_format == "pyi" else "py"
    helper_path = helper_dir / f"overload_mapping.{helper_ext}"

    helper_code = (
        "import typing\n\n"
        'P = typing.ParamSpec("P")\n'
        'R = typing.TypeVar("R")\n\n'
        "def overload_mapping(\n"
        "    mapped_parameter_name: str,\n"
        "    operator_properties_by_name: dict[str, type],\n"
        ") -> typing.Callable[[typing.Callable[P, R]], "
        "typing.Callable[P, R]]:\n"
    )
    if output_format == "pyi":
        helper_code += "    ...\n"
    else:
        helper_code += "    return lambda function: function\n"

    with helper_path.open("w", encoding="utf-8", newline="\n") as file:
        file.write(helper_code)


def ensure_stub_internal_reexport(output_dir: str, output_format: str) -> None:
    helper_ext = "pyi" if output_format == "pyi" else "py"
    stub_internal_init = Path(
        f"{output_dir}/bpy/stub_internal/__init__.{helper_ext}"
    )
    export_line = "from . import overload_mapping as overload_mapping\n"
    if not stub_internal_init.exists():
        return

    init_text = stub_internal_init.read_text(encoding="utf-8")
    if export_line.strip() in init_text:
        return

    with stub_internal_init.open("a", encoding="utf-8", newline="\n") as file:
        if not init_text.endswith("\n"):
            file.write("\n")
        file.write(export_line)
