import time
from pynput.keyboard import Key, Controller

class AutoTyper:

    def __init__(self):
        self.controller = Controller()
        self.waittime = 0.01

    def type(self, character):
        self.controller.press(character)
        self.controller.release(character)
        self.wait()

    def indent(self):
        self.controller.press(" ")
        self.controller.release(" ")
        self.wait()
        self.controller.press(" ")
        self.controller.release(" ")
        self.wait()

    def unident(self):
        self.controller.press(Key.backspace)
        self.controller.release(Key.backspace)
        self.wait()
        self.controller.press(Key.backspace)
        self.controller.release(Key.backspace)
        self.wait()

    def enter(self):
        self.controller.press(Key.enter)
        self.wait()

    def pressdelete(self):
        self.controller.press(Key.delete)
        self.controller.release(Key.delete)
        self.wait()

    def wait(self):
        time.sleep(self.waittime)

    def tab(self, n=1):
        while n > 0:
            self.controller.press(Key.tab)
            n -= 1
            self.wait()

    def shiftenter(self):
        self.controller.press(Key.shift_l)
        self.controller.press(Key.enter)
        self.wait()
        self.controller.release(Key.enter)
        self.controller.release(Key.shift_l)
        self.wait()

    def shifttab(self):
        self.controller.press(Key.shift_l)
        self.controller.press(Key.tab)
        time.sleep(0.05)
        self.controller.release(Key.tab)
        self.controller.release(Key.shift_l)
        self.wait()

    def backspace(self):
        self.controller.press(Key.backspace)
        self.controller.release(Key.backspace)
        self.wait()

    def end(self):
        self.controller.press(Key.end)
        self.controller.release(Key.end)
        self.wait()

    def write(self, lines):
        currentIndentLevel = 0
        for line in lines:
            if line == "unindent":
                self.unident()
                continue
            startlen = len(line)
            endlen = len(line.lstrip())
            indentlevel = int((startlen - endlen) / 2)
            if indentlevel < currentIndentLevel:
                self.unident()
                currentIndentLevel -= 1
            elif indentlevel > currentIndentLevel:
                self.indent()
                currentIndentLevel += 1
            self.linewrite(line)
            self.shiftenter()

    def linewrite(self, line):
        self.controller.type(line)