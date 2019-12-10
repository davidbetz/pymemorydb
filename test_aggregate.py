# -*- coding: utf-8 -*-

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

import unittest

try:
    import aggregate as aggregate
except:
    from . import aggregate as aggregate

class TestApp(unittest.TestCase):
    def setUp(self):
        pass

    def test_aggregate_count(self):
        agg = aggregate.Count(lambda _: _['title'][0])
        stats = agg.run([{ "title": "hello1" }, { "title": "frogs" }, { "title": "hello3" }])
        items = dict(stats)
        self.assertEqual(items['h'], 2)
        self.assertEqual(items['f'], 1)
        self.assertGreater(len(stats), 0)
        self.assertGreater(stats[0][1], 0)

    def test_aggregate_avg(self):
        agg = aggregate.Average(lambda _: _['value'])
        stats = agg.run([{ "title": "hello1", "value": 10 }, { "title": "frogs", "value": 20 }, { "title": "hello3", "value": 30 }])
        self.assertEqual(stats, 20)

    def test_aggregate_sum(self):
        agg = aggregate.Sum(lambda _: _['value'])
        stats = agg.run([{ "title": "hello1", "value": 10 }, { "title": "frogs", "value": 20 }, { "title": "hello3", "value": 30 }])
        self.assertEqual(stats, 60)

if __name__ == '__main__':
    unittest.main()