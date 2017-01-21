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

from random import randint
from time import time
import copy
from functools import reduce
from itertools import groupby
import operator

try:
    import aggregate as aggregate
except:
    from . import aggregate as aggregate

try:
    import text_analysis as text_analysis
except:
    from . import text_analysis as text_analysis

class MemoryDb():
    def __init__(self):
        self.table = []
        self.all_indices = {}

    def resetDatabase(self):
        self.table = []

    def dumpdb(self, *args):
        if len(args) == 0:
            return self.table[:]

        return args(self.table[:])

    def dumpindices(self, *scope):
        if len(scope) == 0:
            return self.all_indices.copy()

        scope = scope[0]
        if scope in self.all_indices:
            return self.all_indices[scope].copy()

    def delete(self, partition_key, row_key):
        self.table = [v for v in self.table if v['partition_key'] != partition_key or v['row_key'] != row_key]

    def insert(self, partition_key, row_key, item):
        item['partition_key'] = partition_key
        item['row_key'] = row_key
        item['timestamp'] = time()
        index_data = self.indexItem(item)
        if index_data is not None:
            item['index_data'] = index_data
        self.table.append(copy.copy(item))

    def get(self, partition_key, param):
        if type(param) is str:
            row_key = param
            items = [v for v in self.table if v['partition_key'] == partition_key and v['row_key'] == row_key]
            if len(items) > 0:
                return items[0]
            else:
                raise ValueError(404)
        elif type(param) is list:
            ids = param[:]
            items = [v for v in self.table if v['partition_key'] == partition_key]
            results = []
            for id in ids:
                results.append([v for v in items if v['row_key'] == id][0])
            return results
        else:
            raise ValueError('parameter after partition_key must be a row_key or an array of row keys')

    def getAll(self, partition_key):
        return sorted([v for v in self.table if v['partition_key'] == partition_key], key=lambda k: k['timestamp'])

    def stats(self, partition_key, agg):
        if not isinstance(agg, aggregate.Aggregate) or not callable(agg.run):
            raise ValueError('aggregate must be of type Aggregate')
        items = [v for v in self.table if v['partition_key'] == partition_key]
        results = agg.run(items)
        return results

    def sample(self, partition_key, count = 10):
        items = [v for v in self.table if v['partition_key'] == partition_key]

        if len(items) == 0:
            return []

        def _sample(count):
            if count == 0:
                return []
            else:
                tmp = _sample(count - 1)
                tmp.append(items[randint(1, len(items) - 1)])
                return tmp
        
        return _sample(count)

    def query(self, partition_key, expression):
        if not callable(expression):
            raise ValueError('expression function is required for query')
        items = [v for v in self.table if v['partition_key'] == partition_key]
        items = sorted(items, key=lambda _: _['ts'] if 'ts' in _ else 0, reverse=True)

        results = [_ for _ in items if all(f(_) for f in [expression])] or []

        return results

    def changeId(self, item, new_id):
        if 'partition_key' not in item:
            raise ValueError('item.partition_key is required')

        if 'row_key' not in item:
            raise ValueError('item.row_key is required')

        if len([v for v in self.table if v['partition_key'] == item["partition_key"] and v['row_key'] == item["row_key"]]) == 0:
            raise ValueError(404)

        self.delete(item['partition_key'], item['row_key'])

        item['row_key'] = new_id

        self.table.append(item)

    def update(self, item):
        if 'partition_key' not in item:
            raise ValueError('item.partition_key is required')

        if 'row_key' not in item:
            raise ValueError('item.row_key is required')

        if len([v for v in self.table if v['partition_key'] == item["partition_key"] and v['row_key'] == item["row_key"]]) == 0:
            raise ValueError(404)

        self.delete(item['partition_key'], item['row_key'])

        self.table.append(item)

    def updateAll(self, items):
        for item in items:
            self.delete(item['partition_key'], item['row_key'])
        for item in items:
            self.table.append(item)

    def indexItem(self, item):
        partition_key = item['partition_key']
        if partition_key not in self.all_indices:
            return

        indices = self.all_indices[partition_key]
        keys = item.keys()
        fields = [_ for _ in keys if _ != 'partition_key' and _ != 'row_key']
        running = {}
        for field in fields:
            if field not in indices:
                continue
            index = indices[field]
            if type(index) is dict and 'weight' in index:
                weight = index['weight']
            else:
                weight = 1
            p = (lambda _ : _[field])(item)
            split = p.strip().split(' ')
            reduced = [(c, len(list(cs)) * weight) for c, cs in groupby(split)]
            for k,v in reduced:
                if k not in running:
                    running[k] = 0
                running[k] = running[k] + v

        results = sorted(running.items(), key=operator.itemgetter(1), reverse=True)
        return results

    def textAnalysis(self, partition_key):
        items = [v for v in self.table if v['partition_key'] == partition_key]

        tokenized_data = {}
        for item in items:
            if 'index_data' not in item:
                continue
            b = item['index_data']
            breaker = 0
            for n, v in b:
                i = 0
                if n not in tokenized_data:
                    tokenized_data[n] = {}
                if v not in tokenized_data[n]:
                    tokenized_data[n][v] = { 'value': item['row_key'] }
                else:
                    value = tokenized_data[n][v]
                    next = value['next'] if 'next' in value else None
                    while next is not None:
                        value = next
                        next = value['next'] if 'next' in value else None
                        breaker = breaker + 1
                        if breaker > 20:
                            break
                    next = { 'value': item['row_key'] }
                    value['next'] = next

        tokenized_data_keys = tokenized_data.keys()
        if len(tokenized_data_keys) == 0:
            return

        result = {}
        for key in tokenized_data_keys:
            if key not in tokenized_data:
                tokenized_data[key] = {}
            key_data = tokenized_data[key]
            if key not in result:
                result[key] = {}
            parent = key_data.copy()
            sum = 0
            numeric_keys = parent.keys()
            for n in numeric_keys:
                value = parent[n]
                base = int(n)
                i = 1
                before = sum
                sum += base
                value = value['next'] if 'next' in value else None
                while value is not None:
                    before = sum
                    sum += base
                    i = i + 1
                    value = value['next'] if 'next' in value else None
            result[key]['sum'] = sum
            result[key]['spread'] = key_data
            
        return text_analysis.FullTextAnalysis(result)

    def textIndex(self, partition_key, desc):
        if partition_key not in self.all_indices:
            indices = {}
            self.all_indices[partition_key] = indices
        indices = self.all_indices[partition_key]
        keys = desc.keys()
        for key in keys:
            indices[key] = desc[key]