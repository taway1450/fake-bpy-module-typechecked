from pathlib import Path

from docutils import nodes

from fake_bpy_module import config
from fake_bpy_module.analyzer.nodes import FunctionNode, TargetFileNode
from fake_bpy_module.utils import get_first_child

from .writers import (
    BaseWriter,
    JsonWriter,
    PyCodeWriter,
    PyInterfaceWriter,
)


def generate(documents: list[nodes.document]) -> None:
    # Create module directories.
    for doc in documents:
        target_filename = get_first_child(doc, TargetFileNode).astext()
        dir_path = (f"{config.get_output_dir()}/"
                    f"{target_filename[:target_filename.rfind('/')]}")
        Path(dir_path).mkdir(parents=True, exist_ok=True)

        # Create py.typed file at the root of modules.
        if target_filename.count("/") == 1:
            filename = f"{dir_path}/py.typed"
            with Path(filename).open(
                    "w", encoding="utf-8", newline="\n") as file:
                file.write("")

    has_operator_mapping_decorator = any(
        "operator-properties-map" in func_node.attributes
        for doc in documents
        for func_node in doc.findall(FunctionNode)
    )

    if has_operator_mapping_decorator:
        helper_dir = Path(f"{config.get_output_dir()}/bpy/stub_internal")
        helper_dir.mkdir(parents=True, exist_ok=True)
        helper_ext = "pyi" if config.get_output_format() == "pyi" else "py"
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
        if config.get_output_format() == "pyi":
            helper_code += "    ...\n"
        else:
            helper_code += "    return lambda function: function\n"

        with helper_path.open("w", encoding="utf-8", newline="\n") as file:
            file.write(helper_code)

    # Generate modules.
    generator: BaseWriter
    if config.get_output_format() == "py":
        generator = PyCodeWriter()
    elif config.get_output_format() == "pyi":
        generator = PyInterfaceWriter()
    elif config.get_output_format() == "json":
        generator = JsonWriter()
    else:
        raise ValueError(
            f"Unsupported output format: {config.get_output_format()}"
        )

    for doc in documents:
        target_filename = get_first_child(doc, TargetFileNode).astext()
        generator.write(f"{config.get_output_dir()}/{target_filename}",
                        doc, config.get_style_format())

    if has_operator_mapping_decorator:
        helper_ext = "pyi" if config.get_output_format() == "pyi" else "py"
        stub_internal_init = Path(
            f"{config.get_output_dir()}/bpy/stub_internal/__init__.{helper_ext}"
        )
        export_line = "from . import overload_mapping as overload_mapping\n"
        if stub_internal_init.exists():
            init_text = stub_internal_init.read_text(encoding="utf-8")
            if export_line.strip() not in init_text:
                with stub_internal_init.open(
                    "a", encoding="utf-8", newline="\n"
                ) as file:
                    if not init_text.endswith("\n"):
                        file.write("\n")
                    file.write(export_line)
