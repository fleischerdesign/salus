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

/**
 * Periodic background harvest of Health Connect measurements with direct push to the
 * Salus health-push endpoint. Idempotent by design: the endpoint upserts by
 * `(external_id, source)`, so retries and overlapping runs never duplicate rows.
 */
class HealthSyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    private enum class PushResult { SUCCESS, RETRY, UNAUTHORIZED }

    private companion object {
        const val BATCH_SIZE = 2000
        const val MAX_BATCHES = 200
    }

    override suspend fun doWork(): Result {
        val appContext = applicationContext
        val token = SecureStorage.token(appContext) ?: return Result.success()
        val serverUrl = SecureStorage.serverUrl(appContext)?.trimEnd('/') ?: return Result.success()

        val lastHarvest = SecureStorage.lastHarvestAt(appContext) ?: ""
        var cursor: String? = null
        var batches = 0

        do {
            val batch = HealthConnectHarvester(appContext).harvestBatch(lastHarvest, cursor, BATCH_SIZE)
            if (batch.metrics.isNotEmpty()) {
                when (pushMeasurements(serverUrl, token, batch.metrics)) {
                    PushResult.RETRY -> return Result.retry()
                    PushResult.UNAUTHORIZED -> return Result.success()
                    PushResult.SUCCESS -> Unit
                }
            }
            batch.metrics.maxOfOrNull { it.measuredAt }?.let { max ->
                if (max > lastHarvest) {
                    SecureStorage.setLastHarvestAt(appContext, max)
                }
            }
            cursor = batch.nextCursor
            batches += 1
        } while (cursor != null && batches < MAX_BATCHES)

        return Result.success()
    }

    private suspend fun pushMeasurements(
        serverUrl: String,
        token: String,
        metrics: List<HarvestedMetric>
    ): PushResult {
        return withContext(Dispatchers.IO) {
            try {
                val now = java.time.Instant.now().toString()
                val measurements = JSONArray()
                for (metric in metrics) {
                    measurements.put(JSONObject()
                        .put("id", java.util.UUID.randomUUID().toString())
                        .put("metric_code", metric.metricCode)
                        .put("source_data_type", "")
                        .put("source", metric.source)
                        .put("value_numeric", metric.valueNumeric ?: JSONObject.NULL)
                        .put("value_text", metric.valueText ?: JSONObject.NULL)
                        .put("value_json", metric.valueJson ?: JSONObject.NULL)
                        .put("start_time", metric.measuredAt)
                        .put("end_time", metric.endTime ?: metric.measuredAt)
                        .put("external_id", metric.externalId)
                        .put("created_at", now)
                        .put("updated_at", now))
                }
                val body = JSONObject().put("measurements", measurements).toString()
                val conn = URL("$serverUrl/api/v1/sync/health-push").openConnection() as HttpURLConnection
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
