import unittest
from pathlib import Path
from minutes import parse,render

class MinutesTests(unittest.TestCase):
    def test_example(self):
        r=parse((Path(__file__).parents[1]/'examples/synthetic_notes.txt').read_text()); self.assertEqual(len(r['decisions']),1); self.assertEqual(len(r['actions']),2); self.assertEqual(r['actions'][0]['line'],6); self.assertEqual(r['actions'][0]['owner'],'Demo analyst'); self.assertIsNone(r['actions'][1]['owner']); self.assertIsNone(r['actions'][1]['due']); self.assertEqual(len(r['unclassified']),1)
    def test_no_inference(self): self.assertEqual(parse('Alex might do this tomorrow.')['actions'],[])
    def test_invalid_due(self):
        r=parse('ACTION: Check | owner=Demo | due=tomorrow'); self.assertIsNone(r['actions'][0]['due']); self.assertTrue(r['warnings'])
    def test_malformed(self):
        r=parse('ACTION: Check | owner=A | owner=B'); self.assertEqual(r['actions'],[]); self.assertEqual(len(r['unclassified']),1)
    def test_evidence(self): self.assertEqual(parse('DECISION: Continue')['decisions'][0]['source'],'DECISION: Continue')
    def test_empty(self): self.assertIn('Not recorded',render(parse('')))
    def test_unknown_tag(self): self.assertEqual(len(parse('IDEA: Maybe proceed')['unclassified']),1)
    def test_duplicate_meta(self):
        r=parse('TITLE: First\nTITLE: Second'); self.assertEqual(r['title']['value'],'First'); self.assertTrue(r['warnings'])
    def test_missing_owner(self): self.assertIn('Unassigned',render(parse('ACTION: Review')))
    def test_escape(self): self.assertNotIn('<script>',render(parse('SUMMARY: <script>')))
