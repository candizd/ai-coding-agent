# functions/get_files_info.py
import os


schema_get_files_info = {
    "type": "function",
    "function": {
        "name": "get_files_info",
        "description": "Lists files in a specified directory relative to the working directory, providing file size and directory status",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory path to list files from, relative to the working directory (default is the working directory itself)",
                },
            },
        },
    },
}


def get_files_info(working_directory: str, directory: str = ".") -> str:
    try:
        workdir_abs_path = os.path.abspath(working_directory)
        full_path = os.path.normpath(os.path.join(workdir_abs_path, directory))

        if os.path.commonpath([workdir_abs_path, full_path]) != workdir_abs_path:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        if not os.path.isdir(full_path):
            return f'Error: "{directory}" is not a directory'

        contents = []
        for item in os.listdir(full_path):
            item_path = os.path.join(full_path, item)
            contents.append(
                f"- {item}: file_size={os.path.getsize(item_path)} bytes, "
                f"is_dir={os.path.isdir(item_path)}"
            )

        return "\n".join(contents)
    except Exception as e:
        return f"Error: {e}"
