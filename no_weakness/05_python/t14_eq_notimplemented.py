class Weird:
    def __eq__(self, other):
        return NotImplemented

w = Weird()
print(w == w)          # falls back to identity when both sides decline
print(w == object())
