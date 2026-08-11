import sys

def buggy_tracer(frame, event, arg):
    stats = {}
    stats[event] += 1        # KeyError the first time any event is seen -- a bug
    return buggy_tracer

def add(a, b):
    return a + b

sys.settrace(buggy_tracer)
try:
    result = add(2, 3)
    print("result:", result)
except KeyError as e:
    print("KeyError escaped from the traced call:", e)
sys.settrace(None)
print("tracing still active?", sys.gettrace() is not None)
