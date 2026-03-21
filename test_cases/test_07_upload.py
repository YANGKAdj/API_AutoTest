"""
test_07_upload.py - KYC 文件上传接口测试
覆盖需求：REQ-45 ~ REQ-48
- 合法文件上传成功（JPG / PNG / PDF）
- 非法文件类型（.exe / .zip）被拒绝
- 超大文件（>5MB）被拒绝
- 空文件被拒绝
- 无 Token 被拒绝（鉴权）
"""
import io
import pytest
import requests
from config import BASE_URL


class TestKYCUpload:
    """KYC 身份证件上传接口测试"""

    BASE = f"{BASE_URL}/api/account/6222020000000001/kyc-upload"

    def _post(self, token, filename, content_type, content=b"fake file content"):
        return requests.post(
            self.BASE,
            files={"file": (filename, io.BytesIO(content), content_type)},
            headers={"authorization": token},
        )

    # ── 正向用例 ────────────────────────────────────────
    def test_upload_jpg_success(self, zhang_token):
        """正向：上传合法 JPG 文件"""
        res = self._post(zhang_token, "id_card.jpg", "image/jpeg")
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["status"] == "pending_review"
        assert data["content_type"] == "image/jpeg"

    def test_upload_png_success(self, zhang_token):
        """正向：上传合法 PNG 文件"""
        res = self._post(zhang_token, "id_card.png", "image/png")
        assert res.status_code == 200

    def test_upload_pdf_success(self, zhang_token):
        """正向：上传合法 PDF 文件"""
        res = self._post(zhang_token, "contract.pdf", "application/pdf")
        assert res.status_code == 200

    # ── 异常用例：文件类型 ────────────────────────────────
    def test_upload_exe_rejected(self, zhang_token):
        """异常：上传可执行文件 .exe 被拒"""
        res = self._post(zhang_token, "virus.exe", "application/octet-stream")
        assert res.status_code == 400
        assert "不支持的文件类型" in res.json()["detail"]["msg"]

    def test_upload_zip_rejected(self, zhang_token):
        """异常：上传压缩包 .zip 被拒"""
        res = self._post(zhang_token, "archive.zip", "application/zip")
        assert res.status_code == 400

    # ── 异常用例：文件大小 ────────────────────────────────
    def test_upload_oversized_file_rejected(self, zhang_token):
        """异常：超过 5MB 大小限制被拒"""
        large_content = b"x" * (5 * 1024 * 1024 + 1)  # 5MB + 1 byte
        res = self._post(zhang_token, "big.jpg", "image/jpeg", large_content)
        assert res.status_code == 400
        assert "超过限制" in res.json()["detail"]["msg"]

    def test_upload_empty_file_rejected(self, zhang_token):
        """异常：上传空文件被拒"""
        res = self._post(zhang_token, "empty.jpg", "image/jpeg", b"")
        assert res.status_code == 400
        assert "不能为空" in res.json()["detail"]["msg"]

    # ── 鉴权用例 ─────────────────────────────────────────
    def test_upload_no_token_rejected(self):
        """鉴权：无 Token 上传被拒"""
        res = requests.post(
            self.BASE,
            files={"file": ("test.jpg", io.BytesIO(b"data"), "image/jpeg")},
        )
        assert res.status_code == 401
