package design.fleischer.salus.plugins

import android.content.Intent
import androidx.activity.result.ActivityResult
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.PermissionController
import androidx.health.connect.client.permission.HealthPermission
import androidx.health.connect.client.records.*
import androidx.health.connect.client.request.ReadRecordsRequest
import androidx.health.connect.client.time.TimeRangeFilter
import com.getcapacitor.JSArray
import com.getcapacitor.JSObject
import com.getcapacitor.Plugin
import com.getcapacitor.PluginCall
import com.getcapacitor.PluginMethod
import com.getcapacitor.annotation.ActivityCallback
import com.getcapacitor.annotation.CapacitorPlugin
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.time.Duration
import java.time.Instant
import java.time.temporal.ChronoUnit

@CapacitorPlugin(name = "HealthConnectPlugin")
class HealthConnectPlugin : Plugin() {

    private val PERMISSIONS = setOf(
        HealthPermission.getReadPermission(StepsRecord::class),
        HealthPermission.getReadPermission(HeartRateRecord::class),
        HealthPermission.getReadPermission(RestingHeartRateRecord::class),
        HealthPermission.getReadPermission(HeartRateVariabilityRmssdRecord::class),
        HealthPermission.getReadPermission(SleepSessionRecord::class),
        HealthPermission.getReadPermission(TotalCaloriesBurnedRecord::class),
        HealthPermission.getReadPermission(ActiveCaloriesBurnedRecord::class),
        HealthPermission.getReadPermission(ExerciseSessionRecord::class),
        HealthPermission.getReadPermission(BloodPressureRecord::class),
        HealthPermission.getReadPermission(WeightRecord::class),
        HealthPermission.getReadPermission(BodyFatRecord::class),
        HealthPermission.getReadPermission(OxygenSaturationRecord::class),
        HealthPermission.getReadPermission(BloodGlucoseRecord::class),
        HealthPermission.getReadPermission(HydrationRecord::class),
        HealthPermission.getReadPermission(NutritionRecord::class),
        HealthPermission.getReadPermission(DistanceRecord::class)
    )

    private val healthConnectClient: HealthConnectClient?
        get() = try {
            if (HealthConnectClient.getSdkStatus(context) == HealthConnectClient.SDK_AVAILABLE) {
                HealthConnectClient.getOrCreate(context)
            } else {
                null
            }
        } catch (e: Exception) {
            null
        }

    @PluginMethod
    fun isAvailable(call: PluginCall) {
        val status = try {
            HealthConnectClient.getSdkStatus(context)
        } catch (e: Exception) {
            HealthConnectClient.SDK_UNAVAILABLE
        }
        val ret = JSObject()
        ret.put("available", status == HealthConnectClient.SDK_AVAILABLE)
        ret.put("status", status)
        call.resolve(ret)
    }

    @PluginMethod
    override fun checkPermissions(call: PluginCall) {
        val client = healthConnectClient
        if (client == null) {
            val ret = JSObject()
            ret.put("granted", false)
            ret.put("available", false)
            call.resolve(ret)
            return
        }

        CoroutineScope(Dispatchers.IO).launch {
            try {
                val granted = client.permissionController.getGrantedPermissions()
                val missing = PERMISSIONS.filter { it !in granted }
                val ret = JSObject()
                ret.put("granted", missing.isEmpty())
                val missingArray = JSArray()
                missing.forEach { missingArray.put(it) }
                ret.put("missing", missingArray)
                call.resolve(ret)
            } catch (e: Exception) {
                call.reject("Check permissions error: ${e.message}")
            }
        }
    }

    @PluginMethod
    override fun requestPermissions(call: PluginCall) {
        val client = healthConnectClient
        if (client == null) {
            call.reject("Health Connect is not available on this device")
            return
        }

        try {
            val intent = PermissionController.createRequestPermissionResultContract()
                .createIntent(context, PERMISSIONS)
            startActivityForResult(call, intent, "handlePermissionResult")
        } catch (e: Exception) {
            call.reject("Failed to launch Health Connect permission prompt: ${e.message}")
        }
    }

    @ActivityCallback
    private fun handlePermissionResult(call: PluginCall, result: ActivityResult) {
        checkPermissions(call)
    }

    @PluginMethod
    fun openHealthConnectSettings(call: PluginCall) {
        try {
            val intent = Intent("androidx.health.ACTION_HEALTH_CONNECT_SETTINGS")
            activity.startActivity(intent)
            call.resolve()
        } catch (e: Exception) {
            try {
                val intent = Intent(HealthConnectClient.ACTION_HEALTH_CONNECT_SETTINGS)
                activity.startActivity(intent)
                call.resolve()
            } catch (ex: Exception) {
                call.reject("Could not open Health Connect settings: ${ex.message}")
            }
        }
    }

