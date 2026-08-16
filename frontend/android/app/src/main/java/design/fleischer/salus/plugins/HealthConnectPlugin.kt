package design.fleischer.salus.plugins

import android.content.Intent
import androidx.activity.result.ActivityResult
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.PermissionController
import androidx.health.connect.client.permission.HealthPermission
import androidx.health.connect.client.records.*
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

@CapacitorPlugin(name = "HealthConnectPlugin")
class HealthConnectPlugin : Plugin() {

    private val PERMISSIONS = setOf(
        HealthPermission.PERMISSION_READ_HEALTH_DATA_HISTORY,
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
        HealthPermission.getReadPermission(HeightRecord::class),
        HealthPermission.getReadPermission(BodyFatRecord::class),
        HealthPermission.getReadPermission(BoneMassRecord::class),
        HealthPermission.getReadPermission(LeanBodyMassRecord::class),
        HealthPermission.getReadPermission(BodyWaterMassRecord::class),
        HealthPermission.getReadPermission(BasalMetabolicRateRecord::class),
        HealthPermission.getReadPermission(OxygenSaturationRecord::class),
        HealthPermission.getReadPermission(BloodGlucoseRecord::class),
        HealthPermission.getReadPermission(HydrationRecord::class),
        HealthPermission.getReadPermission(NutritionRecord::class),
        HealthPermission.getReadPermission(DistanceRecord::class),
        HealthPermission.getReadPermission(ElevationGainedRecord::class),
        HealthPermission.getReadPermission(FloorsClimbedRecord::class),
        HealthPermission.getReadPermission(SpeedRecord::class),
        HealthPermission.getReadPermission(PowerRecord::class),
        HealthPermission.getReadPermission(StepsCadenceRecord::class),
        HealthPermission.getReadPermission(CyclingPedalingCadenceRecord::class),
        HealthPermission.getReadPermission(WheelchairPushesRecord::class),
        HealthPermission.getReadPermission(Vo2MaxRecord::class),
        HealthPermission.getReadPermission(RespiratoryRateRecord::class),
        HealthPermission.getReadPermission(BodyTemperatureRecord::class),
        HealthPermission.getReadPermission(BasalBodyTemperatureRecord::class),
        HealthPermission.getReadPermission(MenstruationPeriodRecord::class),
        HealthPermission.getReadPermission(MenstruationFlowRecord::class),
        HealthPermission.getReadPermission(OvulationTestRecord::class),
        HealthPermission.getReadPermission(CervicalMucusRecord::class),
        HealthPermission.getReadPermission(IntermenstrualBleedingRecord::class),
        HealthPermission.getReadPermission(SexualActivityRecord::class),
        HealthPermission.getReadPermission(MindfulnessSessionRecord::class),
        HealthPermission.getReadPermission(PlannedExerciseSessionRecord::class),
        HealthPermission.getReadPermission(SkinTemperatureRecord::class)
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
                // Only report the permissions we actually request — the frontend uses this set
                // as the "changes token coverage" cursor for re-pinning on permission changes.
                val grantedOfOurs = granted.intersect(PERMISSIONS)
                val missing = PERMISSIONS.filter { it !in granted }
                val ret = JSObject()
                ret.put("granted", grantedOfOurs.isNotEmpty())
                ret.put("available", true)
                val grantedArray = JSArray()
                grantedOfOurs.forEach { grantedArray.put(it) }
                ret.put("grantedPermissions", grantedArray)
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
        val sinceIso = call.getString("sinceIso") ?: ""
        val cursor = call.getString("cursor")
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val batch = HealthConnectHarvester(context).harvestBatch(sinceIso, cursor)
                val metricsArray = JSArray()
                for (item in batch.metrics) {
                    metricsArray.put(item.toJSObject())
                }
                val ret = JSObject()
                ret.put("metrics", metricsArray)
                ret.put("next_cursor", batch.nextCursor ?: "")
                call.resolve(ret)
            } catch (e: Exception) {
                call.reject("Health Connect fetch error: ${e.message}")
            }
        }
    }

    @PluginMethod
    fun getChangesToken(call: PluginCall) {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val token = HealthConnectHarvester(context).getChangesToken()
                val ret = JSObject()
                ret.put("token", token ?: "")
                call.resolve(ret)
            } catch (e: Exception) {
                call.reject("Health Connect get changes token error: ${e.message}")
            }
        }
    }

    @PluginMethod
    fun getChanges(call: PluginCall) {
        val token = call.getString("token") ?: ""
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val result = HealthConnectHarvester(context).getChanges(token)
                val ret = JSObject()
                val metricsArray = JSArray()
                if (result != null) {
                    for (item in result.metrics) {
                        metricsArray.put(item.toJSObject())
                    }
                    ret.put("token", result.nextToken)
                } else {
                    ret.put("token", "")
                }
                ret.put("metrics", metricsArray)
                call.resolve(ret)
            } catch (e: Exception) {
                call.reject("Health Connect get changes error: ${e.message}")
            }
        }
    }

    private fun HarvestedMetric.toJSObject(): JSObject {
        val obj = JSObject()
        obj.put("metric_code", metricCode)
        obj.put("unit", unit)
        obj.put("measured_at", measuredAt)
        obj.put("external_id", externalId)
        obj.put("value", valueNumeric)
        obj.put("value_text", valueText)
        obj.put("value_json", valueJson)
        obj.put("end_time", endTime)
        obj.put("source", source)
        return obj
    }
}
