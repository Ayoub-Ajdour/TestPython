import os
import subprocess
import requests
import re

# Retrieve GitHub token from environment variable
github_token = os.getenv("GITHUB_TOKEN")
if not github_token:
    print("Error: GITHUB_TOKEN environment variable not set.")
    exit(1)

def get_last_build_error():
    """Reads the last pipeline error log from errors.txt"""
    try:
        with open("errors.txt", "r") as file:
            errors = file.read().strip()
            return errors if errors else "No error logs captured."
    except Exception as e:
        return f"Failed to retrieve error logs: {str(e)}"

def suggest_fix_llama3_70(error_log):
    """Uses OpenRouter's LLaMA 3.1 405B via direct API call"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    api_key = "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"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-site.com",
        "X-Title": "Jenkins Auto-Repair",
    }
    try:
        with open("test.py", "r") as f:
            original_code = f.read().strip()
    except Exception as e:
        original_code = ""
        print(f"Warning: Could not read test.py: {str(e)}")

    payload = {
        "model": "meta-llama/llama-3.1-405b-instruct",
        "messages": [
            {"role": "system", "content": "You are a code-fixing assistant. Given the Python error and the original code, return ONLY the complete corrected Python code with the error fixed and all original functionality preserved. Do not include any explanations, markdown, or extra text—just the raw code. If the code is incomplete, infer the intent (e.g., 'return a + b' for a function with parameters 'a' and 'b') rather than adding 'pass' unless no intent is clear."},
            {"role": "user", "content": f"Original code:\n{original_code}\n\nError:\n{error_log}\n\nReturn only the fixed Python code, nothing else."}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        fix_suggestion = response.json()["choices"][0]["message"]["content"].strip()
        # Post-process to extract just the code (in case model adds extra text)
        # Look for Python code lines, ignoring markdown or prose
        lines = fix_suggestion.splitlines()
        code_lines = [line for line in lines if line.strip() and not line.strip().startswith(("#", "```", "Here", "Explanation"))]
        return "\n".join(code_lines).strip()
    except Exception as e:
        print(f"Error while communicating with OpenRouter: {str(e)}")
        return None

def apply_fix(fix_suggestion):
    """Applies the fix to test.py"""
    try:
        with open("test.py", "w") as f:
            f.write(fix_suggestion)
        return True
    except Exception as e:
        print(f"Failed to apply fix: {str(e)}")
        return False
