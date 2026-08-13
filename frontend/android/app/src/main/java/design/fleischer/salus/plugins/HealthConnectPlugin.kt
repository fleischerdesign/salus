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
        HealthPermission.getReadPermission(SexualActivityRecord::class)
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
        val sinceIso = call.getString("sinceIso") ?: ""

        CoroutineScope(Dispatchers.IO).launch {
            try {
                val harvester = HealthConnectHarvester(context)
                val metrics = harvester.harvest(sinceIso)
                val metricsArray = JSArray()
                for (item in metrics) {
                    val obj = JSObject()
                    obj.put("metric_code", item.metricCode)
                    obj.put("value", item.value)
                    obj.put("unit", item.unit)
                    obj.put("measured_at", item.measuredAt)
                    obj.put("external_id", item.externalId)
                    obj.put("source", item.source)
                    metricsArray.put(obj)
                }
                val ret = JSObject()
                ret.put("metrics", metricsArray)
                call.resolve(ret)
            } catch (e: Exception) {
                call.reject("Health Connect fetch error: ${e.message}")
            }
        }
    }
}
