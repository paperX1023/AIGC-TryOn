import unittest

from app.schemas.taxonomy import BodyShape, ShoulderType, WaistType
from app.services.body_service import (
    _classify_body_shape,
    _classify_shoulder_type,
    _classify_waist_type,
)


class BodyAnalysisRuleTests(unittest.TestCase):
    def test_classify_x_shape(self):
        result = _classify_body_shape(
            shoulder_width_px=120,
            waist_width_px=80,
            hip_width_px=118,
        )

        self.assertEqual(result, BodyShape.X)

    def test_classify_o_shape(self):
        result = _classify_body_shape(
            shoulder_width_px=116,
            waist_width_px=110,
            hip_width_px=118,
        )

        self.assertEqual(result, BodyShape.O)

    def test_classify_a_shape(self):
        result = _classify_body_shape(
            shoulder_width_px=96,
            waist_width_px=85,
            hip_width_px=124,
        )

        self.assertEqual(result, BodyShape.A)

    def test_classify_inverted_triangle_shape(self):
        result = _classify_body_shape(
            shoulder_width_px=130,
            waist_width_px=92,
            hip_width_px=106,
        )

        self.assertEqual(result, BodyShape.INVERTED_TRIANGLE)

    def test_classify_h_shape(self):
        result = _classify_body_shape(
            shoulder_width_px=118,
            waist_width_px=102,
            hip_width_px=114,
        )

        self.assertEqual(result, BodyShape.H)

    def test_classify_shoulder_type(self):
        self.assertEqual(_classify_shoulder_type(95, 620), ShoulderType.NARROW)
        self.assertEqual(_classify_shoulder_type(128, 600), ShoulderType.MEDIUM)
        self.assertEqual(_classify_shoulder_type(165, 620), ShoulderType.WIDE)

    def test_classify_waist_type(self):
        self.assertEqual(_classify_waist_type(78, 120, 118), WaistType.DEFINED)
        self.assertEqual(_classify_waist_type(98, 118, 114), WaistType.NORMAL)
        self.assertEqual(_classify_waist_type(112, 116, 118), WaistType.UNDEFINED)


if __name__ == "__main__":
    unittest.main()
