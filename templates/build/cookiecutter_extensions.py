from jinja2 import pass_context
from jinja2.ext import Extension


class FletExtension(Extension):
    def __init__(self, environment):
        super(FletExtension, self).__init__(environment)
        environment.globals["get_pyproject"] = self.get_pyproject
        environment.filters["indent_widget"] = self.indent_widget
        environment.filters["indent_code"] = self.indent_code

    @pass_context
    def get_pyproject(self, context, setting):
        pyproject = context.get("cookiecutter", {}).get("pyproject", {})

        if not setting:
            return pyproject

        d = pyproject
        for k in setting.split("."):
            d = d.get(k)
            if d is None:
                return None
        return d

    @pass_context
    def indent_widget(self, context, text, indent_level=1):
        """Toggleable indent for widgets. Default false (via cookiecutter indent_widgets)."""
        if not text:
            return text
        try:
            cc = context.get("cookiecutter", {})
            # Check toggle defaults false for additional indent filters
            enabled = cc.get("indent_widgets", False)
            # Also allow pyproject.toml override [tool.flet] indent_widgets
            pyproject = cc.get("pyproject")
            if isinstance(pyproject, dict):
                py_enabled = pyproject.get("tool", {}).get("flet", {}).get("indent_widgets")
                if py_enabled is not None:
                    enabled = py_enabled
            if not enabled:
                return text
            width = None
            if isinstance(pyproject, dict):
                width = pyproject.get("tool", {}).get("flet", {}).get("indent_width")
            if width is None:
                width = cc.get("indent_width", 4)
            width = int(width)
        except Exception:
            width = 4
        indent = " " * (width * indent_level)
        lines = str(text).splitlines()
        return "\n".join(indent + line if line else line for line in lines)

    @pass_context
    def indent_code(self, context, text, width=None):
        """Toggleable indent for share/code. Default false (via indent_share)."""
        if not text:
            return text
        try:
            cc = context.get("cookiecutter", {})
            enabled = cc.get("indent_share", False)
            pyproject = cc.get("pyproject")
            if isinstance(pyproject, dict):
                py_enabled = pyproject.get("tool", {}).get("flet", {}).get("indent_share")
                # Also allow generic indent_code toggle via indent_share
                if py_enabled is not None:
                    enabled = py_enabled
            if not enabled:
                return text
            if width is None:
                if isinstance(pyproject, dict):
                    width = pyproject.get("tool", {}).get("flet", {}).get("indent_width")
                if width is None:
                    width = cc.get("indent_width", 4)
            width = int(width)
        except Exception:
            width = 4
        indent = " " * width
        lines = str(text).splitlines()
        return "\n".join(indent + line if line else line for line in lines)
