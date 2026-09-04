package {{ cookiecutter.org_name_2 }}.{{ cookiecutter.package_name }}

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.os.Build
import android.os.IBinder
import android.util.Log
import androidx.core.app.NotificationCompat
import io.flutter.FlutterInjector
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.embedding.engine.dart.DartExecutor
import io.flutter.plugin.common.MethodChannel
import java.io.File

/**
 * Pure Python headless submodule — does NOT spawn MainActivity UI.
 * Started by ShareReceiverActivity when receive_share_headless=true.
 * Creates headless FlutterEngine with serious_python, then invokes
 * Dart ReceiveShare -> Python src/main.py handle_incoming_share -> download+upscale.
 * Shows foreground notification while working, then stops.
 */
class ShareDownloadService : Service() {
    private var flutterEngine: FlutterEngine? = null
    private val channelName = "app.instasave/share_download"

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val payloadFile = File(filesDir, "share_payload.json")
        val payload = try { payloadFile.readText() } catch (_: Exception) { "{}" }
        Log.i("ShareDownloadService", "onStartCommand payload=$payload")
        startForeground(1, buildNotification("Instasave", "Processing shared content…"))
        // Headless FlutterEngine — runs Dart entrypoint shareBackgroundEntry (must be @pragma('vm:entry-point'))
        try {
            val engine = FlutterEngine(this)
            flutterEngine = engine
            // Pre-warm serious_python is handled by Dart side when engine runs
            val entrypoint = DartExecutor.DartEntrypoint(
                FlutterInjector.instance().flutterLoader().findAppBundlePath(),
                "shareBackgroundEntry"
            )
            engine.dartExecutor.executeDartEntrypoint(entrypoint)
            // Channel to pass payload to Dart
            MethodChannel(engine.dartExecutor.binaryMessenger, channelName).invokeMethod("handleShare", payload,
                object : MethodChannel.Result {
                    override fun success(result: Any?) { stopSelf() }
                    override fun error(code: String, msg: String?, details: Any?) { stopSelf() }
                    override fun notImplemented() { stopSelf() }
                })
        } catch (e: Exception) {
            Log.e("ShareDownloadService", "headless engine error", e)
            stopSelf()
        }
        return START_NOT_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        try { flutterEngine?.destroy() } catch (_: Exception) {}
        super.onDestroy()
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val mgr = getSystemService(NotificationManager::class.java)
            val ch = NotificationChannel("share_download", "Share Download", NotificationManager.IMPORTANCE_LOW)
            mgr.createNotificationChannel(ch)
        }
    }

    private fun buildNotification(title: String, text: String): Notification {
        return NotificationCompat.Builder(this, "share_download")
            .setContentTitle(title)
            .setContentText(text)
            .setSmallIcon(android.R.drawable.stat_sys_download)
            .setOngoing(true)
            .build()
    }
}
