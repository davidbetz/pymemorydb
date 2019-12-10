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
    from hamlet import hamlet, piglet
except:
    from .hamlet import hamlet, piglet

try:
    from beowulf import wiglaf
except:
    from .beowulf import wiglaf

try:
    import aggregate as aggregate
except:
    from . import aggregate as aggregate

class TestApp(unittest.TestCase):
    def setUp(self):
        self.provider = MemoryDb()

    def test_get_tokenized_data_no_indices_set(self):
        scope = idgen.generate(__name__)
        
        self.provider.insert(scope, 'item1', { 'title': 'n n z c c c d d d dddd' })
        self.provider.insert(scope, 'item2', { 'title': 'n n m c c d dddd doodle' })
        self.provider.insert(scope, 'item3', { 'title': 'n n z m m c d d d donkey' })

        analysis = self.provider.textAnalysis(scope)

        self.assertIsNone(analysis)

    def test_get_tokenized_data(self):
        scope = idgen.generate(__name__)
        
        self.provider.textIndex(scope, { 'title': True })
        self.provider.insert(scope, 'item1', { 'title': 'n n z c c c d d d dddd' })
        self.provider.insert(scope, 'item2', { 'title': 'n n m c c d dddd doodle' })
        self.provider.insert(scope, 'item3', { 'title': 'n n z m m c d d d donkey' })

        analysis = self.provider.textAnalysis(scope)
        dump = analysis.dump()

        sample_key = analysis.terms()[0]
        self.assertIsNotNone(sample_key)
        self.assertGreater(len(sample_key), 0)

        dump_single = analysis.dump()[sample_key]
        self.assertIsNotNone(dump_single)
        self.assertGreater(dump_single['sum'], 0)
        self.assertGreater(len(dump_single['spread'].keys()), 0)

        self.assertEqual(dump['c']['spread'][1]['value'], 'item3')
        self.assertEqual(dump['c']['spread'][2]['value'], 'item2')
        self.assertEqual(dump['c']['spread'][3]['value'], 'item1')

        self.assertEqual(dump['m']['spread'][1]['value'], 'item2')
        self.assertEqual(dump['m']['spread'][2]['value'], 'item3')

        self.assertEqual(dump['z']['spread'][1]['value'], 'item1')
        self.assertEqual(dump['z']['spread'][1]['next']['value'], 'item3')

        self.assertEqual(dump['d']['spread'][1]['value'], 'item2')
        self.assertEqual(dump['d']['spread'][3]['value'], 'item1')
        self.assertEqual(dump['d']['spread'][3]['next']['value'], 'item3')

        self.assertEqual(dump['n']['spread'][2]['value'], 'item1')
        self.assertEqual(dump['n']['spread'][2]['next']['value'], 'item2')
        self.assertEqual(dump['n']['spread'][2]['next']['next']['value'], 'item3')

    def test_get_tokenized_data_two_fields(self):
        scope = idgen.generate(__name__)

        self.provider.textIndex(scope, {
            'title': { 'weight': 2 },
            'text': { 'weight': 1 }
        })
        self.provider.insert(scope, 'item1', {
            'title': 'c d d',
            'text': 'n n z c c c d d d d d dddd'
        })
        self.provider.insert(scope, 'item2', {
            'title': 'm m z',
            'text': 'n n m c c d dddd doodle'
        })
        self.provider.insert(scope, 'item3', {
            'title': 'd d d',
            'text': 'n n z m m c d d d donkey'
        })

        analysis = self.provider.textAnalysis(scope)
        dump = analysis.dump()
        
        sample_key = analysis.terms()[0]
        self.assertIsNotNone(sample_key)
        self.assertGreater(len(sample_key), 0)

        dump_single = analysis.dump()[sample_key]
        self.assertIsNotNone(dump_single)
        self.assertGreater(dump_single['sum'], 0)
        self.assertGreater(len(dump_single['spread'].keys()), 0)

        self.assertEqual(dump['c']['spread'][1]['value'], 'item3')
        self.assertEqual(dump['c']['spread'][2]['value'], 'item2')
        self.assertEqual(dump['c']['spread'][5]['value'], 'item1')

        self.assertEqual(dump['m']['spread'][5]['value'], 'item2')
        self.assertEqual(dump['m']['spread'][2]['value'], 'item3')

        self.assertEqual(dump['z']['spread'][1]['value'], 'item1')
        self.assertEqual(dump['z']['spread'][2]['value'], 'item2')
        self.assertEqual(dump['z']['spread'][1]['next']['value'], 'item3')

        self.assertEqual(dump['d']['spread'][9]['value'], 'item1')
        self.assertEqual(dump['d']['spread'][1]['value'], 'item2')
        self.assertEqual(dump['d']['spread'][9]['next']['value'], 'item3')

        self.assertEqual(dump['n']['spread'][2]['value'], 'item1')
        self.assertEqual(dump['n']['spread'][2]['next']['value'], 'item2')
        self.assertEqual(dump['n']['spread'][2]['next']['next']['value'], 'item3')

    def test_get_tokenized_data_terms(self):
        scope = idgen.generate(__name__)
        
        self.provider.textIndex(scope, { 'title': True })
        self.provider.insert(scope, 'item1', { 'title': 'n n z c c c d d d dddd' })
        self.provider.insert(scope, 'item2', { 'title': 'n n m c c d dddd doodle' })
        self.provider.insert(scope, 'item3', { 'title': 'n n z m m c d d d donkey' })

        analysis = self.provider.textAnalysis(scope)

        terms = analysis.terms()

        self.assertIsNotNone(terms)
        self.assertGreater(len(terms[0]), 0)
        self.assertGreater(len(terms), 0)

    def test_get_tokenized_data_scores(self):
        scope = idgen.generate(__name__)

        self.provider.textIndex(scope, { 'title': True })
        self.provider.insert(scope, 'item1', { 'title': 'n n z c c c d d d dddd' })
        self.provider.insert(scope, 'item2', { 'title': 'n n m c c d dddd doodle' })
        self.provider.insert(scope, 'item3', { 'title': 'n n z m m c d d d donkey' })
          
        analysis = self.provider.textAnalysis(scope)
        
        sample_key = 'd'

        scores = analysis.scores(sample_key)

        self.assertEqual(scores[0], 3)
        self.assertEqual(scores[1], 1)

    def test_get_tokenized_data_top(self):
        scope = idgen.generate(__name__)

        self.provider.textIndex(scope, { 'title': True })
        self.provider.insert(scope, 'item1', { 'title': 'n n z c c c d d d dddd' })
        self.provider.insert(scope, 'item2', { 'title': 'n n m c c d dddd doodle' })
        self.provider.insert(scope, 'item3', { 'title': 'n n z m m c d d d donkey' })
          
        analysis = self.provider.textAnalysis(scope)
        
        sample_key = 'd'

        top = analysis.top(sample_key)

        self.assertEqual(top, 'item1')

    def test_get_tokenized_data_all(self):
        scope = idgen.generate(__name__)

        self.provider.textIndex(scope, { 'title': True })
        self.provider.insert(scope, 'item1', { 'title': 'n n z c c c d d d dddd' })
        self.provider.insert(scope, 'item2', { 'title': 'n n m c c d dddd doodle' })
        self.provider.insert(scope, 'item3', { 'title': 'n n z m m c d d d donkey' })
          
        analysis = self.provider.textAnalysis(scope)
        
        sample_key = 'm'

        all = analysis.all(sample_key)

        self.assertEqual(all[0], 'item2')
        self.assertEqual(all[1], 'item3')

    def test_get_tokenized_data_all_chained(self):
        scope = idgen.generate(__name__)

        self.provider.textIndex(scope, { 'title': True })
        self.provider.insert(scope, 'item1', { 'title': 'n n z c c c d d d dddd' })
        self.provider.insert(scope, 'item2', { 'title': 'n n m c c d dddd doodle' })
        self.provider.insert(scope, 'item3', { 'title': 'n n z m m c d d d donkey' })
          
        analysis = self.provider.textAnalysis(scope)
        
        sample_key = 'd'

        all = analysis.all(sample_key)

        self.assertEqual(all[0], 'item2')
        self.assertEqual(all[1], 'item1')
        self.assertEqual(all[2], 'item3')

    def test_get_tokenized_data_filter(self):
        scope = idgen.generate(__name__)

        self.provider.textIndex(scope, { 'title': True })
        self.provider.insert(scope, 'item1', { 'title': 'n n z c c c d d d dddd' })
        self.provider.insert(scope, 'item2', { 'title': 'n n m c c d dddd doodle' })
        self.provider.insert(scope, 'item3', { 'title': 'n n z m m c d d d donkey' })
          
        analysis = self.provider.textAnalysis(scope)

        sample_key = 'd'

        top = analysis.top(sample_key)

        filtered = analysis.filter(lambda p: p.startswith(sample_key))
        filtered_keys = filtered.keys()

        self.assertEqual(filtered['d']['sum'], 7)
        self.assertEqual(filtered['dddd']['sum'], 2)

    def test_get_tokenized_data_scores_top_filter_more_data(self):
        scope = idgen.generate(__name__)

        self.provider.textIndex(scope, { 'title': True })
        for n in range(20):
            self.provider.insert(scope, idgen.generate(__name__), { "title": piglet(400), "order": n })
          
        analysis = self.provider.textAnalysis(scope)
        terms = analysis.terms()
        sample_key = terms[0]
        scores = analysis.scores(sample_key)
        top = analysis.top(sample_key)
        filtered = analysis.filter(lambda p: p.startswith(sample_key[0]))
        filtered_keys = filtered.keys()
        for p in filtered_keys:
            self.assertEqual(p[0], sample_key[0])
            self.assertTrue(p in terms)

    def test_get_tokenized_data_two_indices(self):
        scope = idgen.generate(__name__)

        self.provider.textIndex(scope, { 'title': True })
        self.provider.textIndex(scope, { 'text': True })
        for n in range(20):
            self.provider.insert(scope, idgen.generate(__name__), { "title": piglet(400), "text": wiglaf(400), "order": n })
          
        analysis = self.provider.textAnalysis(scope)
        terms = analysis.terms()
        sample_key = terms[0]
        scores = analysis.scores(sample_key)
        top = analysis.top(sample_key)
        filtered = analysis.filter(lambda p: p.startswith(sample_key[0]))
        filtered_keys = filtered.keys()
        for p in filtered_keys:
            self.assertEqual(p[0], sample_key[0])
            self.assertTrue(p in terms)

    def test_get_tokenized_data_serialize(self):
        scope = idgen.generate(__name__)

        self.provider.textIndex(scope, { 'title': True })
        self.provider.insert(scope, 'item1', { 'title': 'n n z c c c d d d dddd' })
        self.provider.insert(scope, 'item2', { 'title': 'n n m c c d dddd doodle' })
        self.provider.insert(scope, 'item3', { 'title': 'n n z m m c d d d donkey' })
          
        analysis = self.provider.textAnalysis(scope)

        sample_key = 'd'
        top = analysis.top(sample_key)
        
        filtered = analysis.filter(lambda p: p.startswith(sample_key))
        
        serialized = analysis.serialize(filtered)
        
        filtered_keys = filtered.keys()

        self.assertGreater(len(filtered_keys), len(serialized))

        items = self.provider.get(scope, serialized)

        self.assertEqual(len(items), 3)

    def test_get_tokenize_data_highlight(self):
        scope = idgen.generate(__name__)

        self.provider.textIndex(scope, { 'title': True })
        self.provider.insert(scope, 'item1', { 'title': 'n n z c c c d d d dddd' })
        self.provider.insert(scope, 'item2', { 'title': 'n n m c c d dddd doodle' })
        self.provider.insert(scope, 'item3', { 'title': 'n n z m m c d d d donkey' })
          
        analysis = self.provider.textAnalysis(scope)

        sample_key = 'd'

        top = analysis.top(sample_key)

        p = self.provider.get(scope, top)

        highlighted = analysis.highlight(sample_key, p['title'], '<{{_}}>')
        
        self.assertEqual(highlighted, 'n n z c c c <d> <d> <d> dddd')

    def test_dumpindices_for_all(self):
        scope1 = idgen.generate(__name__)
        scope2 = idgen.generate(__name__)

        scope1_index = {
            "title": { "weight": 2 },
            "text": { "weight": 1 }
        }
        scope2_index = {
            "headings": { "weight": 2 }
        }
        self.provider.textIndex(scope1, scope1_index)
        self.provider.textIndex(scope2, scope2_index)

        all = self.provider.dumpindices()
        self.assertEqual(all[scope1], scope1_index)
        self.assertEqual(all[scope2], scope2_index)

    def test_dumpindices_for_single_scope(self):
        scope1 = idgen.generate(__name__)
        scope2 = idgen.generate(__name__)

        scope1_index = {
            "title": { "weight": 2 },
            "text": { "weight": 1 }
        }
        self.provider.textIndex(scope1, scope1_index)
        self.provider.textIndex(scope2, {
            "headings": { "weight": 2 }
        })

        self.assertEqual(self.provider.dumpindices(scope1), scope1_index)

    def test_dumpindices_for_wrong_scope(self):
        self.assertIsNone(self.provider.dumpindices('asdfasdf'))

    #+ edge cases

    def test_get_tokenized_data_filter_with_bad_expression(self):
        scope = idgen.generate(__name__)

        self.provider.textIndex(scope, { 'title': True })
        self.provider.insert(scope, 'item1', { 'title': 'n n z c c c d d d dddd' })
        self.provider.insert(scope, 'item2', { 'title': 'n n m c c d dddd doodle' })
        self.provider.insert(scope, 'item3', { 'title': 'n n z m m c d d d donkey' })
          
        analysis = self.provider.textAnalysis(scope)

        sample_key = 'd'

        top = analysis.top(sample_key)

        filtered = analysis.filter('asdf')
        self.assertEqual(len(filtered), 0)

    def test_get_tokenized_data_top_wuth_bad_key(self):
        scope = idgen.generate(__name__)

        self.provider.textIndex(scope, { 'title': True })
        self.provider.insert(scope, 'item1', { 'title': 'n n z c c c d d d dddd' })
        self.provider.insert(scope, 'item2', { 'title': 'n n m c c d dddd doodle' })
        self.provider.insert(scope, 'item3', { 'title': 'n n z m m c d d d donkey' })
          
        analysis = self.provider.textAnalysis(scope)

        top = analysis.top('asdfasddfasdf')

        self.assertIsNone(top)

if __name__ == '__main__':
    unittest.main()