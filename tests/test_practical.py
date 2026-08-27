import pytest
from unittest.mock import AsyncMock, patch
from flet_practical import (
    Clipboard,
    Notifications,
    WakeLock,
    TtsService,
    AutoStart,
    BackgroundService,
    ReceiveShare,
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
async def test_notifications_enabled_default():
    notifications = Notifications()
    assert await notifications.are_notifications_enabled() is True


@pytest.mark.asyncio
async def test_notifications_on_click_adapter():
    received = []
    notifications = Notifications(on_click=lambda payload: received.append(payload))

    class _FakeEvent:
        data = "tracking:open"

    await notifications._on_click_event(_FakeEvent())
    assert received == ["tracking:open"]


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
async def test_autostart_mobile_service_delegation():
    autostart = AutoStart(app_name="TestApp")
    svc = AsyncMock()
    svc.enable.return_value = True
    svc.is_enabled.return_value = True
    with patch.object(autostart, "_is_mobile", return_value=True), \
         patch.object(autostart, "_ensure_service", return_value=svc):
        assert await autostart.enable() is True
        assert await autostart.is_enabled() is True
        svc.enable.assert_awaited_once()
        svc.is_enabled.assert_awaited_once()


@pytest.mark.asyncio
async def test_autostart_mobile_no_service():
    autostart = AutoStart(app_name="TestApp")
    with patch.object(autostart, "_is_mobile", return_value=True), \
         patch.object(autostart, "_ensure_service", return_value=None):
        assert await autostart.enable() is False
        assert await autostart.disable() is False
        assert await autostart.is_enabled() is False


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


@pytest.mark.asyncio
async def test_background_service():
    bg = BackgroundService()
    # On desktop, start is no-op returning True, is_running False
    assert await bg.start(title="Test", text="Testing") is True
    assert await bg.is_running() is False
    assert await bg.stop() is True


@pytest.mark.asyncio
async def test_receive_share():
    receive = ReceiveShare()
    # No page / no incoming share on desktop -> empty list
    initial = await receive.get_initial_share()
    assert initial == []
    assert await receive.reset() is False
