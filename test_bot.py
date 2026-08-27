"""
Unit tests for Bot Engine and Chatbot Server functionality.
"""

import unittest
import os
import sqlite3
from bot_engine import SmartAssistant, get_bot_reply
import app

class TestBotEngine(unittest.TestCase):

    def test_math_evaluator(self):
        self.assertEqual(SmartAssistant.safe_eval_math("15 * 24"), 360)
        self.assertEqual(SmartAssistant.safe_eval_math("sqrt(144)"), 12.0)
        self.assertEqual(SmartAssistant.safe_eval_math("2^8"), 256)
        self.assertIsNone(SmartAssistant.safe_eval_math("import os"))

    def test_greeting_response(self):
        reply = get_bot_reply("Hello there!", persona="general")
        self.assertIn("Hello", reply)

    def test_code_response(self):
        reply = get_bot_reply("Write a python function to reverse a string", persona="coder")
        self.assertIn("def reverse_string", reply)
        self.assertIn("```python", reply)

    def test_joke_response(self):
        reply = get_bot_reply("Tell me a joke", persona="general")
        self.assertTrue("joke" in reply.lower() or "🐛" in reply or "SQL" in reply)

    def test_database_init(self):
        app.init_db()
        self.assertTrue(os.path.exists(app.DB_FILE))
        conn = sqlite3.connect(app.DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        conn.close()
        self.assertIn("conversations", tables)
        self.assertIn("messages", tables)

if __name__ == "__main__":
    unittest.main()
