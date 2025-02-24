import os
import subprocess

github_token = os.getenv("GITHUB_TOKEN")

def get_last_build_error():
    """Reads the last pipeline error log from errors.txt"""
    try:
        with open("errors.txt", "r") as file:
            return file.read().strip().split('\n')
    except Exception as e:
        return [f"Failed to retrieve error logs: {str(e)}"]

def suggest_fix_rule_based(error_log):
    """Rule-based fixer for common Python syntax errors"""
    if "SyntaxError: expected ':'" in error_log:
        return "def test(a, B):"  # Fix missing colon in function definition
    elif "SyntaxError: incomplete input" in error_log or "SyntaxError: unexpected EOF" in error_log:
        # Fix missing closing parenthesis or incomplete line
        try:
            with open("test.py", "r") as f:
                line = f.read().strip()
                if line.startswith("print(") and not line.endswith(")"):
                    return f"{line})"
                elif line.startswith("def ") and not line.endswith(":"):
                    return f"{line}:"
        except Exception:
            return None
    elif "IndentationError" in error_log:
        # Fix basic indentation (assumes 4-space indent)
        try:
            with open("test.py", "r") as f:
                lines = f.readlines()
                fixed_lines = ["    " + line.strip() if line.strip() else line for line in lines]
                return "".join(fixed_lines)
        except Exception:
            return None
    return None  # Return None if no rule matches

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

error_message = next((line for line in error_log if "SyntaxError" in line or "Error" in line), None)
if not error_message:
    print("No actionable errors detected.")
    exit(0)

print("Processing Error:\n", error_message)
fix_suggestion = suggest_fix_rule_based(error_message)
print("Suggested Fix:\n", fix_suggestion)

if fix_suggestion:
    if apply_fix(fix_suggestion):
        print("Fix applied. Committing changes...")
        commit_and_push()
    else:
        print("Failed to apply the fix.")
else:
    print("No fix suggested for this error.")
