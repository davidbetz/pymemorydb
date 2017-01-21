# MIT License
# Copyright (c) 2017 David Betz
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

class Aggregate():
    def __init__(self):
        pass

    def prepare(self, items):
        if callable(self.logic):
            return map(self.logic, items) or []
        return items


class Count(Aggregate):
    def __init__(self, logic):
        Aggregate.__init__(self)
        self.logic = logic

    def run(self, items):
        results = []
        groups = {}
        for n in self.prepare(items):
            if n not in groups:
                groups[n] = 0
            groups[n] = groups[n] + 1
            
        return sorted(groups.items(), key=lambda _: _[1], reverse=True)


class Average(Aggregate):
    def __init__(self, logic):
        Aggregate.__init__(self)
        self.logic = logic

    def run(self, items):
        return sum(_ for _ in self.prepare(items)) / len(items)


class Sum(Aggregate):
    def __init__(self, logic):
        Aggregate.__init__(self)
        self.logic = logic

    def run(self, items):
        return sum(_ for _ in self.prepare(items))