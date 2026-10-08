# functions/run_python_file.py
import os
import subprocess


schema_run_python_file = {
    "type": "function",
    "function": {
        "name": "run_python_file",
        "description": "Executes a Python file relative to the working directory with optional arguments and returns its output",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the Python file to execute, relative to the working directory",
                },
                "args": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional command-line arguments to pass to the Python file",
                },
            },
            "required": ["file_path"],
        },
    },
}

def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
    try:
        workdir_abs_path = os.path.abspath(working_directory)
        full_path = os.path.normpath(os.path.join(workdir_abs_path, file_path))

        if os.path.commonpath([workdir_abs_path, full_path]) != workdir_abs_path:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(full_path):
            return f'Error: "{file_path}" does not exist or is not a regular file'

        if not file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'

        command = ["python", full_path]
        if args:
            command.extend(args)

        completed_process = subprocess.run(
            command,
            cwd=workdir_abs_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        parts = []
        if completed_process.returncode != 0:
            parts.append(f"Process exited with code {completed_process.returncode}")
        if not completed_process.stdout and not completed_process.stderr:
            parts.append("No output produced")
        if completed_process.stdout:
            parts.append(f"STDOUT:\n{completed_process.stdout}")
        if completed_process.stderr:
            parts.append(f"STDERR:\n{completed_process.stderr}")

        return "\n".join(parts)
    except Exception as e:
        # Tool must never crash the agent; report failures as text
        return f"Error: executing Python file: {e}"
