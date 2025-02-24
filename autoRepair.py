import openai
import os
import subprocess

# Retrieve secrets from environment variables
github_token = "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"
openai_api_key = "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"

# Set the OpenAI API key for the session
openai.api_key = openai_api_key  # Use the OpenAI API key from secrets

def get_last_build_error():
    """Reads the last pipeline error log from errors.txt"""
    try:
        with open("errors.txt", "r") as file:
            errors = file.read().strip()
            return errors.split('\n')  # Split errors into a list of individual errors
    except Exception as e:
        return [f"Failed to retrieve error logs: {str(e)}"]

def suggest_fix_llama3(error_log):
    """Uses OpenAI's GPT model to suggest a syntax fix"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use the correct model version
            messages=[{"role": "system", "content": "You are an assistant that fixes code."},
                      {"role": "user", "content": f"Provide a syntax-only fix for this Python error without explanation:\n{error_log}"}]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error while communicating with OpenAI: {str(e)}")
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
        subprocess.run("git remote set-url origin https://{github_token}@github.com/Ayoub-Ajdour/TestPython.git", shell=True, check=True)
        subprocess.run("git config --global user.email 'ayoubajdour20@gmail.com'", shell=True, check=True)
        subprocess.run("git config --global user.name 'Ayoub Ajdour'", shell=True, check=True)
        subprocess.run("git add test.py", shell=True, check=True)
        subprocess.run('git commit -m "Auto-fixed build issue"', shell=True, check=True)
        subprocess.run("git push origin main", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error while committing or pushing: {e}")
        raise  # Re-raise the error to fail the Jenkins pipeline

# Main execution
error_log = get_last_build_error()
print("Error Log:\n", error_log)
if not error_log or "No error logs" in error_log:
    print("No errors detected.")
    exit(0)

# Handle multiple errors
for log in error_log:
    fix_suggestion = suggest_fix_llama3(log)
    print("Suggested Fix:\n", fix_suggestion)

    if fix_suggestion:
        if apply_fix(fix_suggestion):
            print("Fix applied. Committing changes...")
            commit_and_push()
        else:
            print("Failed to apply the fix.")
