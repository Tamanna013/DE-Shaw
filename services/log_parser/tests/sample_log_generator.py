import random

def generate_pytest_log(num_tests: int = 50) -> str:
    lines = ["=== test session starts ==="]
    lines.append("platform linux -- Python 3.12.0, pytest-7.4.0")
    lines.append("rootdir: /app")
    lines.append("plugins: xdist-3.3.1")
    
    for i in range(num_tests):
        outcome = random.choices(["PASSED", "FAILED"], weights=[0.9, 0.1])[0]
        lines.append(f"tests/test_module_{i%5}.py::test_function_{i} {outcome} [ {int(i/num_tests*100)}%]")
        
        if outcome == "FAILED":
            lines.append(f"___ test_function_{i} ___")
            lines.append("def test_function():")
            lines.append(">   assert False")
            lines.append("E   AssertionError: assert False")
            lines.append(f"tests/test_module_{i%5}.py:10: AssertionError")
            
    lines.append("=== short test summary info ===")
    lines.append("=== 1 failed, 49 passed in 0.50s ===")
    return "\n".join(lines)

def generate_junit_xml(num_tests: int = 50) -> str:
    lines = ['<?xml version="1.0" encoding="utf-8"?>']
    lines.append(f'<testsuites>')
    lines.append(f'  <testsuite name="pytest" errors="0" failures="1" skipped="0" tests="{num_tests}" time="1.5">')
    
    for i in range(num_tests):
        outcome = random.choices(["PASSED", "FAILED"], weights=[0.9, 0.1])[0]
        time_ms = random.random()
        lines.append(f'    <testcase classname="tests.test_module_{i%5}" name="test_function_{i}" time="{time_ms:.3f}">')
        if outcome == "FAILED":
            lines.append('      <failure message="assert False">AssertionError: assert False\nat tests/test_module.py:10</failure>')
        lines.append('    </testcase>')
        
    lines.append('  </testsuite>')
    lines.append('</testsuites>')
    return "\n".join(lines)

if __name__ == "__main__":
    # Deterministic generation
    random.seed(42)
    print("Generating Pytest Sample...")
    with open("pytest_sample.log", "w") as f:
        f.write(generate_pytest_log(100))
        
    print("Generating JUnit Sample...")
    with open("junit_sample.xml", "w") as f:
        f.write(generate_junit_xml(100))