    @PluginMethod
    fun fetchDelta(call: PluginCall) {
        val client = healthConnectClient
        if (client == null) {
            val ret = JSObject()
            ret.put("metrics", JSArray())
            call.resolve(ret)
            return
        }

        val sinceIso = call.getString("sinceIso") ?: ""
        val startTime = try {
            if (sinceIso.isNotBlank()) Instant.parse(sinceIso) else Instant.now().minus(30, ChronoUnit.DAYS)
        } catch (e: Exception) {
            Instant.now().minus(30, ChronoUnit.DAYS)
        }
        val endTime = Instant.now()

        CoroutineScope(Dispatchers.IO).launch {
            try {
                val timeRangeFilter = TimeRangeFilter.between(startTime, endTime)
                val metricsArray = JSArray()

                // 1. Steps
                try {
                    val stepsResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = StepsRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in stepsResponse.records) {
                        val item = JSObject()
                        item.put("metric_code", "steps")
                        item.put("value", record.count.toDouble())
                        item.put("unit", "count")
                        item.put("measured_at", record.startTime.toString())
                        item.put("external_id", "hc_steps_${record.metadata.id}")
                        item.put("source", "health_connect")
                        metricsArray.put(item)
                    }
                } catch (_: Exception) {}

                // 2. Heart Rate
                try {
                    val hrResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = HeartRateRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in hrResponse.records) {
                        for (sample in record.samples) {
                            val item = JSObject()
                            item.put("metric_code", "heart_rate")
                            item.put("value", sample.beatsPerMinute.toDouble())
                            item.put("unit", "bpm")
                            item.put("measured_at", sample.time.toString())
                            item.put("external_id", "hc_hr_${record.metadata.id}_${sample.time.toEpochMilli()}")
                            item.put("source", "health_connect")
                            metricsArray.put(item)
                        }
                    }
                } catch (_: Exception) {}

                // 3. Resting Heart Rate
                try {
                    val rhrResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = RestingHeartRateRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in rhrResponse.records) {
                        val item = JSObject()
                        item.put("metric_code", "resting_heart_rate")
                        item.put("value", record.beatsPerMinute.toDouble())
                        item.put("unit", "bpm")
                        item.put("measured_at", record.time.toString())
                        item.put("external_id", "hc_rhr_${record.metadata.id}")
                        item.put("source", "health_connect")
                        metricsArray.put(item)
                    }
                } catch (_: Exception) {}

                // 4. Sleep
                try {
                    val sleepResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = SleepSessionRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in sleepResponse.records) {
                        val durationMinutes = Duration.between(record.startTime, record.endTime).toMinutes().toDouble()
                        val item = JSObject()
                        item.put("metric_code", "sleep_duration")
                        item.put("value", durationMinutes)
                        item.put("unit", "min")
                        item.put("measured_at", record.endTime.toString())
                        item.put("external_id", "hc_sleep_${record.metadata.id}")
                        item.put("source", "health_connect")
                        metricsArray.put(item)
                    }
                } catch (_: Exception) {}

                // 5. Total Calories Burned
                try {
                    val calResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = TotalCaloriesBurnedRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in calResponse.records) {
                        val item = JSObject()
                        item.put("metric_code", "calories_burned")
                        item.put("value", record.energy.inKilocalories)
                        item.put("unit", "kcal")
                        item.put("measured_at", record.startTime.toString())
                        item.put("external_id", "hc_cal_${record.metadata.id}")
                        item.put("source", "health_connect")
                        metricsArray.put(item)
                    }
                } catch (_: Exception) {}

                // 6. Weight
                try {
                    val weightResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = WeightRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in weightResponse.records) {
                        val item = JSObject()
                        item.put("metric_code", "weight")
                        item.put("value", record.weight.inKilograms)
                        item.put("unit", "kg")
                        item.put("measured_at", record.time.toString())
                        item.put("external_id", "hc_weight_${record.metadata.id}")
                        item.put("source", "health_connect")
                        metricsArray.put(item)
                    }
                } catch (_: Exception) {}

                // 7. Blood Pressure
                try {
                    val bpResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = BloodPressureRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in bpResponse.records) {
                        val sysItem = JSObject()
                        sysItem.put("metric_code", "systolic_bp")
                        sysItem.put("value", record.systolic.inMillimetersOfMercury)
                        sysItem.put("unit", "mmHg")
                        sysItem.put("measured_at", record.time.toString())
                        sysItem.put("external_id", "hc_bps_${record.metadata.id}")
                        sysItem.put("source", "health_connect")
                        metricsArray.put(sysItem)

                        val diaItem = JSObject()
                        diaItem.put("metric_code", "diastolic_bp")
                        diaItem.put("value", record.diastolic.inMillimetersOfMercury)
                        diaItem.put("unit", "mmHg")
                        diaItem.put("measured_at", record.time.toString())
                        diaItem.put("external_id", "hc_bpd_${record.metadata.id}")
                        diaItem.put("source", "health_connect")
                        metricsArray.put(diaItem)
                    }
                } catch (_: Exception) {}

                // 8. Oxygen Saturation (SpO2)
                try {
                    val spo2Response = client.readRecords(
                        ReadRecordsRequest(
                            recordType = OxygenSaturationRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in spo2Response.records) {
                        val item = JSObject()
                        item.put("metric_code", "spo2")
                        item.put("value", record.percentage.value)
                        item.put("unit", "%")
                        item.put("measured_at", record.time.toString())
                        item.put("external_id", "hc_spo2_${record.metadata.id}")
                        item.put("source", "health_connect")
                        metricsArray.put(item)
                    }
                } catch (_: Exception) {}

                val ret = JSObject()
                ret.put("metrics", metricsArray)
                call.resolve(ret)
            } catch (e: Exception) {
                call.reject("Health Connect fetch error: ${e.message}")
            }
        }
    }
}
