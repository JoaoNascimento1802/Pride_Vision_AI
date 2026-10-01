with open(r"C:\Users\Joaoe\.gemini\antigravity\brain\92dae92a-4968-4a2f-a75b-76ccca570fb5\.system_generated\tasks\task-8655.log", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "ERROR backend\\tests\\test_ai.py" in line:
        print("".join(lines[max(0, i-5):i+30]))
        break
