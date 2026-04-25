import unittest
from types import SimpleNamespace

from app.schemas.recommend import RecommendRequest
from app.schemas.taxonomy import BodyShape, Gender, GoalTag, LegRatio, SceneTag, ShoulderType, StyleTag, WaistType
from app.services.recommend_service import generate_recommendation
from app.services.style_service import parse_style_text_rule


class StyleAndRecommendationTests(unittest.TestCase):
    def test_rule_parser_normalizes_synonyms(self):
        result = parse_style_text_rule("想要韩风和简洁一点，面试穿得显高又舒服")

        self.assertEqual(result["scene"], SceneTag.INTERVIEW.value)
        self.assertCountEqual(result["styles"], [StyleTag.KOREAN.value, StyleTag.MINIMAL.value])
        self.assertCountEqual(result["goals"], [GoalTag.TALL.value, GoalTag.COMFORT.value])

    def test_recommendation_supports_string_inputs_from_chat_flow(self):
        data = SimpleNamespace(
            gender="女",
            body_shape="H型",
            shoulder_type="中等",
            waist_type="不明显",
            leg_ratio="偏短",
            styles=["韩系", "简约"],
            scene="面试",
            goals=["显高", "显瘦"],
        )

        result = generate_recommendation(data, use_llm_reason=False)

        self.assertEqual(result["recommended_style_direction"], "韩系简约风")
        self.assertIn("高腰直筒裤", result["recommended_items"])
        self.assertIn("简洁西装外套", result["recommended_items"])

    def test_recommendation_supports_typed_request_inputs(self):
        request = RecommendRequest(
            gender=Gender.MALE,
            body_shape=BodyShape.INVERTED_TRIANGLE,
            shoulder_type=ShoulderType.WIDE,
            waist_type=WaistType.NORMAL,
            leg_ratio=LegRatio.LONG,
            styles=[StyleTag.CHINESE, StyleTag.COMMUTE],
            scene=SceneTag.DATE,
            goals=[GoalTag.COMFORT],
        )

        result = generate_recommendation(request, use_llm_reason=False)

        self.assertEqual(result["recommended_style_direction"], "新中式通勤风")
        self.assertTrue(result["recommended_items"])
        self.assertTrue(any(item["name"] == "新中式提花上衣" for item in result["categorized_items"]))

    def test_recommendation_supports_new_body_shape_labels(self):
        request = RecommendRequest(
            gender=Gender.FEMALE,
            body_shape=BodyShape.X,
            shoulder_type=ShoulderType.MEDIUM,
            waist_type=WaistType.DEFINED,
            leg_ratio=LegRatio.NORMAL,
            styles=[StyleTag.KOREAN, StyleTag.SWEET],
            scene=SceneTag.DATE,
            goals=[GoalTag.TALL],
        )

        result = generate_recommendation(request, use_llm_reason=False)

        self.assertTrue(result["recommended_items"])
        self.assertIn("韩系", result["recommended_style_direction"])


if __name__ == "__main__":
    unittest.main()
