import unittest
from src.main import parse_articles

SAMPLE_HTML = '''<html><body>
<h2><a href="https://example.com/a">First Article</a></h2>
<h3><a href="https://example.com/b">Second Article</a></h3>
</body></html>'''

class TestParse(unittest.TestCase):
    def test_parse_articles(self):
        arts = parse_articles(SAMPLE_HTML)
        self.assertEqual(len(arts), 2)
        self.assertEqual(arts[0].title, 'First Article')
        self.assertEqual(arts[0].url, 'https://example.com/a')

if __name__ == '__main__':
    unittest.main()
