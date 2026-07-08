import random

def generate_python_traceback() -> str:
    return """Traceback (most recent call last):
  File "/app/main.py", line 42, in <module>
    main()
  File "/app/main.py", line 38, in main
    process_data(data)
  File "/app/processor.py", line 15, in process_data
    raise ValueError("Invalid data format for ID 0x8F9A")
ValueError: Invalid data format for ID 0x8F9A"""

def generate_java_stacktrace() -> str:
    return """Exception in thread "main" java.lang.NullPointerException: Cannot read field "name"
\tat com.example.app.UserService.getUserName(UserService.java:105)
\tat com.example.app.Main.main(Main.java:20)
\tat org.springframework.boot.SpringApplication.run(SpringApplication.java:1234)"""

def generate_js_stacktrace() -> str:
    return """TypeError: Cannot read properties of undefined (reading 'length')
    at calculateSize (/app/src/utils.js:45:10)
    at Object.<anonymous> (/app/src/index.js:10:5)
    at Module._compile (internal/modules/cjs/loader.js:1015:30)"""

def generate_go_panic() -> str:
    return """panic: runtime error: index out of range [5] with length 3

goroutine 1 [running]:
main.processArray(...)
        /app/src/main.go:25
main.main()
        /app/src/main.go:10 +0x39"""

if __name__ == "__main__":
    random.seed(42)
    print("Generating traces...")
    with open("python_trace.txt", "w") as f:
        f.write(generate_python_traceback())
    with open("java_trace.txt", "w") as f:
        f.write(generate_java_stacktrace())
    with open("js_trace.txt", "w") as f:
        f.write(generate_js_stacktrace())
    with open("go_panic.txt", "w") as f:
        f.write(generate_go_panic())
