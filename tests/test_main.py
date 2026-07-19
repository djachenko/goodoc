from pathlib import Path

import pytest
import typer

from goodoc.main import app, validate


class TestValidate:
    def test_passes_on_valid_files(self, tmp_path):
        files = [tmp_path / "a.docx", tmp_path / "b.xlsx"]

        for f in files:
            f.touch()

        validate(files)

    def test_raises_on_missing_file(self, tmp_path):
        existing = tmp_path / "doc.docx"
        existing.touch()

        with pytest.raises(typer.Exit):
            validate([Path("missing.docx"), existing])

    def test_raises_on_unsupported_format(self, tmp_path):
        valid = tmp_path / "doc.docx"
        invalid = tmp_path / "data.txt"
        valid.touch()
        invalid.touch()

        with pytest.raises(typer.Exit):
            validate([valid, invalid])

    def test_missing_checked_before_format(self, tmp_path):
        existing_invalid = tmp_path / "data.txt"
        existing_invalid.touch()

        with pytest.raises(typer.Exit):
            validate([Path("missing.docx"), existing_invalid])


class TestCLI:
    def test_file_not_found(self, runner, mock_get_credentials, mock_upload):
        result = runner.invoke(app, ["nonexistent.docx"])

        assert result.exit_code == 1
        assert "File not found" in result.output

    def test_single_file_uploads(self, runner, tmp_path, mock_get_credentials, mock_upload, mock_browser):
        file = tmp_path / "doc.docx"
        file.touch()

        result = runner.invoke(app, [str(file)])

        assert result.exit_code == 0
        mock_upload.assert_called_once()

    def test_url_printed(self, runner, tmp_path, mock_get_credentials, mock_upload, mock_browser):
        file = tmp_path / "doc.docx"
        file.touch()

        result = runner.invoke(app, [str(file)])

        assert "https://docs.google.com/doc" in result.output

    def test_browser_opened(self, runner, tmp_path, mock_get_credentials, mock_upload, mock_browser):
        file = tmp_path / "doc.docx"
        file.touch()

        runner.invoke(app, [str(file)])

        mock_browser.assert_called_once_with("https://docs.google.com/doc")

    @pytest.mark.parametrize("count", [1, 2, 3, 5])
    def test_multiple_files_all_uploaded(self, runner, tmp_path, mock_get_credentials, mock_upload, mock_browser, count):
        files = [tmp_path / f"doc{i}.docx" for i in range(count)]

        for f in files:
            f.touch()

        result = runner.invoke(app, [str(f) for f in files])

        assert result.exit_code == 0
        assert mock_upload.call_count == count

    @pytest.mark.parametrize("count", [2, 3, 5])
    def test_credentials_fetched_once(self, runner, tmp_path, mock_get_credentials, mock_upload, mock_browser, count):
        """get_credentials вызывается один раз независимо от числа файлов."""
        files = [tmp_path / f"doc{i}.docx" for i in range(count)]

        for f in files:
            f.touch()

        runner.invoke(app, [str(f) for f in files])

        mock_get_credentials.assert_called_once()

    def test_no_open_skips_browser(self, runner, tmp_path, mock_get_credentials, mock_upload, mock_browser):
        file = tmp_path / "doc.docx"
        file.touch()

        result = runner.invoke(app, [str(file), "--no-open"])

        assert result.exit_code == 0
        mock_browser.assert_not_called()

    def test_stops_on_first_missing_file(self, runner, tmp_path, mock_get_credentials, mock_upload, mock_browser):
        """При отсутствующем файле не загружает следующие."""
        existing = tmp_path / "doc.docx"
        existing.touch()

        result = runner.invoke(app, ["missing.docx", str(existing)])

        assert result.exit_code == 1
        mock_upload.assert_not_called()
        mock_get_credentials.assert_not_called()

    def test_no_auth_on_unsupported_format(self, runner, tmp_path, mock_get_credentials, mock_upload):
        valid = tmp_path / "doc.docx"
        invalid = tmp_path / "data.txt"
        valid.touch()
        invalid.touch()

        result = runner.invoke(app, [str(valid), str(invalid)])

        assert result.exit_code == 1
        mock_get_credentials.assert_not_called()
