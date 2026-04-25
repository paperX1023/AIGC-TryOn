import unittest

from app.services.wardrobe_service import (
    DEFAULT_CLOTH_SOURCE_DIR,
    detect_clothing_image,
    list_wardrobe_items,
    resolve_wardrobe_item,
)


class WardrobeServiceTests(unittest.TestCase):
    def test_default_wardrobe_items_are_available(self):
        if not DEFAULT_CLOTH_SOURCE_DIR.exists():
            self.skipTest("default cloth samples are not available")

        items = list_wardrobe_items()

        self.assertTrue(items)
        self.assertTrue(all(item.source == "default" for item in items))
        self.assertTrue(all(item.image_url.startswith("/uploads/wardrobe/default/") for item in items))

    def test_default_wardrobe_item_can_be_resolved_for_tryon(self):
        if not DEFAULT_CLOTH_SOURCE_DIR.exists():
            self.skipTest("default cloth samples are not available")

        item = resolve_wardrobe_item("default-04469", user_id=None)

        self.assertEqual(item.id, "default-04469")
        self.assertEqual(item.source, "default")
        self.assertTrue(item.image_path)

    def test_clothing_detection_accepts_sample_cloth_image(self):
        sample_path = DEFAULT_CLOTH_SOURCE_DIR / "04469_00.jpg"
        if not sample_path.exists():
            self.skipTest("sample cloth image is not available")

        result = detect_clothing_image(str(sample_path))

        self.assertTrue(result.passed)
        self.assertGreaterEqual(result.score, 0.75)


if __name__ == "__main__":
    unittest.main()
