"""Tests for fireworks.training.sdk.path — cloud-aware path utilities."""

from __future__ import annotations

import io
import os
import tempfile
from unittest import mock

import pytest

from fireworks.training.sdk.path import (
    cloud_join,
    is_cloud_path,
    open_path,
    require_fsspec,
)


# -- is_cloud_path ------------------------------------------------------------

class TestIsCloudPath:
    def test_gs(self):
        assert is_cloud_path("gs://bucket/file.jsonl") is True

    def test_s3(self):
        assert is_cloud_path("s3://bucket/file.jsonl") is True

    def test_local(self):
        assert is_cloud_path("/tmp/data.jsonl") is False

    def test_relative(self):
        assert is_cloud_path("data/train.jsonl") is False

    def test_http(self):
        assert is_cloud_path("https://example.com/data.jsonl") is False


# -- require_fsspec ------------------------------------------------------------

class TestRequireFsspec:
    def test_raises_when_unavailable(self):
        with mock.patch("fireworks.training.sdk.path.FSSPEC_AVAILABLE", False):
            with pytest.raises(ImportError, match="fsspec is required"):
                require_fsspec()

    def test_noop_when_available(self):
        with mock.patch("fireworks.training.sdk.path.FSSPEC_AVAILABLE", True):
            require_fsspec()


# -- cloud_join ----------------------------------------------------------------

class TestCloudJoin:
    def test_gs_join(self):
        assert cloud_join("gs://bucket/dir", "sub", "file.jsonl") == "gs://bucket/dir/sub/file.jsonl"

    def test_gs_trailing_slash(self):
        assert cloud_join("gs://bucket/dir/", "file.jsonl") == "gs://bucket/dir/file.jsonl"

    def test_s3_join(self):
        assert cloud_join("s3://bucket", "key") == "s3://bucket/key"

    def test_local_join(self):
        result = cloud_join("/tmp/logs", "checkpoints.jsonl")
        assert result == os.path.join("/tmp/logs", "checkpoints.jsonl")

    def test_local_with_multiple_parts(self):
        result = cloud_join("/tmp", "a", "b")
        assert result == os.path.join("/tmp", "a", "b")


# -- open_path -----------------------------------------------------------------

class TestOpenPath:
    def test_local_read(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
            tmp.write("hello\nworld\n")
            tmp_path = tmp.name

        try:
            with open_path(tmp_path) as f:
                lines = f.readlines()
            assert lines == ["hello\n", "world\n"]
        finally:
            os.unlink(tmp_path)

    def test_local_write(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            with open_path(tmp_path, "w") as f:
                f.write("written")
            with open(tmp_path) as f:
                assert f.read() == "written"
        finally:
            os.unlink(tmp_path)

    def test_gs_delegates_to_fsspec(self):
        fake_fh = io.StringIO("cloud data")
        mock_cm = mock.MagicMock()
        mock_cm.__enter__ = mock.Mock(return_value=fake_fh)
        mock_cm.__exit__ = mock.Mock(return_value=False)

        with mock.patch("fireworks.training.sdk.path.fsspec") as mock_fsspec, \
             mock.patch("fireworks.training.sdk.path.FSSPEC_AVAILABLE", True):
            mock_fsspec.open.return_value = mock_cm
            with open_path("gs://bucket/file.txt") as f:
                content = f.read()

        assert content == "cloud data"
        mock_fsspec.open.assert_called_once_with("gs://bucket/file.txt", "r")

    def test_s3_delegates_to_fsspec(self):
        fake_fh = io.StringIO("s3 data")
        mock_cm = mock.MagicMock()
        mock_cm.__enter__ = mock.Mock(return_value=fake_fh)
        mock_cm.__exit__ = mock.Mock(return_value=False)

        with mock.patch("fireworks.training.sdk.path.fsspec") as mock_fsspec, \
             mock.patch("fireworks.training.sdk.path.FSSPEC_AVAILABLE", True):
            mock_fsspec.open.return_value = mock_cm
            with open_path("s3://bucket/file.txt") as f:
                content = f.read()

        assert content == "s3 data"
        mock_fsspec.open.assert_called_once_with("s3://bucket/file.txt", "r")

    def test_cloud_path_without_fsspec_raises(self):
        with mock.patch("fireworks.training.sdk.path.FSSPEC_AVAILABLE", False):
            with pytest.raises(ImportError, match="fsspec is required"):
                with open_path("gs://bucket/file.txt"):
                    pass
