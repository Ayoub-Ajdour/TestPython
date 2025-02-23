import openai
import os
import subprocess

def get_last_build_error():
    """Reads the last pipeline error log from errors.txt"""
    try:
        with open("errors.txt", "r") as file:
            errors = file.read().strip()
            return errors if errors else "No error logs captured."
    except Exception as e:
        return f"Failed to retrieve error logs: {str(e)}"

def suggest_fix_llama3(error_log):
    """Uses OpenAI API to suggest a syntax fix for the error"""
    openai.api_key = "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"
    
    try:
        completion = openai.Completion.create(
            model="gpt-3.5-turbo",  # You can use the desired model here
            prompt=f"Provide a syntax-only fix for this Python error without explanation:\n{error_log}",
            max_tokens=100,
            temperature=0.5
        )
        return completion.choices[0].text.strip()
    except Exception as e:
        return f"Error while communicating with OpenAI: {str(e)}"

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
    
    # Add the remote credentials (username/password or token)
    subprocess.run("git remote set-url origin https://<USERNAME>:<TOKEN>@github.com/<USERNAME>/<REPO>.git", shell=True)
    
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
