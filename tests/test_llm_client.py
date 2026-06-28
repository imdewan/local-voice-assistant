import unittest

from local_alexa.llm_client import _clean_reply


class ReplyCleanupTest(unittest.TestCase):
    def test_reply_is_trimmed_to_short_voice_response(self):
        text = " ".join(f"word{i}" for i in range(40))
        reply = _clean_reply(text)
        self.assertLessEqual(len(reply.split()), 28)

    def test_empty_reply_falls_back_to_okay(self):
        self.assertEqual(_clean_reply(""), "Okay.")


if __name__ == "__main__":
    unittest.main()
