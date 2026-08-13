package design.fleischer.salus.plugins

import android.content.Context
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.records.*
import androidx.health.connect.client.request.ReadRecordsRequest
import androidx.health.connect.client.time.TimeRangeFilter
import java.time.Duration
import java.time.Instant
import java.time.temporal.ChronoUnit

/**
 * A single harvested metric value. Single source of truth for the
 * Health Connect → Salus mapping, shared by the foreground Capacitor
 * bridge (HealthConnectPlugin) and the background HealthSyncWorker.
 */
data class HarvestedMetric(
    val metricCode: String,
    val value: Double,
    val unit: String,
    val measuredAt: String,
    val externalId: String,
    val source: String = "health_connect"
)

class HealthConnectHarvester(private val context: Context) {

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

    suspend fun harvest(sinceIso: String): List<HarvestedMetric> {
        val client = healthConnectClient ?: return emptyList()

        val startTime = try {
            if (sinceIso.isNotBlank()) Instant.parse(sinceIso) else Instant.now().minus(30, ChronoUnit.DAYS)
        } catch (e: Exception) {
            Instant.now().minus(30, ChronoUnit.DAYS)
        }
        val timeRangeFilter = TimeRangeFilter.between(startTime, Instant.now())

        val metrics = mutableListOf<HarvestedMetric>()

        // 1. Steps
        try {
            for (record in readAllRecords<StepsRecord>(client, timeRangeFilter)) {
                metrics.add(HarvestedMetric("steps", record.count.toDouble(), "count", record.startTime.toString(), "hc_steps_${record.metadata.id}"))
            }
        } catch (_: Exception) {}

        // 2. Heart Rate (per-sample)
        try {
            for (record in readAllRecords<HeartRateRecord>(client, timeRangeFilter)) {
                for (sample in record.samples) {
                    metrics.add(HarvestedMetric("heart_rate", sample.beatsPerMinute.toDouble(), "bpm", sample.time.toString(), "hc_hr_${record.metadata.id}_${sample.time.toEpochMilli()}"))
                }
            }
        } catch (_: Exception) {}

        // 3. Resting Heart Rate
        try {
            for (record in readAllRecords<RestingHeartRateRecord>(client, timeRangeFilter)) {
                metrics.add(HarvestedMetric("resting_heart_rate", record.beatsPerMinute.toDouble(), "bpm", record.time.toString(), "hc_rhr_${record.metadata.id}"))
            }
        } catch (_: Exception) {}

        // 4. Sleep
        try {
            for (record in readAllRecords<SleepSessionRecord>(client, timeRangeFilter)) {
                val durationMinutes = Duration.between(record.startTime, record.endTime).toMinutes().toDouble()
                metrics.add(HarvestedMetric("sleep", durationMinutes, "minutes", record.endTime.toString(), "hc_sleep_${record.metadata.id}"))
            }
        } catch (_: Exception) {}

        // 5. Total Calories Burned
        try {
            for (record in readAllRecords<TotalCaloriesBurnedRecord>(client, timeRangeFilter)) {
                metrics.add(HarvestedMetric("calories_burned", record.energy.inKilocalories, "kcal", record.startTime.toString(), "hc_cal_${record.metadata.id}"))
            }
        } catch (_: Exception) {}

        // 6. Weight
        try {
            for (record in readAllRecords<WeightRecord>(client, timeRangeFilter)) {
                metrics.add(HarvestedMetric("weight", record.weight.inKilograms, "kg", record.time.toString(), "hc_weight_${record.metadata.id}"))
            }
        } catch (_: Exception) {}

        // 7. Blood Pressure (two metrics per record)
        try {
            for (record in readAllRecords<BloodPressureRecord>(client, timeRangeFilter)) {
                metrics.add(HarvestedMetric("systolic_bp", record.systolic.inMillimetersOfMercury, "mmHg", record.time.toString(), "hc_bps_${record.metadata.id}"))
                metrics.add(HarvestedMetric("diastolic_bp", record.diastolic.inMillimetersOfMercury, "mmHg", record.time.toString(), "hc_bpd_${record.metadata.id}"))
            }
        } catch (_: Exception) {}

        // 8. Oxygen Saturation (SpO2)
        try {
            for (record in readAllRecords<OxygenSaturationRecord>(client, timeRangeFilter)) {
                metrics.add(HarvestedMetric("spo2", record.percentage.value, "%", record.time.toString(), "hc_spo2_${record.metadata.id}"))
            }
        } catch (_: Exception) {}

        // 9. Active Calories Burned
        try {
            for (record in readAllRecords<ActiveCaloriesBurnedRecord>(client, timeRangeFilter)) {
                metrics.add(HarvestedMetric("active_calories", record.energy.inKilocalories, "kcal", record.startTime.toString(), "hc_actcal_${record.metadata.id}"))
            }
        } catch (_: Exception) {}

        // 10. Distance
        try {
            for (record in readAllRecords<DistanceRecord>(client, timeRangeFilter)) {
                metrics.add(HarvestedMetric("distance", record.distance.inKilometers, "km", record.startTime.toString(), "hc_dist_${record.metadata.id}"))
            }
        } catch (_: Exception) {}

        // 11. Elevation Gained
        try {
            for (record in readAllRecords<ElevationGainedRecord>(client, timeRangeFilter)) {
                metrics.add(HarvestedMetric("elevation_gained", record.elevation.inMeters, "m", record.startTime.toString(), "hc_elev_${record.metadata.id}"))
            }
        } catch (_: Exception) {}

        // 12. Floors Climbed
        try {
            for (record in readAllRecords<FloorsClimbedRecord>(client, timeRangeFilter)) {
                metrics.add(HarvestedMetric("floors_climbed", record.floors.toDouble(), "floors", record.startTime.toString(), "hc_floors_${record.metadata.id}"))
            }
        } catch (_: Exception) {}

        // 13. VO2 Max
        try {
            for (record in readAllRecords<Vo2MaxRecord>(client, timeRangeFilter)) {
                metrics.add(HarvestedMetric("vo2_max", record.vo2MillilitersPerMinuteKilogram, "ml/kg/min", record.time.toString(), "hc_vo2_${record.metadata.id}"))
            }
        } catch (_: Exception) {}

        // 14. Respiratory Rate
        try {
            for (record in readAllRecords<RespiratoryRateRecord>(client, timeRangeFilter)) {
                metrics.add(HarvestedMetric("respiratory_rate", record.rate, "rpm", record.time.toString(), "hc_resp_${record.metadata.id}"))
            }
        } catch (_: Exception) {}

        // 15. Body Temperature
        try {
            for (record in readAllRecords<BodyTemperatureRecord>(client, timeRangeFilter)) {
                metrics.add(HarvestedMetric("body_temperature", record.temperature.inCelsius, "°C", record.time.toString(), "hc_temp_${record.metadata.id}"))
            }
        } catch (_: Exception) {}

        // 16. Height
        try {
            for (record in readAllRecords<HeightRecord>(client, timeRangeFilter)) {
                metrics.add(HarvestedMetric("height", record.height.inMeters * 100, "cm", record.time.toString(), "hc_height_${record.metadata.id}"))
            }
        } catch (_: Exception) {}

        // 17. Body Fat
        try {
            for (record in readAllRecords<BodyFatRecord>(client, timeRangeFilter)) {
                metrics.add(HarvestedMetric("body_fat", record.percentage.value, "%", record.time.toString(), "hc_bf_${record.metadata.id}"))
            }
        } catch (_: Exception) {}

        // 18. Heart Rate Variability (RMSSD)
        try {
            for (record in readAllRecords<HeartRateVariabilityRmssdRecord>(client, timeRangeFilter)) {
                metrics.add(HarvestedMetric("hrv", record.heartRateVariabilityMillis, "ms", record.time.toString(), "hc_hrv_${record.metadata.id}"))
            }
        } catch (_: Exception) {}

        // 19. Hydration (Water)
        try {
            val response = client.readRecords(ReadRecordsRequest(recordType = HydrationRecord::class, timeRangeFilter = timeRangeFilter))
            for (record in response.records) {
                metrics.add(HarvestedMetric("water", record.volume.inLiters * 1000, "ml", record.startTime.toString(), "hc_water_${record.metadata.id}"))
            }
        } catch (_: Exception) {}

        // 20. Blood Glucose
        try {
            val response = client.readRecords(ReadRecordsRequest(recordType = BloodGlucoseRecord::class, timeRangeFilter = timeRangeFilter))
            for (record in response.records) {
                metrics.add(HarvestedMetric("blood_glucose", record.level.inMilligramsPerDeciliter, "mg/dL", record.time.toString(), "hc_bg_${record.metadata.id}"))
            }
        } catch (_: Exception) {}

        // 21. Bone Mass
        try {
            val response = client.readRecords(ReadRecordsRequest(recordType = BoneMassRecord::class, timeRangeFilter = timeRangeFilter))
            for (record in response.records) {
                metrics.add(HarvestedMetric("bone_mass", record.mass.inKilograms, "kg", record.time.toString(), "hc_bone_${record.metadata.id}"))
            }
        } catch (_: Exception) {}

        // 22. Lean Body Mass
        try {
            val response = client.readRecords(ReadRecordsRequest(recordType = LeanBodyMassRecord::class, timeRangeFilter = timeRangeFilter))
            for (record in response.records) {
                metrics.add(HarvestedMetric("lean_body_mass", record.mass.inKilograms, "kg", record.time.toString(), "hc_lean_${record.metadata.id}"))
            }
        } catch (_: Exception) {}

        // 23. Body Water Mass
        try {
            val response = client.readRecords(ReadRecordsRequest(recordType = BodyWaterMassRecord::class, timeRangeFilter = timeRangeFilter))
            for (record in response.records) {
                metrics.add(HarvestedMetric("body_water_mass", record.mass.inKilograms, "kg", record.time.toString(), "hc_bwm_${record.metadata.id}"))
            }
        } catch (_: Exception) {}

        // 24. Basal Metabolic Rate (BMR)
        try {
            val response = client.readRecords(ReadRecordsRequest(recordType = BasalMetabolicRateRecord::class, timeRangeFilter = timeRangeFilter))
            for (record in response.records) {
                metrics.add(HarvestedMetric("bmr", record.basalMetabolicRate.inKilocaloriesPerDay, "kcal", record.time.toString(), "hc_bmr_${record.metadata.id}"))
            }
        } catch (_: Exception) {}

        // 25. Speed (per-sample)
        try {
            val response = client.readRecords(ReadRecordsRequest(recordType = SpeedRecord::class, timeRangeFilter = timeRangeFilter))
            for (record in response.records) {
                for (sample in record.samples) {
                    metrics.add(HarvestedMetric("speed", sample.speed.inKilometersPerHour, "km/h", sample.time.toString(), "hc_spd_${record.metadata.id}_${sample.time.toEpochMilli()}"))
                }
            }
        } catch (_: Exception) {}

        // 26. Power (per-sample)
        try {
            val response = client.readRecords(ReadRecordsRequest(recordType = PowerRecord::class, timeRangeFilter = timeRangeFilter))
            for (record in response.records) {
                for (sample in record.samples) {
                    metrics.add(HarvestedMetric("power", sample.power.inWatts, "W", sample.time.toString(), "hc_pwr_${record.metadata.id}_${sample.time.toEpochMilli()}"))
                }
            }
        } catch (_: Exception) {}

        // 27. Steps Cadence (per-sample)
        try {
            val response = client.readRecords(ReadRecordsRequest(recordType = StepsCadenceRecord::class, timeRangeFilter = timeRangeFilter))
            for (record in response.records) {
                for (sample in record.samples) {
                    metrics.add(HarvestedMetric("cadence", sample.rate.toDouble(), "rpm", sample.time.toString(), "hc_cad_${record.metadata.id}_${sample.time.toEpochMilli()}"))
                }
            }
        } catch (_: Exception) {}

        // 28. Cycling Cadence (per-sample)
        try {
            val response = client.readRecords(ReadRecordsRequest(recordType = CyclingPedalingCadenceRecord::class, timeRangeFilter = timeRangeFilter))
            for (record in response.records) {
                for (sample in record.samples) {
                    metrics.add(HarvestedMetric("cadence", sample.revolutionsPerMinute.toDouble(), "rpm", sample.time.toString(), "hc_cyc_${record.metadata.id}_${sample.time.toEpochMilli()}"))
                }
            }
        } catch (_: Exception) {}

        // 29. Wheelchair Pushes
        try {
            val response = client.readRecords(ReadRecordsRequest(recordType = WheelchairPushesRecord::class, timeRangeFilter = timeRangeFilter))
            for (record in response.records) {
                metrics.add(HarvestedMetric("wheelchair_pushes", record.count.toDouble(), "pushes", record.startTime.toString(), "hc_push_${record.metadata.id}"))
            }
        } catch (_: Exception) {}

        // 30. Basal Body Temperature
        try {
            val response = client.readRecords(ReadRecordsRequest(recordType = BasalBodyTemperatureRecord::class, timeRangeFilter = timeRangeFilter))
            for (record in response.records) {
                metrics.add(HarvestedMetric("basal_body_temp", record.temperature.inCelsius, "°C", record.time.toString(), "hc_bbt_${record.metadata.id}"))
            }
        } catch (_: Exception) {}

        // 31. Menstruation Flow
        try {
            val response = client.readRecords(ReadRecordsRequest(recordType = MenstruationFlowRecord::class, timeRangeFilter = timeRangeFilter))
            for (record in response.records) {
                metrics.add(HarvestedMetric("menstruation_flow", record.flow.toDouble(), "flow", record.time.toString(), "hc_flow_${record.metadata.id}"))
            }
        } catch (_: Exception) {}

        // 32. Sexual Activity
        try {
            val response = client.readRecords(ReadRecordsRequest(recordType = SexualActivityRecord::class, timeRangeFilter = timeRangeFilter))
            for (record in response.records) {
                metrics.add(HarvestedMetric("sexual_activity", record.protectionUsed.toDouble(), "protection", record.time.toString(), "hc_sex_${record.metadata.id}"))
            }
        } catch (_: Exception) {}

        return metrics
    }

    private suspend inline fun <reified T : Record> readAllRecords(
        client: HealthConnectClient,
        timeRangeFilter: TimeRangeFilter
    ): List<T> {
        val allRecords = mutableListOf<T>()
        var pageToken: String? = null
        do {
            val request = ReadRecordsRequest(
                recordType = T::class,
                timeRangeFilter = timeRangeFilter,
                pageToken = pageToken,
                pageSize = 5000
            )
            val response = client.readRecords(request)
            allRecords.addAll(response.records)
            pageToken = response.pageToken
        } while (pageToken != null)
        return allRecords
    }
}
