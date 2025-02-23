import openai
import os
import subprocess
from openai import OpenAI

def get_last_build_error():
    """Reads the last pipeline error log from errors.txt"""
    try:
        with open("errors.txt", "r") as file:
            errors = file.read().strip()
            return errors if errors else "No error logs captured."
    except Exception as e:
        return f"Failed to retrieve error logs: {str(e)}"

def suggest_fix_llama3(error_log):
    """Uses LLaMA 3.1 via OpenRouter to suggest a syntax fix"""
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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",
    )
    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "http://example.com",  # Replace with your site URL
            "X-Title": "AutoRepair Project",       # Replace with your project name
        },
        model="meta-llama/llama-3.1-405b-instruct",
        messages=[
            {
                "role": "user",
                "content": f"Provide a syntax-only fix for this Python error without explanation:\n{error_log}"
            }
        ]
    )
    return completion.choices[0].message.content

def apply_fix(fix_suggestion):
    """Applies the fix to test.py"""
    try:
        with open("test.py", "w") as f:
            f.write(fix_suggestion)
        return True
    except Exception as e:
        print(f"Failed to apply fix: {str(e)}")
        return False

def commit_and_push():
    """Commits and pushes changes to the repository"""
    subprocess.run("git config --global user.email 'jenkins@example.com'", shell=True)
    subprocess.run("git config --global user.name 'Jenkins AutoFix'", shell=True)
    subprocess.run("git add test.py", shell=True)
    subprocess.run('git commit -m "Auto-fixed build issue"', shell=True)
    subprocess.run("git push origin main", shell=True, check=True)

# Main execution
error_log = get_last_build_error()
print("Error Log:\n", error_log)
if "No error logs" in error_log:
    print("No errors detected.")
    exit(0)

fix_suggestion = suggest_fix_llama3(error_log)
print("Suggested Fix:\n", fix_suggestion)

if apply_fix(fix_suggestion):
    print("Fix applied. Committing changes...")
    commit_and_push()
else:
    print("Failed to apply the fix.")