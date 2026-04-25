import unittest
from unittest.mock import patch

from app.schemas.chat import ChatRecommendRequest
from app.services.chat_service import stream_chat_recommendation


class ChatStreamTests(unittest.TestCase):
    @patch("app.services.chat_service.save_chat_exchange")
    @patch(
        "app.services.chat_service.parse_style_text",
        return_value={
            "styles": ["韩系"],
            "scene": "日常",
            "goals": ["显高"],
        },
    )
    def test_stream_emits_meta_chunks_and_done(self, *_):
        request = ChatRecommendRequest(text="想要韩系显高日常穿搭")

        events = list(stream_chat_recommendation(request))

        self.assertEqual(events[0]["event"], "session")
        self.assertEqual(events[-1]["event"], "done")
        self.assertTrue(any(event["event"] == "meta" for event in events))
        self.assertTrue(any(event["event"] == "chunk" for event in events))
        self.assertEqual(
            "".join(event["data"]["content"] for event in events if event["event"] == "chunk"),
            events[-1]["data"]["reply"],
        )
        self.assertEqual(events[0]["data"]["session_id"], events[-1]["data"]["session_id"])


if __name__ == "__main__":
    unittest.main()
