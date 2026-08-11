import sys

TOOL_ID = sys.monitoring.DEBUGGER_ID
sys.monitoring.use_tool_id(TOOL_ID, "demo-tracer")

def on_line(code, line_number):
    print(f"line event: {code.co_name} line {line_number}")

sys.monitoring.register_callback(TOOL_ID, sys.monitoring.events.LINE, on_line)

def add(a, b):
    total = a + b
    return total

def noisy():
    x = 1
    y = 2
    return x + y

sys.monitoring.set_local_events(TOOL_ID, add.__code__, sys.monitoring.events.LINE)

add(2, 3)
noisy()          # produces no LINE events at all — never registered for this code object

sys.monitoring.set_local_events(TOOL_ID, add.__code__, 0)
sys.monitoring.free_tool_id(TOOL_ID)
