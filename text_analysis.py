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

import re

class FullTextAnalysis():
    def __init__(self, data):
        self.data = data

    def dump(self):
        return self.data

    def terms(self):
        return [_ for _ in self.data.keys()]

    def scores(self, text):
        if text not in self.data:
            return None
        return sorted([v for v in self.data[text]['spread'].keys()], reverse=True)

    def top(self, text):
        scores = self.scores(text)
        if scores is None:
            return None
        item = self.data[text]['spread'][scores[0]]
        return item['value']

    def all(self, text):
        scanned = self.scores(text)
        keys = self.data[text]['spread']
        results = []
        for v in keys:
            i = 0
            value = keys[v]
            results.append(value['value'])
            next = value['next'] if 'next' in value else None
            while next is not None:
                value = next
                next = value['next'] if 'next' in value else None
                results.append(value['value'])
            value['next'] = next
        return results

    def filter(self, expression):
        if not callable(expression):
            return []

        filtered = [_ for _ in self.terms() if all(f(_) for f in [expression])] or []
        filtered = sorted(filtered, key=lambda _: _['sum'] if 'sum' in _ else 0, reverse=True)
        
        results = {}
        for key in filtered:
            results[key] = self.data[key]
            
        return results

    def serialize(self, filtered):
        if filtered is None:
            return
        transformed = [{ "p": _, "score": filtered[_]['sum'], "items": filtered[_]['spread'] } for _ in filtered.keys()]
        ids = []
        for a in transformed:
            keys = [int(_) for _ in a['items'].keys()]
            keys = sorted(keys, reverse=True)
            for key in keys:
                value = a['items'][key]
                if value['value'] not in ids:
                    ids.append(value['value'])
                    value = value['next'] if 'next' in value else None
                while value is not None:
                    if value['value'] not in ids:
                        ids.append(value['value'])
                    value = value['next'] if 'next' in value else None

        return ids

    def highlight(self, term, text, render):
        pattern = re.compile("\\b" + term + "\\b")
        replacement = render.replace('{{_}}', term, re.I)
        result = pattern.sub(replacement, text)
        return result