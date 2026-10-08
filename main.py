import argparse
import os

from dotenv import load_dotenv
from openai import OpenAI
from config import SYSTEM_PROMPT, MAX_ITERATIONS
from call_function import available_functions, call_function
import json
import sys

def main() -> None:
    parser = argparse.ArgumentParser(description="AI Code Assistant")
    parser.add_argument("user_prompt", type=str, help="Prompt to send to the LLM")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY environment variable not set")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": args.user_prompt},
    ]

    if args.verbose:
        print("User prompt:", args.user_prompt)

    for _ in range(MAX_ITERATIONS):
        final_response = generate_content(client, messages, args.verbose)
        if final_response:
            print("Final response:")
            print(final_response)
            return

    print(f"Maximum iterations ({MAX_ITERATIONS}) reached")
    sys.exit(1)


def generate_content(client: OpenAI, messages: list, flag: bool) -> None:
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
        tools=available_functions,
    )
    if not response.usage:
        raise RuntimeError("API response appears to be malformed")

    if flag:
        print("Prompt tokens:", response.usage.prompt_tokens)
        print("Response tokens:", response.usage.completion_tokens)

    message = response.choices[0].message
    messages.append(message)

    if not message.tool_calls:
        return message.content

    for tool_call in message.tool_calls:
        result_message = call_function(tool_call, flag)
        if not result_message.get("content"):
            raise RuntimeError(f"Empty result from {tool_call.function.name}")
        if flag:
            print(f"-> {result_message['content']}")
        messages.append(result_message)

    return None


if __name__ == "__main__":
    main()
