import unittest
from assistant import classify, reply

class AssistantTests(unittest.TestCase):
    def test_price_question(self):
        self.assertEqual(classify("How much does this cost?"),"pricing")
    def test_schedule_question(self):
        self.assertEqual(classify("Can I book an appointment?"),"schedule")
    def test_human_handoff(self):
        intent,text=reply("I need to talk to a person about damage")
        self.assertEqual(intent,"handoff")
        self.assertIn("team member",text)
    def test_unknown_does_not_invent(self):
        intent,text=reply("Tell me something unrelated")
        self.assertEqual(intent,"unknown")
        self.assertIn("not certain",text)

if __name__=="__main__":
    unittest.main()
