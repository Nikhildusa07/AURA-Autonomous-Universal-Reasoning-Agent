from backend.app.core.autonomous_executor import autonomous_executor


print("\n========== REAL EXECUTION TEST ==========")


# -------------------------------------------------
# 1. Calculator
# -------------------------------------------------

calculator_result = autonomous_executor.execute(
    "Calculate 1500 multiplied by 4."
)

print("\nCalculator:")
print(calculator_result)


# -------------------------------------------------
# 2. Web Research
# -------------------------------------------------

research_result = autonomous_executor.execute(
    "Find the official FastAPI documentation."
)

print("\nWeb Research:")
print(research_result)


# -------------------------------------------------
# 3. Validation
# -------------------------------------------------

calculator_success = (
    calculator_result["success"]
    and calculator_result["tool"] == "calculator"
    and calculator_result["selection_method"] == "local_rule"
    and calculator_result["execution"]["result"]["result"] == 6000
)

research_success = (
    research_result["success"]
    and research_result["tool"] == "web_research"
    and research_result["selection_method"] == "local_rule"
    and research_result["execution"]["result"]["count"] > 0
)


print("\n========== TEST RESULT ==========")

if calculator_success and research_success:
    print("REAL TOOL EXECUTION TEST PASSED")
else:
    print("REAL TOOL EXECUTION TEST FAILED")