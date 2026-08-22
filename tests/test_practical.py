import pytest
from unittest.mock import AsyncMock, patch
from flet_practical import (
    Clipboard,
    Notifications,
    WakeLock,
    TtsService,
    AutoStart,
    InAppPurchase,
    Product,
    Share,
)


@pytest.mark.asyncio
async def test_clipboard():
    clipboard = Clipboard()
    with patch.object(clipboard, "_get_text_linux", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = "Practical Clipboard Test"
        text = await clipboard.get_text()
        assert text == "Practical Clipboard Test"

    with patch.object(clipboard, "_set_text_linux", new_callable=AsyncMock) as mock_set:
        mock_set.return_value = True
        res = await clipboard.set_text("Test")
        assert res is True


@pytest.mark.asyncio
async def test_notifications():
    notifications = Notifications()
    res = await notifications.show("Test Title", "Test Body", ongoing=True)
    assert res is True

    cancel_res = await notifications.cancel(1)
    assert cancel_res is True


@pytest.mark.asyncio
async def test_wakelock():
    wakelock = WakeLock()
    assert await wakelock.is_enabled() is False

    await wakelock.enable()
    assert await wakelock.is_enabled() is True

    await wakelock.disable()
    assert await wakelock.is_enabled() is False


@pytest.mark.asyncio
async def test_tts_initialization():
    tts = TtsService(voice="en-US-JennyNeural")
    assert tts.voice == "en-US-JennyNeural"
    assert tts.rate == "+0%"


@pytest.mark.asyncio
async def test_autostart():
    autostart = AutoStart(app_name="TestApp")
    assert autostart.app_name == "TestApp"


@pytest.mark.asyncio
async def test_iap():
    iap = InAppPurchase()
    assert await iap.is_available() is True
    products = await iap.get_products(["pro_sub"])
    assert len(products) == 1
    assert products[0].id == "pro_sub"

    buy_res = await iap.buy("pro_sub")
    assert buy_res is True


@pytest.mark.asyncio
async def test_share():
    share = Share()
    res = await share.share_text("Test Share Message", subject="Subject")
    assert res is True

    files_res = await share.share_files(["/nonexistent/file.txt"])
    assert files_res is False
