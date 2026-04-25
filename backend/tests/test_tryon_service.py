import unittest

from app.services import tryon_service


class TryonServiceTests(unittest.TestCase):
    def test_resolve_remote_result_url_from_relative_path(self):
        original_base_url = tryon_service.settings.tryon_api_base_url
        try:
            tryon_service.settings.tryon_api_base_url = "http://remote-host:6006"
            result = tryon_service._resolve_remote_result_url(
                {"result_image_path": "/results/demo.jpg"}
            )
            self.assertEqual(result, "http://remote-host:6006/results/demo.jpg")
        finally:
            tryon_service.settings.tryon_api_base_url = original_base_url

    def test_resolve_remote_result_url_prefers_explicit_url(self):
        original_base_url = tryon_service.settings.tryon_api_base_url
        try:
            tryon_service.settings.tryon_api_base_url = "http://remote-host:6006"
            result = tryon_service._resolve_remote_result_url(
                {
                    "result_image_url": "https://cdn.example.com/result.jpg",
                    "result_image_path": "/results/demo.jpg",
                }
            )
            self.assertEqual(result, "https://cdn.example.com/result.jpg")
        finally:
            tryon_service.settings.tryon_api_base_url = original_base_url


if __name__ == "__main__":
    unittest.main()
