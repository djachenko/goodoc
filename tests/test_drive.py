import pytest
import typer

from goodoc.drive import MIME_MAP, upload


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
    def test_unsupported_extension_exits(self, tmp_path, mock_creds):
        file = tmp_path / "doc.pdf"
        file.touch()

        with pytest.raises(typer.Exit) as exc_info:
            upload(file, mock_creds)

        assert exc_info.value.exit_code == 1

    @pytest.mark.parametrize("extension", MIME_MAP.keys())
    def test_supported_extension_returns_url(self, extension, tmp_path, mock_creds):
        file = tmp_path / f"doc{extension}"
        file.touch()

        url = upload(file, mock_creds)

        assert url == "https://docs.google.com/doc"

    @pytest.mark.parametrize("filename", ["DOC.DOCX", "Doc.Docx", "sheet.XLSX"])
    def test_uppercase_extension_accepted(self, filename, tmp_path, mock_creds):
        file = tmp_path / filename
        file.touch()

        assert upload(file, mock_creds) == "https://docs.google.com/doc"

    def test_creates_with_stem_name_and_target_mime(self, tmp_path, mock_creds, mock_drive_build):
        file = tmp_path / "report.docx"
        file.touch()

        upload(file, mock_creds)

        _, kwargs = mock_drive_build.files.return_value.create.call_args

        assert kwargs["body"]["name"] == "report"
        assert kwargs["body"]["mimeType"] == "application/vnd.google-apps.document"
