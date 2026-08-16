package design.fleischer.salus.plugins

import android.content.Context
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.changes.UpsertionChange
import androidx.health.connect.client.permission.HealthPermission
import androidx.health.connect.client.records.*
import androidx.health.connect.client.records.metadata.DataOrigin
import androidx.health.connect.client.request.ChangesTokenRequest
import androidx.health.connect.client.request.ReadRecordsRequest
import androidx.health.connect.client.time.TimeRangeFilter
import org.json.JSONObject
import java.time.Duration
import java.time.Instant
import kotlin.reflect.KClass

/**
 * A single harvested metric value. Single source of truth for the
 * Health Connect → Salus mapping, shared by the foreground Capacitor
 * bridge (HealthConnectPlugin) and the background HealthSyncWorker.
 *
 * Exactly one of [valueNumeric], [valueText], [valueJson] is set, matching
 * the Salus metric `data_type` (number / text / json).
 */
data class HarvestedMetric(
    val metricCode: String,
    val unit: String,
    val measuredAt: String,
    val externalId: String,
    val valueNumeric: Double? = null,
    val valueText: String? = null,
    val valueJson: String? = null,
    val endTime: String? = null,
    val source: String = "health_connect"
)

/** Result of a change-based fetch: upserted metrics, the token the next read advances from,
 *  and whether the supplied token had expired (a fresh baseline + re-import is then required). */
data class ChangesResult(
    val metrics: List<HarvestedMetric>,
    val nextToken: String,
    val expired: Boolean = false
)

/** One bounded page of a time-based harvest plus the cursor to resume the next page from. */
data class HarvestBatch(
    val metrics: List<HarvestedMetric>,
    val nextCursor: String?
)

