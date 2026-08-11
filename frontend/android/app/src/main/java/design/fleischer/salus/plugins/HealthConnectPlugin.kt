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
                        item.put("metric_code", "sleep")
                        item.put("value", durationMinutes)
                        item.put("unit", "minutes")
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

                // 9. Active Calories Burned
                try {
                    val activeCalResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = ActiveCaloriesBurnedRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in activeCalResponse.records) {
                        val item = JSObject()
                        item.put("metric_code", "active_calories")
                        item.put("value", record.energy.inKilocalories)
                        item.put("unit", "kcal")
                        item.put("measured_at", record.startTime.toString())
                        item.put("external_id", "hc_actcal_${record.metadata.id}")
                        item.put("source", "health_connect")
                        metricsArray.put(item)
                    }
                } catch (_: Exception) {}

                // 10. Distance
                try {
                    val distResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = DistanceRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in distResponse.records) {
                        val item = JSObject()
                        item.put("metric_code", "distance")
                        item.put("value", record.distance.inKilometers)
                        item.put("unit", "km")
                        item.put("measured_at", record.startTime.toString())
                        item.put("external_id", "hc_dist_${record.metadata.id}")
                        item.put("source", "health_connect")
                        metricsArray.put(item)
                    }
                } catch (_: Exception) {}

                // 11. Elevation Gained
                try {
                    val elevResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = ElevationGainedRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in elevResponse.records) {
                        val item = JSObject()
                        item.put("metric_code", "elevation_gained")
                        item.put("value", record.elevation.inMeters)
                        item.put("unit", "m")
                        item.put("measured_at", record.startTime.toString())
                        item.put("external_id", "hc_elev_${record.metadata.id}")
                        item.put("source", "health_connect")
                        metricsArray.put(item)
                    }
                } catch (_: Exception) {}

                // 12. Floors Climbed
                try {
                    val floorsResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = FloorsClimbedRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in floorsResponse.records) {
                        val item = JSObject()
                        item.put("metric_code", "floors_climbed")
                        item.put("value", record.floors)
                        item.put("unit", "floors")
                        item.put("measured_at", record.startTime.toString())
                        item.put("external_id", "hc_floors_${record.metadata.id}")
                        item.put("source", "health_connect")
                        metricsArray.put(item)
                    }
                } catch (_: Exception) {}

                // 13. VO2 Max
                try {
                    val vo2Response = client.readRecords(
                        ReadRecordsRequest(
                            recordType = Vo2MaxRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in vo2Response.records) {
                        val item = JSObject()
                        item.put("metric_code", "vo2_max")
                        item.put("value", record.vo2MillilitersPerMinuteKilogram)
                        item.put("unit", "ml/kg/min")
                        item.put("measured_at", record.time.toString())
                        item.put("external_id", "hc_vo2_${record.metadata.id}")
                        item.put("source", "health_connect")
                        metricsArray.put(item)
                    }
                } catch (_: Exception) {}

                // 14. Respiratory Rate
                try {
                    val respResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = RespiratoryRateRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in respResponse.records) {
                        val item = JSObject()
                        item.put("metric_code", "respiratory_rate")
                        item.put("value", record.rate)
                        item.put("unit", "rpm")
                        item.put("measured_at", record.time.toString())
                        item.put("external_id", "hc_resp_${record.metadata.id}")
                        item.put("source", "health_connect")
                        metricsArray.put(item)
                    }
                } catch (_: Exception) {}

                // 15. Body Temperature
                try {
                    val tempResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = BodyTemperatureRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in tempResponse.records) {
                        val item = JSObject()
                        item.put("metric_code", "body_temperature")
                        item.put("value", record.temperature.inCelsius)
                        item.put("unit", "°C")
                        item.put("measured_at", record.time.toString())
                        item.put("external_id", "hc_temp_${record.metadata.id}")
                        item.put("source", "health_connect")
                        metricsArray.put(item)
                    }
                } catch (_: Exception) {}

                // 16. Height
                try {
                    val heightResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = HeightRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in heightResponse.records) {
                        val item = JSObject()
                        item.put("metric_code", "height")
                        item.put("value", record.height.inMeters * 100)
                        item.put("unit", "cm")
                        item.put("measured_at", record.time.toString())
                        item.put("external_id", "hc_height_${record.metadata.id}")
                        item.put("source", "health_connect")
                        metricsArray.put(item)
                    }
                } catch (_: Exception) {}

                // 17. Body Fat
                try {
                    val bodyFatResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = BodyFatRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in bodyFatResponse.records) {
                        val item = JSObject()
                        item.put("metric_code", "body_fat")
                        item.put("value", record.percentage.value)
                        item.put("unit", "%")
                        item.put("measured_at", record.time.toString())
                        item.put("external_id", "hc_bf_${record.metadata.id}")
                        item.put("source", "health_connect")
                        metricsArray.put(item)
                    }
                } catch (_: Exception) {}

                // 18. Heart Rate Variability (HRV RMSSD)
                try {
                    val hrvResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = HeartRateVariabilityRmssdRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in hrvResponse.records) {
                        val item = JSObject()
                        item.put("metric_code", "hrv")
                        item.put("value", record.heartRateVariabilityMillis)
                        item.put("unit", "ms")
                        item.put("measured_at", record.time.toString())
                        item.put("external_id", "hc_hrv_${record.metadata.id}")
                        item.put("source", "health_connect")
                        metricsArray.put(item)
                    }
                } catch (_: Exception) {}

                // 19. Hydration (Water)
                try {
                    val hydrResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = HydrationRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in hydrResponse.records) {
                        val item = JSObject()
                        item.put("metric_code", "water")
                        item.put("value", record.volume.inLiters * 1000)
                        item.put("unit", "ml")
                        item.put("measured_at", record.startTime.toString())
                        item.put("external_id", "hc_water_${record.metadata.id}")
                        item.put("source", "health_connect")
                        metricsArray.put(item)
                    }
                } catch (_: Exception) {}

                // 20. Blood Glucose
                try {
                    val bgResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = BloodGlucoseRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in bgResponse.records) {
                        val item = JSObject()
                        item.put("metric_code", "blood_glucose")
                        item.put("value", record.level.inMilligramsPerDeciliter)
                        item.put("unit", "mg/dL")
                        item.put("measured_at", record.time.toString())
                        item.put("external_id", "hc_bg_${record.metadata.id}")
                        item.put("source", "health_connect")
                        metricsArray.put(item)
                    }
                } catch (_: Exception) {}

                // 21. Bone Mass
                try {
                    val boneResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = BoneMassRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in boneResponse.records) {
                        val item = JSObject()
                        item.put("metric_code", "bone_mass")
                        item.put("value", record.mass.inKilograms)
                        item.put("unit", "kg")
                        item.put("measured_at", record.time.toString())
                        item.put("external_id", "hc_bone_${record.metadata.id}")
                        item.put("source", "health_connect")
                        metricsArray.put(item)
                    }
                } catch (_: Exception) {}

                // 22. Lean Body Mass
                try {
                    val leanResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = LeanBodyMassRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in leanResponse.records) {
                        val item = JSObject()
                        item.put("metric_code", "lean_body_mass")
                        item.put("value", record.mass.inKilograms)
                        item.put("unit", "kg")
                        item.put("measured_at", record.time.toString())
                        item.put("external_id", "hc_lean_${record.metadata.id}")
                        item.put("source", "health_connect")
                        metricsArray.put(item)
                    }
                } catch (_: Exception) {}

                // 23. Body Water Mass
                try {
                    val waterMassResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = BodyWaterMassRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in waterMassResponse.records) {
                        val item = JSObject()
                        item.put("metric_code", "body_water_mass")
                        item.put("value", record.mass.inKilograms)
                        item.put("unit", "kg")
                        item.put("measured_at", record.time.toString())
                        item.put("external_id", "hc_bwm_${record.metadata.id}")
                        item.put("source", "health_connect")
                        metricsArray.put(item)
                    }
                } catch (_: Exception) {}

                // 24. Basal Metabolic Rate (BMR)
                try {
                    val bmrResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = BasalMetabolicRateRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in bmrResponse.records) {
                        val item = JSObject()
                        item.put("metric_code", "bmr")
                        item.put("value", record.basalMetabolicRate.inKilocaloriesPerDay)
                        item.put("unit", "kcal")
                        item.put("measured_at", record.time.toString())
                        item.put("external_id", "hc_bmr_${record.metadata.id}")
                        item.put("source", "health_connect")
                        metricsArray.put(item)
                    }
                } catch (_: Exception) {}

                // 25. Speed
                try {
                    val speedResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = SpeedRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in speedResponse.records) {
                        for (sample in record.samples) {
                            val item = JSObject()
                            item.put("metric_code", "speed")
                            item.put("value", sample.speed.inKilometersPerHour)
                            item.put("unit", "km/h")
                            item.put("measured_at", sample.time.toString())
                            item.put("external_id", "hc_spd_${record.metadata.id}_${sample.time.toEpochMilli()}")
                            item.put("source", "health_connect")
                            metricsArray.put(item)
                        }
                    }
                } catch (_: Exception) {}

                // 26. Power
                try {
                    val powerResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = PowerRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in powerResponse.records) {
                        for (sample in record.samples) {
                            val item = JSObject()
                            item.put("metric_code", "power")
                            item.put("value", sample.power.inWatts)
                            item.put("unit", "W")
                            item.put("measured_at", sample.time.toString())
                            item.put("external_id", "hc_pwr_${record.metadata.id}_${sample.time.toEpochMilli()}")
                            item.put("source", "health_connect")
                            metricsArray.put(item)
                        }
                    }
                } catch (_: Exception) {}

                // 27. Steps Cadence
                try {
                    val cadenceResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = StepsCadenceRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in cadenceResponse.records) {
                        for (sample in record.samples) {
                            val item = JSObject()
                            item.put("metric_code", "cadence")
                            item.put("value", sample.rate)
                            item.put("unit", "rpm")
                            item.put("measured_at", sample.time.toString())
                            item.put("external_id", "hc_cad_${record.metadata.id}_${sample.time.toEpochMilli()}")
                            item.put("source", "health_connect")
                            metricsArray.put(item)
                        }
                    }
                } catch (_: Exception) {}

                // 28. Cycling Cadence
                try {
                    val cycleCadenceResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = CyclingPedalingCadenceRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in cycleCadenceResponse.records) {
                        for (sample in record.samples) {
                            val item = JSObject()
                            item.put("metric_code", "cadence")
                            item.put("value", sample.revolutionsPerMinute)
                            item.put("unit", "rpm")
                            item.put("measured_at", sample.time.toString())
                            item.put("external_id", "hc_cyc_${record.metadata.id}_${sample.time.toEpochMilli()}")
                            item.put("source", "health_connect")
                            metricsArray.put(item)
                        }
                    }
                } catch (_: Exception) {}

                // 29. Wheelchair Pushes
                try {
                    val pushesResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = WheelchairPushesRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in pushesResponse.records) {
                        val item = JSObject()
                        item.put("metric_code", "wheelchair_pushes")
                        item.put("value", record.count.toDouble())
                        item.put("unit", "pushes")
                        item.put("measured_at", record.startTime.toString())
                        item.put("external_id", "hc_push_${record.metadata.id}")
                        item.put("source", "health_connect")
                        metricsArray.put(item)
                    }
                } catch (_: Exception) {}

                // 30. Basal Body Temperature
                try {
                    val bbtResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = BasalBodyTemperatureRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in bbtResponse.records) {
                        val item = JSObject()
                        item.put("metric_code", "basal_body_temp")
                        item.put("value", record.temperature.inCelsius)
                        item.put("unit", "°C")
                        item.put("measured_at", record.time.toString())
                        item.put("external_id", "hc_bbt_${record.metadata.id}")
                        item.put("source", "health_connect")
                        metricsArray.put(item)
                    }
                } catch (_: Exception) {}

                // 31. Menstruation Flow
                try {
                    val flowResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = MenstruationFlowRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in flowResponse.records) {
                        val item = JSObject()
                        item.put("metric_code", "menstruation_flow")
                        item.put("value", record.flow.toDouble())
                        item.put("unit", "flow")
                        item.put("measured_at", record.time.toString())
                        item.put("external_id", "hc_flow_${record.metadata.id}")
                        item.put("source", "health_connect")
                        metricsArray.put(item)
                    }
                } catch (_: Exception) {}

                // 32. Sexual Activity
                try {
                    val sexResponse = client.readRecords(
                        ReadRecordsRequest(
                            recordType = SexualActivityRecord::class,
                            timeRangeFilter = timeRangeFilter
                        )
                    )
                    for (record in sexResponse.records) {
                        val item = JSObject()
                        item.put("metric_code", "sexual_activity")
                        item.put("value", record.protectionUsed.toDouble())
                        item.put("unit", "protection")
                        item.put("measured_at", record.time.toString())
                        item.put("external_id", "hc_sex_${record.metadata.id}")
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
