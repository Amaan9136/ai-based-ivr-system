import json
import re
from helpers.llm import generate_response

<<<<<<< HEAD

def fix_malformed_json(output: str) -> dict | None:
    try:
        # Remove known prefixes like `[Raw LLM Output]`
        output = re.sub(r'^\[.*?\]\s*', '', output)

        # Strip anything before first opening brace
=======
def fix_malformed_json(output: str) -> dict | None:
    try:
        # Strip everything before the first curly brace
>>>>>>> master
        start_index = output.find('{')
        if start_index == -1:
            return None
        json_str = output[start_index:]

<<<<<<< HEAD
        # Replace single quotes with double quotes carefully
        json_str = json_str.replace("'", '"')

        # Remove trailing commas before closing } or ]
        json_str = re.sub(r',\s*([}\]])', r'\1', json_str)

        # Fix improperly joined keys (missing comma between fields)
        json_str = re.sub(
            r'("new_response"\s*:\s*".*?)(?<!\\)"\s*("old_response_summary"\s*:\s*")',
            r'\1", \2',
=======
        # Fix common issues
        json_str = json_str.replace("'", '"')  # single to double quotes
        json_str = re.sub(r',\s*([}\]])', r'\1', json_str)  # remove trailing commas
        json_str = re.sub(
            r'("new_response"\s*:\s*".+?")\s*("old_response_summary"\s*:\s*")',
            r'\1, \2',
>>>>>>> master
            json_str,
            flags=re.DOTALL
        )

<<<<<<< HEAD
        # Balance double quotes
=======
        # Balance quotes
>>>>>>> master
        if json_str.count('"') % 2 != 0:
            json_str += '"'

        # Balance braces
        open_braces = json_str.count('{')
        close_braces = json_str.count('}')
        if close_braces < open_braces:
            json_str += '}' * (open_braces - close_braces)

        # Remove anything after the last closing brace
        last_closing = json_str.rfind('}')
        if last_closing != -1:
            json_str = json_str[:last_closing + 1]

        parsed = json.loads(json_str)

<<<<<<< HEAD
        if not isinstance(parsed, dict):
            print("[Fix Attempt] Parsed JSON is not a dict.")
            return None

        # Ensure required keys
=======
        # Ensure required keys exist
>>>>>>> master
        if not all(key in parsed for key in ["new_response", "old_response_summary"]):
            print("[Fix Attempt] JSON is missing required keys.")
            return None

        return parsed

    except Exception as e:
        print(f"[Fix Attempt] JSON still invalid: {e}")
        return None


def chat_with_history(
    role: str = "Normal Chatbot",
    prompt: str = "",
    old_summary: str = "has no chat summary, generate from now",
    additional_instructions: str = "No Additional Instructions Provided"
) -> dict:
    instruction = f"""
Role: {role}

Task:
1. Generate a helpful response to the user's latest message below.
2. Update the overall chat summary by including the new message and your response, and re-summarizing the full conversation so far.

Rules:
- Output only a valid JSON object.
- JSON must include exactly two keys:
  • "new_response": Your plain text reply to the user.
  • "old_response_summary": A rewritten summary of the *entire* chat so far, including this latest message and response.
- Do NOT include usernames, prefixes like 'User:' or 'Bot:', markdown, or formatting.
- Summary should be brief, natural, and cumulative — avoid repeating previous summaries word-for-word.

Example:
{{
  "new_response": "Sure, I can help with that. What do you need?",
  "old_response_summary": "The user greeted the assistant and asked for help. The assistant offered support."
}}

Additional Instructions:
{additional_instructions}

Current chat summary:
{old_summary}

User's new message:
{prompt}
"""

    try:
        output = generate_response(instruction).strip()
        print("[Raw LLM Output]", output)

        # Try direct parse
        try:
            parsed = json.loads(output)
            if all(k in parsed for k in ["new_response", "old_response_summary"]):
                return parsed
            else:
                print("[Warning] Parsed JSON missing keys. Attempting fix.")

        except json.JSONDecodeError:
            print("[Warning] Raw output is not valid JSON. Attempting to fix.")

        # Try fixing malformed JSON
        fixed = fix_malformed_json(output)
        if fixed:
            return fixed

        raise ValueError("No valid JSON could be parsed.")

    except Exception as e:
        print(f"[chat_with_history Error] {e}")
        return {
            "new_response": "Sorry, I couldn't process that properly.",
            "old_response_summary": old_summary
        }
