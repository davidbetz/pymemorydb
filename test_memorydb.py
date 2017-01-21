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
    from memorydb import MemoryDb
except:
    from .memorydb import MemoryDb

try:
    import idgen
except:
    from . import idgen

try:
    from hamlet import hamlet
except:
    from .hamlet import hamlet

try:
    import aggregate as aggregate
except:
    from . import aggregate as aggregate

class TestApp(unittest.TestCase):
    def setUp(self):
        self.provider = MemoryDb()

    def test_simple_add_and_dumpdb(self):
        scope = idgen.generate(__name__)
        row_key = idgen.generate(__name__)
        item = { "title": "hello1" }
        self.provider.insert(scope, row_key, item)
        v = self.provider.dumpdb()
        self.assertEqual(v[0]['title'], item['title'])

    def test_simple_add_and_get(self):
        scope = idgen.generate(__name__)
        row_key = idgen.generate(__name__)
        item = { "title": "hello1" }
        self.provider.insert(scope, row_key, item)
        v = self.provider.get(scope, row_key)

    def test_simple_add_change_id_and_get(self):
        scope = idgen.generate(__name__)
        row_key = idgen.generate(__name__)
        new_row_key = idgen.generate(__name__)

        item = { "title": "hello1" }
        self.provider.insert(scope, row_key, item)
        
        p = self.provider.get(scope, row_key)
        self.provider.changeId(p, new_row_key)
        
        v = self.provider.get(scope, new_row_key)
        self.assertEqual(v['title'], item['title'])

    def test_2_adds_and_getAll(self):
        scope = idgen.generate(__name__)
        
        item1 = { "title": "hello1" }
        item2 = { "title": "hello2" }

        self.provider.insert(scope, idgen.generate(__name__), item1)
        self.provider.insert(scope, idgen.generate(__name__), item2)
        
        items = self.provider.getAll(scope)

        self.assertEqual(items[0]['title'], item1['title'])
        self.assertEqual(items[1]['title'], item2['title'])

    def test_add_get_and_update(self):
        scope = idgen.generate(__name__)
        row_key = idgen.generate(__name__)
        
        item = { "title": "hello1" }
        
        self.provider.insert(scope, row_key, item)
        
        v = self.provider.get(scope, row_key)
        
        v['title'] = 'was updated'
        self.provider.update(v)
        
        v = self.provider.get(scope, row_key)
        
        self.assertNotEqual(v['title'], item['title'])
        self.assertEqual(v['title'], 'was updated')

    def test_3_adds_delete_and_getAll(self):
        scope = idgen.generate(__name__)
        row_key = idgen.generate(__name__)
        
        item1 = { "title": "hello1" }
        item2 = { "title": "hello2" }
        item3 = { "title": "hello3" }
        
        self.provider.insert(scope, idgen.generate(__name__), item1),
        self.provider.insert(scope, row_key, item2),
        self.provider.insert(scope, idgen.generate(__name__), item3)
        
        self.provider.delete(scope, row_key)
        
        items = self.provider.getAll(scope)
        
        self.assertEqual(items[0]['title'], item1['title'])
        self.assertEqual(items[1]['title'], item3['title'])

    def test_stats_count(self):
        scope = idgen.generate(__name__)
        row_key = idgen.generate(__name__)

        item1 = { "title": "hello1" }
        item2 = { "title": "frogs" }
        item3 = { "title": "hello3" }

        self.provider.insert(scope, idgen.generate(__name__), item1)
        self.provider.insert(scope, row_key, item2)
        self.provider.insert(scope, idgen.generate(__name__), item3)

        stats = self.provider.stats(scope, aggregate.Count(lambda _: _['title'][0]))

        self.assertGreater(len(stats), 0)
        self.assertGreater(stats[0][1], 0)
        
    def test_stats_avg(self):
        scope = idgen.generate(__name__)
        row_key = idgen.generate(__name__)
        item1 = { "title": "hello1", "value": 10 }
        item2 = { "title": "frogs", "value": 20 }
        item3 = { "title": "hello3", "value": 30 }

        self.provider.insert(scope, idgen.generate(__name__), item1)
        self.provider.insert(scope, row_key, item2)
        self.provider.insert(scope, idgen.generate(__name__), item3)

        stats = self.provider.stats(scope, aggregate.Average(lambda _: _['value']))

        self.assertGreater(stats, 10)
    
    def test_stats_sum(self):
        scope = idgen.generate(__name__)
        row_key = idgen.generate(__name__)
        item1 = { "title": "hello1", "value": 10 }
        item2 = { "title": "frogs", "value": 20 }
        item3 = { "title": "hello3", "value": 30 }

        self.provider.insert(scope, idgen.generate(__name__), item1)
        self.provider.insert(scope, row_key, item2)
        self.provider.insert(scope, idgen.generate(__name__), item3)

        stats = self.provider.stats(scope, aggregate.Sum(lambda _: _['value']))

        self.assertEquals(stats, 60)

    def test_3_adds_and_query(self):
        scope = idgen.generate(__name__)
        row_key = idgen.generate(__name__)
        item1 = { "title": "hello1" }
        item2 = { "title": "frogs" }
        item3 = { "title": "hello3" }
        self.provider.insert(scope, idgen.generate(__name__), item1)
        self.provider.insert(scope, row_key, item2)
        self.provider.insert(scope, idgen.generate(__name__), item3)

        items = self.provider.query(scope, lambda _: _['title'].startswith('h'))
        self.assertEquals(len(items), 2)

    def test_sample_wo_data(self):
        scope = idgen.generate(__name__)
        row_key = idgen.generate(__name__)

        sample = self.provider.sample(scope, 10)

        self.assertEquals(len(sample), 0)
                
    def test_20_adds_and_sample(self):
        scope = idgen.generate(__name__)
        row_key = idgen.generate(__name__)

        promises = []

        for n in range(20):
            self.provider.insert(scope, idgen.generate(__name__), { "title": hamlet(2), "order": n })

        sample = self.provider.sample(scope, 10)

        self.assertEquals(len(sample), 10)
                
    def test_20_adds_and_sample_using_default_size(self):
        scope = idgen.generate(__name__)
        row_key = idgen.generate(__name__)

        promises = []

        for n in range(20):
            self.provider.insert(scope, idgen.generate(__name__), { "title": hamlet(2), "order": n })

        sample = self.provider.sample(scope)

        self.assertEquals(len(sample), 10)

    def test_add_updateall_get(self):
        scope = idgen.generate(__name__)

        row_key1 = idgen.generate(__name__)
        row_key2 = idgen.generate(__name__)
        row_key3 = idgen.generate(__name__)

        item1 = { "title": "hello1" }
        item2 = { "title": "frogs" }
        item3 = { "title": "hello3" }

        self.provider.insert(scope, row_key1, item1)
        self.provider.insert(scope, row_key2, item2)
        self.provider.insert(scope, row_key3, item3)

        item1Copy = self.provider.get(scope, row_key1)
        item2Copy = self.provider.get(scope, row_key2)
        item3Copy = self.provider.get(scope, row_key3)

        item1Copy['text'] = 'updateda'
        item2Copy['text'] = 'updatedb'
        item3Copy['text'] = 'updatedc'
        
        self.provider.updateAll([item1Copy, item2Copy, item3Copy])

        items = self.provider.getAll(scope)

        self.assertEquals(items[2]['text'], item3Copy['text'])
        self.assertEquals(items[1]['text'], item2Copy['text'])
        self.assertEquals(items[0]['text'], item1Copy['text'])

    def test_updateall_no_data_no_error_either(self):
        self.provider.updateAll([])

    def test_stats_error_invalid_aggregate(self):
        scope = idgen.generate(__name__)
        row_key = idgen.generate(__name__)

        item1 = { "title": "hello1" }
        item2 = { "title": "frogs" }
        item3 = { "title": "hello3" }

        self.provider.insert(scope, idgen.generate(__name__), item1)
        self.provider.insert(scope, row_key, item2)
        self.provider.insert(scope, idgen.generate(__name__), item3)

        try:
            stats = self.provider.stats(scope, '')
            self.assertEquals(1 , 0)
        except ValueError as ex:
            self.assertEquals(str(ex), 'aggregate must be of type Aggregate')

    def test_simple_add_and_get_error_bad_row_key_format(self):
        scope = idgen.generate(__name__)
        row_key = idgen.generate(__name__)
        item = { "title": "hello1" }
        self.provider.insert(scope, row_key, item)

        try:
            v = self.provider.get(scope, {})
            self.assertEquals(1 , 0)
        except ValueError as ex:
            self.assertEquals(str(ex), 'parameter after partition_key must be a row_key or an array of row keys')

    def test_get_error_404(self):
        try:
            v = self.provider.get('scope', 'row_key')
            self.assertEquals(1 , 0)
        except ValueError as ex:
            self.assertEquals(int(str(ex)), 404)

    def test_3_adds_and_query_error_bad_expression(self):
        scope = idgen.generate(__name__)
        row_key = idgen.generate(__name__)
        item1 = { "title": "hello1" }
        item2 = { "title": "frogs" }
        item3 = { "title": "hello3" }
        self.provider.insert(scope, idgen.generate(__name__), item1)
        self.provider.insert(scope, row_key, item2)
        self.provider.insert(scope, idgen.generate(__name__), item3)

        try:
            items = self.provider.query(scope, 'asdf')
            self.assertEquals(1 , 0)
        except ValueError as ex:
            self.assertEquals(str(ex), 'expression function is required for query')

    def test_update_error_item_partition_key_missing(self):
        try:
            self.provider.update({})
            self.assertEquals(1 , 0)
        except ValueError as ex:
            self.assertEquals(str(ex), 'item.partition_key is required')

    def test_update_error_item_row_key_missing(self):
        try:
            self.provider.update({ "partition_key": 1 })
            self.assertEquals(1 , 0)
        except ValueError as ex:
            self.assertEquals(str(ex), 'item.row_key is required')

    def test_update_error_404(self):
        try:
            self.provider.update({ "partition_key": 1, "row_key": 1 })
            self.assertEquals(1 , 0)
        except ValueError as ex:
            self.assertEquals(int(str(ex)), 404)

    def test_changeId_error_item_partition_key_missing(self):
        try:
            self.provider.changeId({}, 'asdf')
            self.assertEquals(1 , 0)
        except ValueError as ex:
            self.assertEquals(str(ex), 'item.partition_key is required')

    def test_changeId_error_item_row_key_missing(self):
        try:
            self.provider.changeId({ "partition_key": 1 }, 'asdf')
            self.assertEquals(1 , 0)
        except ValueError as ex:
            self.assertEquals(str(ex), 'item.row_key is required')

    def test_changeId_error_404(self):
        try:
            self.provider.changeId({ "partition_key": 1, "row_key": 1 }, 2)
            self.assertEquals(1 , 0)
        except ValueError as ex:
            self.assertEquals(int(str(ex)), 404)
    
if __name__ == '__main__':
    unittest.main()