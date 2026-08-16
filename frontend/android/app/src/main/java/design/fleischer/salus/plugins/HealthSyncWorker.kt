package design.fleischer.salus.plugins

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.util.UUID

/**
 * Periodic background harvest of Health Connect metrics with direct push to the
 * Salus sync endpoint. Idempotent via a durable pending queue (fixed client_ids
 * survive retries; the server dedups on client_id within the sync_push_log TTL).
 */
class HealthSyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    private enum class PushResult { SUCCESS, RETRY, UNAUTHORIZED }

    override suspend fun doWork(): Result {
        val appContext = applicationContext
        val token = SecureStorage.token(appContext) ?: return Result.success()
        val serverUrl = SecureStorage.serverUrl(appContext)?.trimEnd('/') ?: return Result.success()

        val lastHarvest = SecureStorage.lastHarvestAt(appContext) ?: ""

        val harvested = HealthConnectHarvester(appContext).harvest(lastHarvest)

        val queue = loadPendingQueue(appContext)
        var maxMeasuredAt = lastHarvest
        val now = java.time.Instant.now().toString()

        for (metric in harvested) {
            queue.put(buildOperation(UUID.randomUUID().toString(), UUID.randomUUID().toString(), metric, now))
            if (metric.measuredAt > maxMeasuredAt) maxMeasuredAt = metric.measuredAt
        }

        if (queue.length() == 0) {
            return Result.success()
        }

        SecureStorage.setPendingQueue(appContext, queue.toString())

        return when (pushQueue(serverUrl, token, queue)) {
            PushResult.SUCCESS -> {
                SecureStorage.setPendingQueue(appContext, null)
                SecureStorage.setLastHarvestAt(appContext, maxMeasuredAt)
                Result.success()
            }
            PushResult.RETRY -> Result.retry()
            PushResult.UNAUTHORIZED -> Result.success()
        }
    }

    private fun loadPendingQueue(context: Context): JSONArray {
        val raw = SecureStorage.pendingQueue(context)
        return try {
            if (raw.isNullOrEmpty()) JSONArray() else JSONArray(raw)
        } catch (e: Exception) {
            JSONArray()
        }
    }

    private fun buildOperation(id: String, clientId: String, metric: HarvestedMetric, now: String): JSONObject {
        val data = JSONObject()
            .put("id", id)
            .put("user_id", "self")
            .put("metric_code", metric.metricCode)
            .put("source_data_type", "")
            .put("source", metric.source)
            .put("value_numeric", metric.valueNumeric ?: JSONObject.NULL)
            .put("value_text", metric.valueText ?: JSONObject.NULL)
            .put("value_json", metric.valueJson ?: JSONObject.NULL)
            .put("start_time", metric.measuredAt)
            .put("end_time", metric.endTime ?: metric.measuredAt)
            .put("notes", JSONObject.NULL)
            .put("external_id", metric.externalId)
            .put("created_at", now)
            .put("updated_at", JSONObject.NULL)
            .put("deleted_at", JSONObject.NULL)

        return JSONObject()
            .put("type", "create")
            .put("entity", "measurement")
            .put("client_id", clientId)
            .put("id", id)
            .put("data", data)
    }

    private suspend fun pushQueue(serverUrl: String, token: String, queue: JSONArray): PushResult {
        return withContext(Dispatchers.IO) {
            try {
                val body = JSONObject().put("operations", queue).toString()
                val conn = URL("$serverUrl/api/v1/sync/push").openConnection() as HttpURLConnection
                conn.requestMethod = "POST"
                conn.connectTimeout = 15000
                conn.readTimeout = 30000
                conn.setRequestProperty("Content-Type", "application/json")
                conn.setRequestProperty("Authorization", "Bearer $token")
                conn.setRequestProperty("X-Salus-Sync-Version", "2")
                conn.doOutput = true
                conn.outputStream.use { it.write(body.toByteArray(Charsets.UTF_8)) }

                when (conn.responseCode) {
                    200, 201, 204 -> PushResult.SUCCESS
                    401, 403 -> PushResult.UNAUTHORIZED
                    else -> PushResult.RETRY
                }
            } catch (e: Exception) {
                PushResult.RETRY
            }
        }
    }
}
