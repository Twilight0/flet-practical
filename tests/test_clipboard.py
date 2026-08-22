import pytest
from unittest.mock import AsyncMock, patch
from flet_practical import Clipboard


@pytest.mark.asyncio
async def test_clipboard_set_and_get_text():
    clipboard = Clipboard()
    with patch.object(clipboard, "_get_text_linux", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = "Hello World"
        text = await clipboard.get_text()
        assert text == "Hello World"

    with patch.object(clipboard, "_set_text_linux", new_callable=AsyncMock) as mock_set:
        mock_set.return_value = True
        res = await clipboard.set_text("Hello World")
        assert res is True


@pytest.mark.asyncio
async def test_clipboard_has_text():
    clipboard = Clipboard()
    with patch.object(clipboard, "get_text", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = "Non empty"
        has_txt = await clipboard.has_text()
        assert has_txt is True

        mock_get.return_value = ""
        has_txt = await clipboard.has_text()
        assert has_txt is False


@pytest.mark.asyncio
async def test_clipboard_get_image():
    clipboard = Clipboard()
    with patch.object(clipboard, "get_image", new_callable=AsyncMock) as mock_img:
        mock_img.return_value = b"PNG_DATA"
        b64 = await clipboard.get_image_base64()
        assert b64 == "UE5HX0RBVEE="


@pytest.mark.asyncio
async def test_clipboard_clear():
    clipboard = Clipboard()
    with patch.object(clipboard, "set_text", new_callable=AsyncMock) as mock_set:
        mock_set.return_value = True
        res = await clipboard.clear()
        assert res is True
        mock_set.assert_awaited_once_with("")
