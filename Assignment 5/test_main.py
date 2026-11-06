import unittest
from src.main import split_sentences, score, classify_act, is_pleonastic

class TestAssignment5(unittest.TestCase):
    def test_sentence_split(self):
        self.assertEqual(len(split_sentences("Ravi came. He left.")), 2)
    def test_measurement(self):
        s = score({"It@S2":"server_1", "He@S4":"Ravi", "bad":"x"})
        self.assertAlmostEqual(s["precision"], 2/3)
    def test_dialog_act(self):
        self.assertEqual(classify_act("Could you give me your ID?"), "REQUEST")
    def test_pleonastic_it(self):
        self.assertTrue(is_pleonastic("It is raining.", "It"))

if __name__ == "__main__":
    unittest.main()
