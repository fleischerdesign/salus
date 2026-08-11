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
    fun checkPermissions(call: PluginCall) {
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
                call.reject(e.message)
            }
        }
    }

    @PluginMethod
    fun requestPermissions(call: PluginCall) {
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
        val ret = JSObject()
        val metricsArray = JSArray()
        ret.put("metrics", metricsArray)
        call.resolve(ret)
    }
}