/** Internal cursor position across the record-type list for [HealthConnectHarvester.harvestBatch]. */
private data class HarvestCursor(
    val typeIndex: Int,
    val pageToken: String?
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
        SexualActivityRecord::class,
        ExerciseSessionRecord::class,
        MindfulnessSessionRecord::class,
        PlannedExerciseSessionRecord::class,
        SkinTemperatureRecord::class,
        NutritionRecord::class,
        MenstruationPeriodRecord::class,
        OvulationTestRecord::class,
        CervicalMucusRecord::class,
        IntermenstrualBleedingRecord::class
    )

    /**
     * Time-based, cursor-paginated read of all records since [sinceIso] (blank = full history).
     * Returns bounded pages of metrics; [HarvestBatch.nextCursor] resumes the next page, or is
     * null when the harvest is exhausted. Used to seed existing Health Connect data; the change
     * API drives every subsequent sync.
     */
    suspend fun harvestBatch(sinceIso: String, cursor: String?, batchSize: Int = 2000): HarvestBatch {
        val client = healthConnectClient ?: return HarvestBatch(emptyList(), null)
        val startTime = try {
            if (sinceIso.isNotBlank()) Instant.parse(sinceIso) else Instant.EPOCH
        } catch (_: Exception) {
            Instant.EPOCH
        }
        val timeRangeFilter = TimeRangeFilter.between(startTime, Instant.now())
        val start = cursor?.let(::decodeCursor) ?: HarvestCursor(0, null)
        val metrics = mutableListOf<HarvestedMetric>()
        var typeIndex = start.typeIndex
        var pageToken = start.pageToken

        while (typeIndex < recordTypes.size && metrics.size < batchSize) {
            val recordType = recordTypes.elementAt(typeIndex)
            try {
                val request = ReadRecordsRequest(
                    recordType = recordType,
                    timeRangeFilter = timeRangeFilter,
                    pageToken = pageToken,
                    pageSize = batchSize
                )
                val response = client.readRecords(request)
                for (record in response.records) {
                    metrics.addAll(toHarvestedMetrics(record))
                }
                pageToken = response.pageToken
                if (pageToken == null) {
                    typeIndex += 1
                }
            } catch (_: Exception) {
                // permission missing or type unsupported — skip, never fail the whole harvest
                typeIndex += 1
                pageToken = null
            }
        }

        val nextCursor = if (typeIndex < recordTypes.size || pageToken != null) {
            encodeCursor(HarvestCursor(typeIndex, pageToken))
        } else {
            null
        }
        return HarvestBatch(metrics, nextCursor)
    }

    private fun encodeCursor(cursor: HarvestCursor): String {
        val obj = org.json.JSONObject()
        obj.put("t", cursor.typeIndex)
        if (cursor.pageToken != null) {
            obj.put("p", cursor.pageToken)
        }
        return obj.toString()
    }

    private fun decodeCursor(raw: String): HarvestCursor {
        return try {
            val obj = org.json.JSONObject(raw)
            HarvestCursor(obj.optInt("t", 0), obj.optString("p", null)?.takeIf { it.isNotBlank() })
        } catch (_: Exception) {
            HarvestCursor(0, null)
        }
    }

    /**
     * Get the current changes token. Only the record types the app actually holds a read
     * permission for are included — otherwise Health Connect throws a SecurityException for
     * the unpermitted types and the token could never be created.
     */
    suspend fun getChangesToken(): String? {
        val client = healthConnectClient ?: return null
        return try {
            val granted = client.permissionController.getGrantedPermissions()
            val grantedTypes = recordTypes.filter { type ->
                HealthPermission.getReadPermission(type) in granted
            }
            if (grantedTypes.isEmpty()) {
                null
            } else {
                client.getChangesToken(ChangesTokenRequest(grantedTypes.toSet(), emptySet<DataOrigin>()))
            }
        } catch (_: Exception) {
            null
        }
    }

    /** Fetch changes since [token]: upserted records → metrics, advancing the token for the next read. */
    suspend fun getChanges(token: String): ChangesResult? {
        val client = healthConnectClient ?: return null
        val metrics = mutableListOf<HarvestedMetric>()
        var currentToken = token
        var expired = false
        return try {
            do {
                val response = client.getChanges(currentToken)
                if (response.changesTokenExpired) {
                    expired = true
                    break
                }
                for (change in response.changes) {
                    if (change is UpsertionChange) {
                        metrics.addAll(toHarvestedMetrics(change.record))
                    }
                }
                currentToken = response.nextChangesToken
            } while (response.hasMore)
            ChangesResult(metrics, currentToken, expired)
        } catch (_: Exception) {
            null
        }
    }

    /** Maps a single Health Connect record to its Salus metric(s). Shared by both sync paths. */
    private fun toHarvestedMetrics(record: Record): List<HarvestedMetric> = when (record) {
        is StepsRecord -> listOf(
            HarvestedMetric("steps", "count", record.startTime.toString(), "hc_steps_${record.metadata.id}", valueNumeric = record.count.toDouble())
        )
        is HeartRateRecord -> record.samples.map { sample ->
            HarvestedMetric("heart_rate", "bpm", sample.time.toString(), "hc_hr_${record.metadata.id}_${sample.time.toEpochMilli()}", valueNumeric = sample.beatsPerMinute.toDouble())
        }
        is RestingHeartRateRecord -> listOf(
            HarvestedMetric("resting_heart_rate", "bpm", record.time.toString(), "hc_rhr_${record.metadata.id}", valueNumeric = record.beatsPerMinute.toDouble())
        )
        is SleepSessionRecord -> listOf(
            HarvestedMetric(
                "sleep",
                "minutes",
                record.endTime.toString(),
                "hc_sleep_${record.metadata.id}",
                valueNumeric = Duration.between(record.startTime, record.endTime).toMinutes().toDouble()
            )
        )
        is TotalCaloriesBurnedRecord -> listOf(
            HarvestedMetric("calories_burned", "kcal", record.startTime.toString(), "hc_cal_${record.metadata.id}", valueNumeric = record.energy.inKilocalories)
        )
        is WeightRecord -> listOf(
            HarvestedMetric("weight", "kg", record.time.toString(), "hc_weight_${record.metadata.id}", valueNumeric = record.weight.inKilograms)
        )
        is BloodPressureRecord -> listOf(
            HarvestedMetric("systolic_bp", "mmHg", record.time.toString(), "hc_bps_${record.metadata.id}", valueNumeric = record.systolic.inMillimetersOfMercury),
            HarvestedMetric("diastolic_bp", "mmHg", record.time.toString(), "hc_bpd_${record.metadata.id}", valueNumeric = record.diastolic.inMillimetersOfMercury)
        )
        is OxygenSaturationRecord -> listOf(
            HarvestedMetric("spo2", "%", record.time.toString(), "hc_spo2_${record.metadata.id}", valueNumeric = record.percentage.value)
        )
        is ActiveCaloriesBurnedRecord -> listOf(
            HarvestedMetric("active_calories", "kcal", record.startTime.toString(), "hc_actcal_${record.metadata.id}", valueNumeric = record.energy.inKilocalories)
        )
        is DistanceRecord -> listOf(
            HarvestedMetric("distance", "km", record.startTime.toString(), "hc_dist_${record.metadata.id}", valueNumeric = record.distance.inKilometers)
        )
        is ElevationGainedRecord -> listOf(
            HarvestedMetric("elevation_gained", "m", record.startTime.toString(), "hc_elev_${record.metadata.id}", valueNumeric = record.elevation.inMeters)
        )
        is FloorsClimbedRecord -> listOf(
            HarvestedMetric("floors_climbed", "floors", record.startTime.toString(), "hc_floors_${record.metadata.id}", valueNumeric = record.floors.toDouble())
        )
        is Vo2MaxRecord -> listOf(
            HarvestedMetric("vo2_max", "ml/kg/min", record.time.toString(), "hc_vo2_${record.metadata.id}", valueNumeric = record.vo2MillilitersPerMinuteKilogram)
        )
        is RespiratoryRateRecord -> listOf(
            HarvestedMetric("respiratory_rate", "rpm", record.time.toString(), "hc_resp_${record.metadata.id}", valueNumeric = record.rate)
        )
        is BodyTemperatureRecord -> listOf(
            HarvestedMetric("body_temperature", "°C", record.time.toString(), "hc_temp_${record.metadata.id}", valueNumeric = record.temperature.inCelsius)
        )
        is HeightRecord -> listOf(
            HarvestedMetric("height", "cm", record.time.toString(), "hc_height_${record.metadata.id}", valueNumeric = record.height.inMeters * 100)
        )
        is BodyFatRecord -> listOf(
            HarvestedMetric("body_fat", "%", record.time.toString(), "hc_bf_${record.metadata.id}", valueNumeric = record.percentage.value)
        )
        is HeartRateVariabilityRmssdRecord -> listOf(
            HarvestedMetric("hrv", "ms", record.time.toString(), "hc_hrv_${record.metadata.id}", valueNumeric = record.heartRateVariabilityMillis)
        )
        is HydrationRecord -> listOf(
            HarvestedMetric("water", "ml", record.startTime.toString(), "hc_water_${record.metadata.id}", valueNumeric = record.volume.inLiters * 1000)
        )
        is BloodGlucoseRecord -> listOf(
            HarvestedMetric("blood_glucose", "mg/dL", record.time.toString(), "hc_bg_${record.metadata.id}", valueNumeric = record.level.inMilligramsPerDeciliter)
        )
        is BoneMassRecord -> listOf(
            HarvestedMetric("bone_mass", "kg", record.time.toString(), "hc_bone_${record.metadata.id}", valueNumeric = record.mass.inKilograms)
        )
        is LeanBodyMassRecord -> listOf(
            HarvestedMetric("lean_body_mass", "kg", record.time.toString(), "hc_lean_${record.metadata.id}", valueNumeric = record.mass.inKilograms)
        )
        is BodyWaterMassRecord -> listOf(
            HarvestedMetric("body_water_mass", "kg", record.time.toString(), "hc_bwm_${record.metadata.id}", valueNumeric = record.mass.inKilograms)
        )
        is BasalMetabolicRateRecord -> listOf(
            HarvestedMetric("bmr", "kcal", record.time.toString(), "hc_bmr_${record.metadata.id}", valueNumeric = record.basalMetabolicRate.inKilocaloriesPerDay)
        )
        is SpeedRecord -> record.samples.map { sample ->
            HarvestedMetric("speed", "km/h", sample.time.toString(), "hc_spd_${record.metadata.id}_${sample.time.toEpochMilli()}", valueNumeric = sample.speed.inKilometersPerHour)
        }
        is PowerRecord -> record.samples.map { sample ->
            HarvestedMetric("power", "W", sample.time.toString(), "hc_pwr_${record.metadata.id}_${sample.time.toEpochMilli()}", valueNumeric = sample.power.inWatts)
        }
        is StepsCadenceRecord -> record.samples.map { sample ->
            HarvestedMetric("cadence", "rpm", sample.time.toString(), "hc_cad_${record.metadata.id}_${sample.time.toEpochMilli()}", valueNumeric = sample.rate.toDouble())
        }
        is CyclingPedalingCadenceRecord -> record.samples.map { sample ->
            HarvestedMetric("cadence", "rpm", sample.time.toString(), "hc_cyc_${record.metadata.id}_${sample.time.toEpochMilli()}", valueNumeric = sample.revolutionsPerMinute.toDouble())
        }
        is WheelchairPushesRecord -> listOf(
            HarvestedMetric("wheelchair_pushes", "pushes", record.startTime.toString(), "hc_push_${record.metadata.id}", valueNumeric = record.count.toDouble())
        )
        is BasalBodyTemperatureRecord -> listOf(
            HarvestedMetric("basal_body_temp", "°C", record.time.toString(), "hc_bbt_${record.metadata.id}", valueNumeric = record.temperature.inCelsius)
        )
        is ExerciseSessionRecord -> listOf(
            HarvestedMetric(
                "exercise",
                "minutes",
                record.endTime.toString(),
                "hc_ex_${record.metadata.id}",
                valueNumeric = Duration.between(record.startTime, record.endTime).toMinutes().toDouble()
            )
        )
        is MindfulnessSessionRecord -> listOf(
            HarvestedMetric(
                "mindfulness",
                "minutes",
                record.endTime.toString(),
                "hc_mind_${record.metadata.id}",
                valueNumeric = Duration.between(record.startTime, record.endTime).toMinutes().toDouble()
            )
        )
        is PlannedExerciseSessionRecord -> listOf(
            HarvestedMetric(
                "planned_exercise",
                "minutes",
                record.endTime.toString(),
                "hc_pex_${record.metadata.id}",
                valueNumeric = Duration.between(record.startTime, record.endTime).toMinutes().toDouble()
            )
        )
        is SkinTemperatureRecord -> record.deltas.map { delta ->
            HarvestedMetric(
                "skin_temperature",
                "°C",
                delta.time.toString(),
                "hc_skin_${record.metadata.id}_${delta.time.toEpochMilli()}",
                valueNumeric = delta.delta.inCelsius
            )
        }
        is NutritionRecord -> listOf(
            HarvestedMetric(
                "nutrition",
                "",
                record.startTime.toString(),
                "hc_nut_${record.metadata.id}",
                valueJson = nutritionJson(record)
            )
        )
        is MenstruationPeriodRecord -> listOf(
            HarvestedMetric(
                "menstruation_period",
                "",
                record.startTime.toString(),
                "hc_mp_${record.metadata.id}",
                valueText = "period",
                endTime = record.endTime.toString()
            )
        )
        is MenstruationFlowRecord -> listOf(
            HarvestedMetric("menstruation_flow", "", record.time.toString(), "hc_flow_${record.metadata.id}", valueText = menstruationFlowLabel(record.flow))
        )
        is OvulationTestRecord -> listOf(
            HarvestedMetric("ovulation_test", "", record.time.toString(), "hc_ov_${record.metadata.id}", valueText = ovulationResultLabel(record.result))
        )
        is CervicalMucusRecord -> listOf(
            HarvestedMetric("cervical_mucus", "", record.time.toString(), "hc_cm_${record.metadata.id}", valueText = cervicalMucusLabel(record.appearance, record.sensation))
        )
        is IntermenstrualBleedingRecord -> listOf(
            HarvestedMetric("spotting", "", record.time.toString(), "hc_imb_${record.metadata.id}", valueText = "spotting")
        )
        is SexualActivityRecord -> listOf(
            HarvestedMetric("sexual_activity", "", record.time.toString(), "hc_sex_${record.metadata.id}", valueText = protectionUsedLabel(record.protectionUsed))
        )
        else -> emptyList()
    }

    private fun menstruationFlowLabel(flow: Int): String = when (flow) {
        MenstruationFlowRecord.FLOW_LIGHT -> "light"
        MenstruationFlowRecord.FLOW_MEDIUM -> "medium"
        MenstruationFlowRecord.FLOW_HEAVY -> "heavy"
        else -> "unknown"
    }

    private fun ovulationResultLabel(result: Int): String = when (result) {
        OvulationTestRecord.RESULT_POSITIVE -> "positive"
        OvulationTestRecord.RESULT_HIGH -> "high"
        OvulationTestRecord.RESULT_NEGATIVE -> "negative"
        OvulationTestRecord.RESULT_INCONCLUSIVE -> "inconclusive"
        else -> "unknown"
    }

    private fun cervicalMucusLabel(appearance: Int, sensation: Int): String = when (appearance) {
        CervicalMucusRecord.APPEARANCE_CREAMY -> "creamy"
        CervicalMucusRecord.APPEARANCE_DRY -> "dry"
        CervicalMucusRecord.APPEARANCE_EGG_WHITE -> "egg_white"
        CervicalMucusRecord.APPEARANCE_STICKY -> "sticky"
        CervicalMucusRecord.APPEARANCE_WATERY -> "watery"
        CervicalMucusRecord.APPEARANCE_UNUSUAL -> "unusual"
        else -> when (sensation) {
            CervicalMucusRecord.SENSATION_LIGHT -> "light"
            CervicalMucusRecord.SENSATION_MEDIUM -> "medium"
            CervicalMucusRecord.SENSATION_HEAVY -> "heavy"
            else -> "unknown"
        }
    }

    private fun protectionUsedLabel(protection: Int): String = when (protection) {
        SexualActivityRecord.PROTECTION_USED_PROTECTED -> "protected"
        SexualActivityRecord.PROTECTION_USED_UNPROTECTED -> "unprotected"
        else -> "unknown"
    }

    private fun nutritionJson(record: NutritionRecord): String {
        val obj = JSONObject()
        obj.put("calories", record.energy?.inKilocalories ?: 0.0)
        obj.put("protein_grams", record.protein?.inGrams ?: 0.0)
        obj.put("carbs_grams", record.totalCarbohydrate?.inGrams ?: 0.0)
        obj.put("fat_grams", record.totalFat?.inGrams ?: 0.0)
        return obj.toString()
    }
}
