# functions/get_file_content.py
import os
from config import MAX_CHARS

schema_get_file_content = {
    "type": "function",
    "function": {
        "name": "get_file_content",
        "description": f"Reads and returns the contents of a file relative to the working directory, truncated at {MAX_CHARS} characters",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to read, relative to the working directory",
                },
            },
            "required": ["file_path"],
        },
    },
}


def get_file_content(working_directory: str, file_path: str) -> str:
    try:
        workdir_abs = os.path.abspath(working_directory)
        full_path = os.path.normpath(os.path.join(workdir_abs, file_path))

        if os.path.commonpath([workdir_abs, full_path]) != workdir_abs:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(full_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        with open(full_path, "r") as f:
            content = f.read(MAX_CHARS)
            if f.read(1):
                content += f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'

        return content
    except Exception as e:
        # Tool must never crash the agent; report failures as text
        return f"Error: {e}"
