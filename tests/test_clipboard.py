import pytest
from unittest.mock import AsyncMock, patch
import flet as ft
from flet_clipboard import Clipboard


def test_clipboard_initialization():
    clipboard = Clipboard()
    assert clipboard._c == "flet_clipboard"


@pytest.mark.asyncio
async def test_clipboard_get_text():
    clipboard = Clipboard()
    with patch.object(clipboard, "_invoke_method", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = "Hello World"
        text = await clipboard.get_text()
        assert text == "Hello World"
        mock_invoke.assert_awaited_once_with("get_text", timeout=None)


@pytest.mark.asyncio
async def test_clipboard_set_text():
    clipboard = Clipboard()
    with patch.object(clipboard, "_invoke_method", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = True
        success = await clipboard.set_text("Sample Text")
        assert success is True
        mock_invoke.assert_awaited_once_with("set_text", {"text": "Sample Text"}, timeout=None)


@pytest.mark.asyncio
async def test_clipboard_has_text():
    clipboard = Clipboard()
    with patch.object(clipboard, "_invoke_method", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = True
        has_txt = await clipboard.has_text()
        assert has_txt is True
        mock_invoke.assert_awaited_once_with("has_text", timeout=None)


@pytest.mark.asyncio
async def test_clipboard_get_image():
    clipboard = Clipboard()
    with patch.object(clipboard, "_invoke_method", new_callable=AsyncMock) as mock_invoke:
        # base64 for "test"
        mock_invoke.return_value = "dGVzdA=="
        img_bytes = await clipboard.get_image()
        assert img_bytes == b"test"
        mock_invoke.assert_awaited_once_with("get_image", timeout=None)


@pytest.mark.asyncio
async def test_clipboard_get_files():
    clipboard = Clipboard()
    with patch.object(clipboard, "_invoke_method", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = ["/path/to/file1.txt", "/path/to/file2.png"]
        files = await clipboard.get_files()
        assert files == ["/path/to/file1.txt", "/path/to/file2.png"]
        mock_invoke.assert_awaited_once_with("get_files", timeout=None)


@pytest.mark.asyncio
async def test_clipboard_clear():
    clipboard = Clipboard()
    with patch.object(clipboard, "_invoke_method", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = True
        res = await clipboard.clear()
        assert res is True
        mock_invoke.assert_awaited_once_with("clear", timeout=None)
