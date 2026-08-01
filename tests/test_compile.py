"""Test that all Python files in the project compile without syntax errors."""
import py_compile
import os
import pytest


def get_all_python_files():
    """Collect all .py files in the project (excluding __pycache__ and virtual envs)."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    python_files = []
    exclude_dirs = {'__pycache__', '.git', 'venv', '.venv', 'env', '.env', 'dist', 'build', 'node_modules'}

    for dirpath, dirnames, filenames in os.walk(root):
        # Skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        for fname in filenames:
            if fname.endswith('.py'):
                full_path = os.path.join(dirpath, fname)
                # Skip compiled files
                if not fname.startswith('.') and 'cached' not in full_path:
                    python_files.append(full_path)

    return sorted(python_files)


@pytest.mark.parametrize("py_file", get_all_python_files(), ids=lambda x: os.path.relpath(x, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
def test_python_file_compiles(py_file):
    """Test that a Python file compiles without syntax errors."""
    try:
        py_compile.compile(py_file, doraise=True)
    except py_compile.PyCompileError as e:
        pytest.fail(f"Syntax error in {py_file}: {e.msg} (line {e.lineno})")
    except SyntaxError as e:
        pytest.fail(f"Syntax error in {py_file}: {e.msg} (line {e.lineno})")