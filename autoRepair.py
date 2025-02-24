import os
import subprocess
from openai import OpenAI

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
    """Uses OpenRouter's LLaMA 3.1 405B to suggest a syntax fix"""
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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",
    )
    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://your-site.com",
                "X-Title": "Jenkins Auto-Repair",
            },
            model="meta-llama/llama-3.1-405b-instruct",
            messages=[
                {"role": "system", "content": "You are a code-fixing assistant. Provide only the corrected syntax for the given Python error, no explanations."},
                {"role": "user", "content": f"Fix this Python error:\n{error_log}"}
            ]
        )
        return completion.choices[0].message.content.strip()
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
