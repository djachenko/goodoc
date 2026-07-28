import pytest
import typer
from unittest.mock import MagicMock

from goodoc.drive import MIME_MAP, Drive


@pytest.fixture
def drive(mock_creds):
    mock_auth = MagicMock()
    mock_auth.get_credentials.return_value = mock_creds
    return Drive(mock_auth)


class TestMimeMap:
    @pytest.mark.parametrize("extension, expected_target", [
        (".docx", "application/vnd.google-apps.document"),
        (".xlsx", "application/vnd.google-apps.spreadsheet"),
        (".pptx", "application/vnd.google-apps.presentation"),
        (".pptm", "application/vnd.google-apps.presentation"),
    ])
    def test_extensions_map_to_google_formats(self, extension, expected_target):
        _, target_mime = MIME_MAP[extension]

        assert target_mime == expected_target


@pytest.mark.usefixtures("mock_drive_build")
class TestUpload:
    def test_unsupported_extension_exits(self, drive, tmp_path, create_files):
        create_files(tmp_path, {"doc.pdf": None})

        with pytest.raises(typer.Exit) as exc_info:
            drive.upload(tmp_path / "doc.pdf")

        assert exc_info.value.exit_code == 1

    @pytest.mark.parametrize("extension", MIME_MAP.keys())
    def test_supported_extension_returns_url(self, drive, extension, tmp_path, create_files):
        create_files(tmp_path, {f"doc{extension}": None})

        assert drive.upload(tmp_path / f"doc{extension}") == "https://docs.google.com/doc"

    @pytest.mark.parametrize("filename", ["DOC.DOCX", "Doc.Docx", "sheet.XLSX"])
    def test_uppercase_extension_accepted(self, drive, filename, tmp_path, create_files):
        create_files(tmp_path, {filename: None})

        assert drive.upload(tmp_path / filename) == "https://docs.google.com/doc"

    def test_creates_with_stem_name_and_target_mime(self, drive, docx_file, mock_drive_build):
        drive.upload(docx_file)

        _, kwargs = mock_drive_build.files.return_value.create.call_args

        assert kwargs["body"]["name"] == "doc"
        assert kwargs["body"]["mimeType"] == "application/vnd.google-apps.document"
