"""
Tests for avatar upload MIME validation (T-02).

Strict TDD: tests written BEFORE production code.
"""
import io


class TestAvatarMimeValidation:
    """Integration tests for avatar MIME/extension validation."""

    def test_upload_valid_png_succeeds(self, client, disable_auth):
        """GIVEN a valid PNG file WHEN uploaded THEN 200 with avatar_url."""
        content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        response = client.post(
            "/api/profile/avatar",
            files={"file": ("avatar.png", io.BytesIO(content), "image/png")},
        )
        assert response.status_code == 200
        assert "avatar_url" in response.json()

    def test_upload_exe_disguised_as_png_rejected(self, client, disable_auth):
        """GIVEN an EXE file with .png extension WHEN uploaded THEN 400."""
        content = b"MZ\x90\x00" + b"\x00" * 100
        response = client.post(
            "/api/profile/avatar",
            files={"file": ("malicious.png", io.BytesIO(content), "image/png")},
        )
        assert response.status_code == 400
        detail = response.json()["detail"]
        assert "magic" in detail.lower() or "extension" in detail.lower() or "formato" in detail.lower()

    def test_upload_invalid_extension_rejected(self, client, disable_auth):
        """GIVEN a .exe file with valid PNG bytes WHEN uploaded THEN 400."""
        content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        response = client.post(
            "/api/profile/avatar",
            files={"file": ("avatar.exe", io.BytesIO(content), "image/png")},
        )
        assert response.status_code == 400
        detail = response.json()["detail"]
        assert "extension" in detail.lower() or "extensi" in detail.lower() or "formato" in detail.lower()

    def test_upload_jpeg_valid_succeeds(self, client, disable_auth):
        """GIVEN a valid JPEG file WHEN uploaded THEN 200."""
        content = b"\xff\xd8\xff\xe0" + b"\x00" * 100
        response = client.post(
            "/api/profile/avatar",
            files={"file": ("photo.jpg", io.BytesIO(content), "image/jpeg")},
        )
        assert response.status_code == 200

    def test_upload_gif_valid_succeeds(self, client, disable_auth):
        """GIVEN a valid GIF file WHEN uploaded THEN 200."""
        content = b"GIF89a" + b"\x00" * 100
        response = client.post(
            "/api/profile/avatar",
            files={"file": ("anim.gif", io.BytesIO(content), "image/gif")},
        )
        assert response.status_code == 200

    def test_upload_webp_valid_succeeds(self, client, disable_auth):
        """GIVEN a valid WebP file WHEN uploaded THEN 200."""
        content = b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 100
        response = client.post(
            "/api/profile/avatar",
            files={"file": ("img.webp", io.BytesIO(content), "image/webp")},
        )
        assert response.status_code == 200
