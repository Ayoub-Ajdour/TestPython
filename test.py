The error is occurring because Python expects an indented block of code after a function definition. Since there is no code inside the function, Python is throwing an error. 

Here is the corrected code:

```python
def test(a, b):
    pass
```

In this corrected code, I've added the `pass` statement, which is a placeholder when a statement is required syntactically but no execution of code is necessary. This allows the function to be defined without any errors. 

However, please note that in a real-world scenario, you would typically have some code inside the function to perform a specific task. The `pass` statement is usually used as a temporary measure until the actual code is written. 

For example, a more realistic version of the function might look like this:

```python
def test(a, b):
    return a + b
```