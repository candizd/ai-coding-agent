# AI Coding Agent

A small command-line coding agent: you give it a prompt, it plans function calls,
and it inspects and edits files inside a sandboxed working directory until it can
answer.

```
uv run main.py "fix the bug in the calculator's render function" --verbose
```

## Provenance

This started as the **"Build an AI Agent" guided project from [boot.dev](https://boot.dev)**.
The agent loop, the four tool functions, and the `calculator/` sample app are the
course's structure and starter code.

What I changed:

- **Swapped the model provider.** The course uses Google Gemini; this version talks
  to [OpenRouter](https://openrouter.ai) through the OpenAI-compatible SDK, so the
  model is a config value rather than a hard dependency.
- Reworked the agent loop into an explicit bounded iteration (`MAX_ITERATIONS`)
  with a non-zero exit when the budget runs out.
- Tool results are returned as `role: "tool"` messages keyed by `tool_call_id`.

I am keeping the attribution explicit because the architecture is not my design.
What I took from it is how a tool-calling loop actually fits together.

## How it works

```
prompt ──> model ──> tool_calls? ──no──> final answer
             ^                  │
             │                 yes
             └── tool results ──┘        (up to MAX_ITERATIONS rounds)
```

The model never touches the filesystem directly. It can only ask for one of four
functions, and every call is rewritten to run inside `WORKING_DIR`:

| Function | What it does |
| --- | --- |
| `get_files_info` | List a directory: names, sizes, file-or-dir |
| `get_file_content` | Read a file, truncated at `MAX_CHARS` |
| `run_python_file` | Execute a `.py` file with arguments, 30s timeout |
| `write_file` | Create or overwrite a file |

### Containment

`working_directory` is injected by `call_function`, never supplied by the model.
Each function resolves the requested path and refuses it when it escapes:

```python
full_path = os.path.normpath(os.path.join(workdir_abs, file_path))
if os.path.commonpath([workdir_abs, full_path]) != workdir_abs:
    return f'Error: Cannot write to "{file_path}" ... outside the permitted working directory'
```

Tool functions return errors as **strings** rather than raising, so a bad path or a
crashing script becomes something the model can read and recover from instead of
killing the run.

**This is a course exercise, not a hardened sandbox.** The guard is a path-prefix
check: it stops `../` traversal, but a symlink inside the working directory can
still point outside it, and `run_python_file` executes real code with your user's
permissions. Point it at a throwaway directory.

## Setup

Requires Python 3.13 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
cp .env.example .env     # then put your OpenRouter key in it
```

| Variable | Purpose |
| --- | --- |
| `OPENROUTER_API_KEY` | OpenRouter API key |

The target directory is `WORKING_DIR` in `call_function.py`, set to `./calculator`.

## The sample app

`calculator/` is a small expression evaluator with a deliberate bug and some filler
text files. It is the course's fixture — something for the agent to explore, run and
repair.

## Checking the tool functions

The scripts in `tests/` print the output of each function against `calculator/`,
including paths that should be refused:

```bash
uv run tests/test_get_files_info.py
```

These are the course's manual verification scripts, not assertions — you read the
output and judge it. Converting them to real `pytest` cases is the obvious next
step.

## Status

A learning project, finished and left as it is. Published because the containment
pattern and the tool-call loop are worth keeping, not because the design is mine.
