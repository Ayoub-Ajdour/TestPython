import os
import subprocess
import requests

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
    # Include original code in the prompt
    try:
        with open("test.py", "r") as f:
            original_code = f.read().strip()
    except Exception as e:
        original_code = ""
        print(f"Warning: Could not read test.py: {str(e)}")

    payload = {
        "model": "meta-llama/llama-3.1-405b-instruct",
        "messages": [
            {"role": "system", "content": "You are a code-fixing assistant. Given the Python error and the original code, provide the complete corrected code with the error fixed and all original functionality preserved. If the original code is incomplete, add a sensible default like 'pass' or restore likely intent (e.g., a return statement)."},
            {"role": "user", "content": f"Original code:\n{original_code}\n\nError:\n{error_log}\n\nReturn the full corrected Python code."}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
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

def commit_and_push():
    """Commits and pushes changes to the repository"""
    try:
        subprocess.run(f"git remote set-url origin https://{github_token}@github.com/Ayoub-Ajdour/TestPython.git", shell=True, check=True)
        subprocess.run("git config --global user.email 'ayoubajdour20@gmail.com'", shell=True, check=True)
        subprocess.run("git config --global user.name 'Ayoub Ajdour'", shell=True, check=True)
        subprocess.run("git add test.py", shell=True, check=True)
        subprocess.run('git commit -m "Auto-fixed build issue"', shell=True, check=True)
        subprocess.run("git push origin main", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error while committing or pushing: {e}")
        raise

# Main execution
error_log = get_last_build_error()
print("Error Log:\n", error_log)
if "No error logs" in error_log or not error_log:
    print("No errors detected.")
    exit(0)

fix_suggestion = suggest_fix_llama3_70(error_log)
print("Suggested Fix:\n", fix_suggestion)

if fix_suggestion:
    if apply_fix(fix_suggestion):
        print("Fix applied. Committing changes...")
        commit_and_push()
    else:
        print("Failed to apply the fix.")
else:
    print("No fix suggested.")
