package design.fleischer.salus.plugins

import android.content.Context
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.changes.UpsertionChange
import androidx.health.connect.client.records.*
import androidx.health.connect.client.records.metadata.DataOrigin
import androidx.health.connect.client.request.ChangesTokenRequest
import androidx.health.connect.client.request.ReadRecordsRequest
import androidx.health.connect.client.time.TimeRangeFilter
import java.time.Duration
import java.time.Instant
import kotlin.reflect.KClass

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

/** Result of a change-based fetch: upserted metrics and the token the next read advances from. */
data class ChangesResult(
    val metrics: List<HarvestedMetric>,
    val nextToken: String
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

    /** All record types Salus harvests. Single source for the time- and change-based reads. */
    private val recordTypes: Set<KClass<out Record>> = setOf(
        StepsRecord::class,
        HeartRateRecord::class,
        RestingHeartRateRecord::class,
        SleepSessionRecord::class,
        TotalCaloriesBurnedRecord::class,
        WeightRecord::class,
        BloodPressureRecord::class,
        OxygenSaturationRecord::class,
        ActiveCaloriesBurnedRecord::class,
        DistanceRecord::class,
        ElevationGainedRecord::class,
        FloorsClimbedRecord::class,
        Vo2MaxRecord::class,
        RespiratoryRateRecord::class,
        BodyTemperatureRecord::class,
        HeightRecord::class,
        BodyFatRecord::class,
        HeartRateVariabilityRmssdRecord::class,
        HydrationRecord::class,
        BloodGlucoseRecord::class,
        BoneMassRecord::class,
        LeanBodyMassRecord::class,
        BodyWaterMassRecord::class,
        BasalMetabolicRateRecord::class,
        SpeedRecord::class,
        PowerRecord::class,
        StepsCadenceRecord::class,
        CyclingPedalingCadenceRecord::class,
        WheelchairPushesRecord::class,
        BasalBodyTemperatureRecord::class,
        MenstruationFlowRecord::class,
        SexualActivityRecord::class
    )

    /**
     * Time-based read of all records since [sinceIso] (blank = full history). Used once to seed
     * existing Health Connect data; the change API drives every subsequent sync.
     */
    suspend fun harvest(sinceIso: String): List<HarvestedMetric> {
        val client = healthConnectClient ?: return emptyList()
        val startTime = try {
            if (sinceIso.isNotBlank()) Instant.parse(sinceIso) else Instant.EPOCH
        } catch (_: Exception) {
            Instant.EPOCH
        }
        val timeRangeFilter = TimeRangeFilter.between(startTime, Instant.now())
        val metrics = mutableListOf<HarvestedMetric>()
        for (recordType in recordTypes) {
            try {
                for (record in readAllRecords(client, recordType, timeRangeFilter)) {
                    metrics.addAll(toHarvestedMetrics(record))
                }
            } catch (_: Exception) {
                // permission missing or type unsupported — skip, never fail the whole harvest
            }
        }
        return metrics
    }

    /** Get the current changes token (the baseline the change feed advances from). */
    suspend fun getChangesToken(): String? {
        val client = healthConnectClient ?: return null
        return try {
            client.getChangesToken(ChangesTokenRequest(recordTypes, emptySet<DataOrigin>()))
        } catch (_: Exception) {
            null
        }
    }

    /** Fetch changes since [token]: upserted records → metrics, advancing the token for the next read. */
    suspend fun getChanges(token: String): ChangesResult? {
        val client = healthConnectClient ?: return null
        val metrics = mutableListOf<HarvestedMetric>()
        var currentToken = token
        return try {
            do {
                val response = client.getChanges(currentToken)
                for (change in response.changes) {
                    if (change is UpsertionChange) {
                        metrics.addAll(toHarvestedMetrics(change.record))
                    }
                }
                currentToken = response.nextChangesToken
            } while (response.hasMore)
            ChangesResult(metrics, currentToken)
        } catch (_: Exception) {
            null
        }
    }

    /** Maps a single Health Connect record to its Salus metric(s). Shared by both sync paths. */
    private fun toHarvestedMetrics(record: Record): List<HarvestedMetric> = when (record) {
        is StepsRecord -> listOf(
            HarvestedMetric("steps", record.count.toDouble(), "count", record.startTime.toString(), "hc_steps_${record.metadata.id}")
        )
        is HeartRateRecord -> record.samples.map { sample ->
            HarvestedMetric("heart_rate", sample.beatsPerMinute.toDouble(), "bpm", sample.time.toString(), "hc_hr_${record.metadata.id}_${sample.time.toEpochMilli()}")
        }
        is RestingHeartRateRecord -> listOf(
            HarvestedMetric("resting_heart_rate", record.beatsPerMinute.toDouble(), "bpm", record.time.toString(), "hc_rhr_${record.metadata.id}")
        )
        is SleepSessionRecord -> listOf(
            HarvestedMetric(
                "sleep",
                Duration.between(record.startTime, record.endTime).toMinutes().toDouble(),
                "minutes",
                record.endTime.toString(),
                "hc_sleep_${record.metadata.id}"
            )
        )
        is TotalCaloriesBurnedRecord -> listOf(
            HarvestedMetric("calories_burned", record.energy.inKilocalories, "kcal", record.startTime.toString(), "hc_cal_${record.metadata.id}")
        )
        is WeightRecord -> listOf(
            HarvestedMetric("weight", record.weight.inKilograms, "kg", record.time.toString(), "hc_weight_${record.metadata.id}")
        )
        is BloodPressureRecord -> listOf(
            HarvestedMetric("systolic_bp", record.systolic.inMillimetersOfMercury, "mmHg", record.time.toString(), "hc_bps_${record.metadata.id}"),
            HarvestedMetric("diastolic_bp", record.diastolic.inMillimetersOfMercury, "mmHg", record.time.toString(), "hc_bpd_${record.metadata.id}")
        )
        is OxygenSaturationRecord -> listOf(
            HarvestedMetric("spo2", record.percentage.value, "%", record.time.toString(), "hc_spo2_${record.metadata.id}")
        )
        is ActiveCaloriesBurnedRecord -> listOf(
            HarvestedMetric("active_calories", record.energy.inKilocalories, "kcal", record.startTime.toString(), "hc_actcal_${record.metadata.id}")
        )
        is DistanceRecord -> listOf(
            HarvestedMetric("distance", record.distance.inKilometers, "km", record.startTime.toString(), "hc_dist_${record.metadata.id}")
        )
        is ElevationGainedRecord -> listOf(
            HarvestedMetric("elevation_gained", record.elevation.inMeters, "m", record.startTime.toString(), "hc_elev_${record.metadata.id}")
        )
        is FloorsClimbedRecord -> listOf(
            HarvestedMetric("floors_climbed", record.floors.toDouble(), "floors", record.startTime.toString(), "hc_floors_${record.metadata.id}")
        )
        is Vo2MaxRecord -> listOf(
            HarvestedMetric("vo2_max", record.vo2MillilitersPerMinuteKilogram, "ml/kg/min", record.time.toString(), "hc_vo2_${record.metadata.id}")
        )
        is RespiratoryRateRecord -> listOf(
            HarvestedMetric("respiratory_rate", record.rate, "rpm", record.time.toString(), "hc_resp_${record.metadata.id}")
        )
        is BodyTemperatureRecord -> listOf(
            HarvestedMetric("body_temperature", record.temperature.inCelsius, "°C", record.time.toString(), "hc_temp_${record.metadata.id}")
        )
        is HeightRecord -> listOf(
            HarvestedMetric("height", record.height.inMeters * 100, "cm", record.time.toString(), "hc_height_${record.metadata.id}")
        )
        is BodyFatRecord -> listOf(
            HarvestedMetric("body_fat", record.percentage.value, "%", record.time.toString(), "hc_bf_${record.metadata.id}")
        )
        is HeartRateVariabilityRmssdRecord -> listOf(
            HarvestedMetric("hrv", record.heartRateVariabilityMillis, "ms", record.time.toString(), "hc_hrv_${record.metadata.id}")
        )
        is HydrationRecord -> listOf(
            HarvestedMetric("water", record.volume.inLiters * 1000, "ml", record.startTime.toString(), "hc_water_${record.metadata.id}")
        )
        is BloodGlucoseRecord -> listOf(
            HarvestedMetric("blood_glucose", record.level.inMilligramsPerDeciliter, "mg/dL", record.time.toString(), "hc_bg_${record.metadata.id}")
        )
        is BoneMassRecord -> listOf(
            HarvestedMetric("bone_mass", record.mass.inKilograms, "kg", record.time.toString(), "hc_bone_${record.metadata.id}")
        )
        is LeanBodyMassRecord -> listOf(
            HarvestedMetric("lean_body_mass", record.mass.inKilograms, "kg", record.time.toString(), "hc_lean_${record.metadata.id}")
        )
        is BodyWaterMassRecord -> listOf(
            HarvestedMetric("body_water_mass", record.mass.inKilograms, "kg", record.time.toString(), "hc_bwm_${record.metadata.id}")
        )
        is BasalMetabolicRateRecord -> listOf(
            HarvestedMetric("bmr", record.basalMetabolicRate.inKilocaloriesPerDay, "kcal", record.time.toString(), "hc_bmr_${record.metadata.id}")
        )
        is SpeedRecord -> record.samples.map { sample ->
            HarvestedMetric("speed", sample.speed.inKilometersPerHour, "km/h", sample.time.toString(), "hc_spd_${record.metadata.id}_${sample.time.toEpochMilli()}")
        }
        is PowerRecord -> record.samples.map { sample ->
            HarvestedMetric("power", sample.power.inWatts, "W", sample.time.toString(), "hc_pwr_${record.metadata.id}_${sample.time.toEpochMilli()}")
        }
        is StepsCadenceRecord -> record.samples.map { sample ->
            HarvestedMetric("cadence", sample.rate.toDouble(), "rpm", sample.time.toString(), "hc_cad_${record.metadata.id}_${sample.time.toEpochMilli()}")
        }
        is CyclingPedalingCadenceRecord -> record.samples.map { sample ->
            HarvestedMetric("cadence", sample.revolutionsPerMinute.toDouble(), "rpm", sample.time.toString(), "hc_cyc_${record.metadata.id}_${sample.time.toEpochMilli()}")
        }
        is WheelchairPushesRecord -> listOf(
            HarvestedMetric("wheelchair_pushes", record.count.toDouble(), "pushes", record.startTime.toString(), "hc_push_${record.metadata.id}")
        )
        is BasalBodyTemperatureRecord -> listOf(
            HarvestedMetric("basal_body_temp", record.temperature.inCelsius, "°C", record.time.toString(), "hc_bbt_${record.metadata.id}")
        )
        is MenstruationFlowRecord -> listOf(
            HarvestedMetric("menstruation_flow", record.flow.toDouble(), "flow", record.time.toString(), "hc_flow_${record.metadata.id}")
        )
        is SexualActivityRecord -> listOf(
            HarvestedMetric("sexual_activity", record.protectionUsed.toDouble(), "protection", record.time.toString(), "hc_sex_${record.metadata.id}")
        )
        else -> emptyList()
    }

    private suspend fun readAllRecords(
        client: HealthConnectClient,
        recordType: KClass<out Record>,
        timeRangeFilter: TimeRangeFilter
    ): List<Record> {
        val allRecords = mutableListOf<Record>()
        var pageToken: String? = null
        do {
            val request = ReadRecordsRequest(
                recordType = recordType,
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
