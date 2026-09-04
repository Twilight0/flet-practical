package {{ cookiecutter.org_name_2 }}.{{ cookiecutter.package_name }}

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.util.Log
import androidx.core.content.FileProvider
import java.io.File
import java.io.FileOutputStream

/**
 * Headless share receiver — does NOT spawn MainActivity UI.
 * Handles ACTION_SEND / SEND_MULTIPLE for text/plain, image, video, any mime
 * Extracts intent data, persists to app files dir, then finishes.
 * MainActivity (when next opened) or BackgroundService reads
 * filesDir/share_payload.json and executes download+upscale.
 * Toggle via pyproject.toml [tool.flet.android] receive_share=true (default)
 * and [tool.flet.android] receive_share_headless=true for this activity.
 */
class ShareReceiverActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        try {
            val intent = intent
            val action = intent.action
            val type = intent.type
            Log.i("ShareReceiver", "onCreate action=$action type=$type")
            if (Intent.ACTION_SEND == action || Intent.ACTION_SEND_MULTIPLE == action) {
                handleSend(intent)
            } else if (Intent.ACTION_VIEW == action) {
                handleView(intent)
            }
        } catch (e: Exception) {
            Log.e("ShareReceiver", "handle error", e)
        } finally {
            finish()
        }
    }

    private fun handleSend(intent: Intent) {
        val text = intent.getStringExtra(Intent.EXTRA_TEXT)
        val stream = intent.getParcelableExtra<android.net.Uri>(Intent.EXTRA_STREAM)
        val streams = intent.getParcelableArrayListExtra<android.net.Uri>(Intent.EXTRA_STREAM)
        // Persist payload for Flutter/Dart to read on next MainActivity resume
        val payload = StringBuilder()
        payload.append("{\"action\":\"" + intent.action + "\",")
        payload.append("\"type\":\"" + intent.type + "\",")
        if (text != null) payload.append("\"text\":\"" + text.replace("\"", "\\\"") + "\",")
        if (stream != null) payload.append("\"stream\":\"" + stream + "\",")
        if (streams != null) payload.append("\"streams\":[" + streams.joinToString(",") { "\"" + it + "\"" } + "],")
        val uris = mutableListOf<android.net.Uri>()
        if (stream != null) uris.add(stream)
        if (streams != null) uris.addAll(streams)
        for (uri in uris) {
            try {
                val input = contentResolver.openInputStream(uri)
                if (input != null) {
                    val fileName = uri.lastPathSegment ?: "shared_${System.currentTimeMillis()}"
                    val outFile = File(cacheDir, "share_$fileName")
                    FileOutputStream(outFile).use { out -> input.copyTo(out) }
                    input.close()
                    payload.append("\"cached\":\"${outFile.absolutePath}\",")
                }
            } catch (_: Exception) {}
        }
        payload.append("\"ts\":${System.currentTimeMillis()}}")
        try {
            val out = File(filesDir, "share_payload.json")
            out.writeText(payload.toString())
            Log.i("ShareReceiver", "persisted ${out.absolutePath}")
        } catch (_: Exception) {}
        // Optionally start foreground service to process headless (uncomment if BackgroundService used)
        // val svc = Intent(this, FlutterForegroundTaskService::class.java)
        // startForegroundService(svc)
    }

    private fun handleView(intent: Intent) {
        val data = intent.dataString
        try {
            val out = File(filesDir, "share_payload.json")
            out.writeText("{\"action\":\"VIEW\",\"data\":\"$data\",\"ts\":${System.currentTimeMillis()}}")
        } catch (_: Exception) {}
    }
}
