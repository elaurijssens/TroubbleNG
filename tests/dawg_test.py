import unittest
from dawg import DAWG

class TestDAWG(unittest.TestCase):
    def setUp(self):
        self.dawg = DAWG()
        self.words = ["car", "cat", "dog", "dogs", "do"]
        for word in sorted(self.words):
            self.dawg.insert(word)
        self.dawg.finish()

    def test_search_existing_words(self):
        self.assertTrue(self.dawg.search("car"))
        self.assertTrue(self.dawg.search("cat"))
        self.assertTrue(self.dawg.search("dog"))
        self.assertTrue(self.dawg.search("dogs"))
        self.assertTrue(self.dawg.search("do"))

    def test_search_non_existing_words(self):
        self.assertFalse(self.dawg.search("cats"))
        self.assertFalse(self.dawg.search("catalog"))
        self.assertFalse(self.dawg.search("ca"))
        self.assertFalse(self.dawg.search("at"))

    def test_add_word(self):
        new_word = "catalog"
        self.dawg.add_word(new_word)
        self.assertTrue(self.dawg.search("catalog"))

    def test_wildcard_search(self):
        self.assertCountEqual(self.dawg.wildcard_search("ca*"), ["car", "cat"])
        self.assertCountEqual(self.dawg.wildcard_search("*og"), ["dog", "dogs"])
        self.assertCountEqual(self.dawg.wildcard_search("ca?"), ["car", "cat"])
        self.assertCountEqual(self.dawg.wildcard_search("do?*"), ["dog", "dogs"])
        self.assertCountEqual(self.dawg.wildcard_search("c*g"), [])
        self.assertCountEqual(self.dawg.wildcard_search("*at*"), ["cat"])

    def test_add_and_search_new_word(self):
        self.dawg.add_word("catalog")
        self.assertTrue(self.dawg.search("catalog"))
        self.assertCountEqual(self.dawg.wildcard_search("ca*"), ["car", "cat", "catalog"])
        self.assertCountEqual(self.dawg.wildcard_search("*og"), ["dog", "dogs", "catalog"])

if __name__ == "__main__":
    unittest.main()
