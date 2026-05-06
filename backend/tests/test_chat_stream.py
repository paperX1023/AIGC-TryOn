import unittest
from unittest.mock import patch

from app.schemas.chat import ChatRecommendRequest
from app.schemas.taxonomy import BodyShape, Gender, GoalTag, LegRatio, SceneTag, ShoulderType, StyleTag, WaistType
from app.services.chat_service import generate_chat_recommendation
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

    @patch("app.services.chat_service.save_chat_exchange")
    @patch(
        "app.services.chat_service.generate_recommendation",
        return_value={
            "recommended_style_direction": "简约通勤男装风",
            "recommended_items": ["高腰直筒裤", "开领衬衫"],
            "reason": "整体会更利落，也能平衡肩部量感。",
        },
    )
    @patch(
        "app.services.chat_service.parse_style_text",
        return_value={
            "styles": [StyleTag.MINIMAL],
            "scene": SceneTag.DAILY,
            "goals": [GoalTag.COMFORT],
        },
    )
    def test_reply_uses_enum_values_instead_of_member_names(self, *_):
        request = ChatRecommendRequest(
            text="我想要简约一点",
            body_context={
                "gender": Gender.MALE,
                "body_shape": BodyShape.INVERTED_TRIANGLE,
                "shoulder_type": ShoulderType.WIDE,
                "waist_type": WaistType.NORMAL,
                "leg_ratio": LegRatio.NORMAL,
            },
        )

        result = generate_chat_recommendation(request)

        self.assertIn("男性别特征", result["reply"])
        self.assertIn("倒三角型体型", result["reply"])
        self.assertIn("宽肩", result["reply"])
        self.assertNotIn("Gender.MALE", result["reply"])
        self.assertNotIn("BodyShape.INVERTED_TRIANGLE", result["reply"])
        self.assertNotIn("ShoulderType.WIDE", result["reply"])


if __name__ == "__main__":
    unittest.main()
