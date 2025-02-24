import openai
import os
import subprocess

github_token = os.getenv("GITHUB_TOKEN")
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    print("Error: OPENAI_API_KEY not set.")
    exit(1)

openai.api_key = openai_api_key

def get_last_build_error():
    try:
        with open("errors.txt", "r") as file:
            return file.read().strip().split('\n')
    except Exception as e:
        return [f"Failed to retrieve error logs: {str(e)}"]

def suggest_fix_llama3(error_log):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are an assistant that fixes code."},
                      {"role": "user", "content": f"Provide a syntax-only fix for this Python error without explanation:\n{error_log}"}]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error while communicating with OpenAI: {str(e)}")
        return None

def apply_fix(fix_suggestion):
    try:
        with open("test.py", "w") as f:
            f.write(fix_suggestion)
        return True
    except Exception as e:
        print(f"Failed to apply fix: {str(e)}")
        return False

def commit_and_push():
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

error_message = next((line for line in error_log if "SyntaxError" in line or "Error" in line), None)
if not error_message:
    print("No actionable errors detected.")
    exit(0)

print("Processing Error:\n", error_message)
fix_suggestion = suggest_fix_llama3(error_message)
print("Suggested Fix:\n", fix_suggestion)

if fix_suggestion:
    if apply_fix(fix_suggestion):
        print("Fix applied. Committing changes...")
        commit_and_push()
    else:
        print("Failed to apply the fix.")
else:
    print("No fix suggested.")
