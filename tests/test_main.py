from pathlib import Path

import pytest

from goodoc.main import app, validate_file


class TestValidateFile:
    def test_returns_none_on_valid_file(self, tmp_path, create_files):
        filename = "doc.docx"
        create_files(tmp_path, {
            filename: None,
        })

        assert validate_file(tmp_path / filename) is None

    def test_returns_error_on_missing_file(self):
        assert validate_file(Path("missing.docx")) is not None

    def test_returns_error_on_unsupported_format(self, tmp_path, create_files):
        filename = "data.txt"
        create_files(tmp_path, {
            filename: None,
        })

        assert validate_file(tmp_path / filename) is not None

    def test_missing_takes_priority_over_format(self):
        assert validate_file(Path("missing.txt")) is not None


class TestCLI:
    def test_file_not_found(self, runner, mock_get_credentials, mock_upload):
        result = runner.invoke(app, ["missing.docx"])

        assert result.exit_code == 1
        assert "File not found" in result.output

    def test_single_file_uploads(self, runner, tmp_path, create_files, mock_get_credentials, mock_upload, mock_browser):
        filename = "doc.docx"
        create_files(tmp_path, {
            filename: None,
        })

        result = runner.invoke(app, [str(tmp_path / filename)])

        assert result.exit_code == 0
        mock_upload.assert_called_once()

    def test_url_printed(self, runner, tmp_path, create_files, mock_get_credentials, mock_upload, mock_browser):
        filename = "doc.docx"
        create_files(tmp_path, {
            filename: None,
        })

        result = runner.invoke(app, [str(tmp_path / filename)])

        assert "https://docs.google.com/doc" in result.output

    def test_browser_opened(self, runner, tmp_path, create_files, mock_get_credentials, mock_upload, mock_browser):
        filename = "doc.docx"
        create_files(tmp_path, {
            filename: None,
        })

        runner.invoke(app, [str(tmp_path / filename)])

        mock_browser.assert_called_once_with("https://docs.google.com/doc")

    @pytest.mark.parametrize("count", [1, 2, 3, 5])
    def test_multiple_files_all_uploaded(
            self,
            runner,
            tmp_path,
            create_files,
            mock_get_credentials,
            mock_upload,
            mock_browser,
            count,
    ):
        structure = {f"doc{i}.docx": None for i in range(count)}
        create_files(tmp_path, structure)
        files = [tmp_path / f"doc{i}.docx" for i in range(count)]

        result = runner.invoke(app, [str(f) for f in files])

        assert result.exit_code == 0
        assert mock_upload.call_count == count

    @pytest.mark.parametrize("count", [2, 3, 5])
    def test_credentials_fetched_once(
            self,
            runner,
            tmp_path,
            create_files,
            mock_get_credentials,
            mock_upload,
            mock_browser,
            count,
    ):
        """get_credentials вызывается один раз независимо от числа файлов."""
        structure = {f"doc{i}.docx": None for i in range(count)}
        create_files(tmp_path, structure)
        files = [tmp_path / f"doc{i}.docx" for i in range(count)]

        runner.invoke(app, [str(f) for f in files])

        mock_get_credentials.assert_called_once()

    def test_no_open_skips_browser(self, runner, tmp_path, create_files, mock_get_credentials, mock_upload, mock_browser):
        filename = "doc.docx"
        create_files(tmp_path, {
            filename: None,
        })

        result = runner.invoke(app, [str(tmp_path / filename), "--no-open"])

        assert result.exit_code == 0
        mock_browser.assert_not_called()

    def test_stops_on_first_missing_file(self, runner, tmp_path, create_files, mock_get_credentials, mock_upload, mock_browser):
        """При отсутствующем файле не загружает следующие."""
        filename = "doc.docx"
        create_files(tmp_path, {
            filename: None,
        })

        result = runner.invoke(app, ["missing.docx", str(tmp_path / filename)])

        assert result.exit_code == 1
        mock_upload.assert_not_called()
        mock_get_credentials.assert_not_called()

    def test_no_auth_on_unsupported_format(self, runner, tmp_path, create_files, mock_get_credentials, mock_upload):
        valid = "doc.docx"
        invalid = "data.txt"
        create_files(tmp_path, {
            valid: None,
            invalid: None,
        })

        result = runner.invoke(app, [
            str(tmp_path / valid),
            str(tmp_path / invalid),
        ])

        assert result.exit_code == 1
        mock_get_credentials.assert_not_called()
