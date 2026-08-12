import logging
import math
from datetime import datetime
from typing import Any

from salus.models.circadian import CircadianProfile
from salus.repositories.unit_of_work import IUnitOfWork
from salus.schemas.circadian import (
    CircadianAdviceResponse,
    CircadianProfileCreate,
    SolarTimes,
)
from salus.services.analytics.stats import pearson

logger = logging.getLogger("salus.services.circadian")

MINUTES_PER_DAY = 1440
MELATONIN_DELAY_MINUTES = 240
SLEEP_DURATION_MINUTES = 480
MORNING_LIGHT_ANCHOR_MINUTES = 120
EATING_WINDOW_START_DELAY_MINUTES = 60
EATING_WINDOW_END_OFFSET_MINUTES = 180
ALIGNMENT_DEDUCTION_MINUTES = 10
ALIGNMENT_EXCELLENT_THRESHOLD = 85


def _mins_to_str(mins: float) -> str:
    m = int(mins % MINUTES_PER_DAY)
    return f"{m // 60:02d}:{m % 60:02d}"


def _time_to_mins(t_str: str) -> int:
    hours, minutes = t_str.split(":")
    return int(hours) * 60 + int(minutes)


class CircadianService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    def get_or_create_profile(self, user_id: str) -> CircadianProfile:
        with self.uow:
            profile = self.uow.circadian_profiles.find_by_user(user_id)
            if not profile:
                profile = CircadianProfile(
                    user_id=user_id,
                    latitude=52.52,  # Default Berlin
                    longitude=13.40,
                    timezone_offset_hours=1.0,
                    configured_chronotype="intermediate",
                )
                self.uow.circadian_profiles.add(profile)
            return profile

    def save_profile(
        self, user_id: str, data: CircadianProfileCreate
    ) -> CircadianProfile:
        with self.uow:
            profile = self.uow.circadian_profiles.find_by_user(user_id)
            if not profile:
                profile = CircadianProfile(user_id=user_id)
                self.uow.circadian_profiles.add(profile)

            profile.latitude = data.latitude
            profile.longitude = data.longitude
            profile.timezone_offset_hours = data.timezone_offset_hours
            profile.configured_chronotype = data.configured_chronotype

            return profile

    def calculate_solar_times(
        self, date: datetime, latitude: float, longitude: float, tz_offset: float
    ) -> dict[str, Any]:
        """
        Pure-Python local solar calculation following the NOAA Solar Calculator.
        """
        y, m, d = date.year, date.month, date.day
        if m <= 2:
            y -= 1
            m += 12
        a = math.floor(y / 100)
        b = 2 - a + math.floor(a / 4)
        jd = (
            math.floor(365.25 * (y + 4716))
            + math.floor(30.6001 * (m + 1))
            + d
            + b
            - 1524.5
        )

        t = (jd - 2451545.0) / 36525.0
        l0 = (280.46646 + t * (36000.76983 + t * 0.0003032)) % 360
        g = (357.52911 + t * (35999.05029 - 0.0001537 * t)) % 360
        e = 0.016708634 - t * (0.000042037 + 0.0000001267 * t)

        sec = (
            (1.914602 - t * (0.004817 + 0.000014 * t)) * math.sin(math.radians(g))
            + (0.019993 - 0.000101 * t) * math.sin(math.radians(2 * g))
            + 0.002893 * math.sin(math.radians(3 * g))
        )
        sun_true_long = (l0 + sec) % 360
        obliquity = 23.439291 - t * (0.013004167 + t * (0.000000164 - t * 0.0000005036))
        declination = math.degrees(
            math.asin(
                math.sin(math.radians(obliquity))
                * math.sin(math.radians(sun_true_long))
            )
        )

        y_var = math.tan(math.radians(obliquity / 2.0)) ** 2
        eq_time = 4.0 * math.degrees(
            y_var * math.sin(math.radians(2.0 * l0))
            - 2.0 * e * math.sin(math.radians(g))
            + 4.0
            * e
            * y_var
            * math.sin(math.radians(g))
            * math.cos(math.radians(2.0 * l0))
            - 0.5 * (y_var**2) * math.sin(math.radians(4.0 * l0))
            - 1.25 * (e**2) * math.sin(math.radians(2.0 * g))
        )

        solar_noon_mins = 720.0 - 4.0 * longitude - eq_time + tz_offset * 60.0

        # Sunrise / Sunset Hour Angle
        cos_ha = (
            math.cos(math.radians(90.833))
            - math.sin(math.radians(latitude)) * math.sin(math.radians(declination))
        ) / (math.cos(math.radians(latitude)) * math.cos(math.radians(declination)))

        if cos_ha < -1.0:
            sunrise_mins = solar_noon_mins - 720.0
            sunset_mins = solar_noon_mins + 720.0
        elif cos_ha > 1.0:
            sunrise_mins = solar_noon_mins
            sunset_mins = solar_noon_mins
        else:
            ha = math.degrees(math.acos(cos_ha))
            sunrise_mins = solar_noon_mins - ha * 4.0
            sunset_mins = solar_noon_mins + ha * 4.0

        # Dawn / Dusk Civil Twilight Hour Angle (zenith = 96.0 degrees)
        cos_ha_civil = (
            math.cos(math.radians(96.0))
            - math.sin(math.radians(latitude)) * math.sin(math.radians(declination))
        ) / (math.cos(math.radians(latitude)) * math.cos(math.radians(declination)))

        if cos_ha_civil < -1.0:
            dawn_mins = solar_noon_mins - 720.0
            dusk_mins = solar_noon_mins + 720.0
        elif cos_ha_civil > 1.0:
            dawn_mins = solar_noon_mins
            dusk_mins = solar_noon_mins
        else:
            ha_civil = math.degrees(math.acos(cos_ha_civil))
            dawn_mins = solar_noon_mins - ha_civil * 4.0
            dusk_mins = solar_noon_mins + ha_civil * 4.0

        return {
            "sunrise": _mins_to_str(sunrise_mins),
            "sunset": _mins_to_str(sunset_mins),
            "solar_noon": _mins_to_str(solar_noon_mins),
            "dawn": _mins_to_str(dawn_mins),
            "dusk": _mins_to_str(dusk_mins),
            "sunrise_mins": sunrise_mins,
            "sunset_mins": sunset_mins,
            "solar_noon_mins": solar_noon_mins,
        }

    def _recent_sleep_times(self, user_id: str) -> tuple[str, str]:
        actual_onset = "23:00"
        actual_offset = "07:00"
        with self.uow:
            if self.uow.metric_definitions.find_by_code("sleep") is None:
                return actual_onset, actual_offset
            sleeps = self.uow.measurements.find_by_metric_type(
                metric_code="sleep", user_id=user_id
            )
            valid_sleeps = [s for s in sleeps if s.end_time is not None]
            if valid_sleeps:
                last_sleep = valid_sleeps[0]
                actual_onset = last_sleep.start_time.strftime("%H:%M")
                if last_sleep.end_time:
                    actual_offset = last_sleep.end_time.strftime("%H:%M")
        return actual_onset, actual_offset

    def _alignment_score(self, actual_onset: str, target_onset: str) -> int:
        diff = abs(_time_to_mins(actual_onset) - _time_to_mins(target_onset))
        if diff > MINUTES_PER_DAY // 2:
            diff = MINUTES_PER_DAY - diff
        return max(0, 100 - int(diff / ALIGNMENT_DEDUCTION_MINUTES))

    def _light_advice(self, solar: dict) -> list[dict]:
        return [
            {
                "time_window": f"{solar['sunrise']} - {_mins_to_str(solar['sunrise_mins'] + MORNING_LIGHT_ANCHOR_MINUTES)}",
                "action": "Morning Daylight Anchor",
                "description": "Expose eyes to bright outdoor daylight (10,000+ Lux) for 15-30 minutes. Suppresses remaining melatonin and sets the 16-hour wake timer.",
            },
            {
                "time_window": f"After {solar['sunset']}",
                "action": "Minimize Blue Light",
                "description": "Dim indoor lighting and use red/warm light sources to avoid suppressing evening melatonin onset.",
            },
        ]

    def _eating_window(self, actual_onset: str, actual_offset: str) -> dict:
        actual_offset_mins = _time_to_mins(actual_offset)
        actual_onset_mins = _time_to_mins(actual_onset)
        eating_start_mins = (
            actual_offset_mins + EATING_WINDOW_START_DELAY_MINUTES
        ) % MINUTES_PER_DAY
        eating_end_mins = (
            actual_onset_mins - EATING_WINDOW_END_OFFSET_MINUTES
        ) % MINUTES_PER_DAY
        return {
            "start": _mins_to_str(eating_start_mins),
            "end": _mins_to_str(eating_end_mins),
            "advice": "Keep your daily eating window within these times. Digesting food close to bedtime disrupts cellular melatonin repairs and sleep quality.",
        }

    def calculate_advice(self, user_id: str) -> CircadianAdviceResponse:
        profile = self.get_or_create_profile(user_id)

        # Calculate solar times for today
        today = datetime.now()
        solar = self.calculate_solar_times(
            today, profile.latitude, profile.longitude, profile.timezone_offset_hours
        )

        actual_onset, actual_offset = self._recent_sleep_times(user_id)

        # Circadian rule engine: melatonin onset is ~4 hours after sunset
        sunset_mins = solar["sunset_mins"]
        target_onset_mins = (sunset_mins + MELATONIN_DELAY_MINUTES) % MINUTES_PER_DAY
        target_offset_mins = (
            target_onset_mins + SLEEP_DURATION_MINUTES
        ) % MINUTES_PER_DAY

        target_onset = _mins_to_str(target_onset_mins)
        target_offset = _mins_to_str(target_offset_mins)

        alignment_score = self._alignment_score(actual_onset, target_onset)
        if alignment_score >= ALIGNMENT_EXCELLENT_THRESHOLD:
            sleep_advice = "Excellent! Your sleep onset aligns perfectly with your local biological melatonin rise."
        else:
            sleep_advice = f"Try moving your sleep window closer to {target_onset} to align sleep pressure with melatonin release."

        # Chronotype — data-driven detection
        chronotype = profile.configured_chronotype
        detected = self._detect_chronotype(user_id)
        if detected is not None:
            chronotype = (
                f"{profile.configured_chronotype} (detected: {detected})"
                if detected != profile.configured_chronotype
                else chronotype
            )

        return CircadianAdviceResponse(
            solar_times=SolarTimes(
                sunrise=solar["sunrise"],
                sunset=solar["sunset"],
                solar_noon=solar["solar_noon"],
                dawn=solar["dawn"],
                dusk=solar["dusk"],
            ),
            chronotype=chronotype,
            alignment_score=alignment_score,
            sleep_window={
                "target_onset": target_onset,
                "target_offset": target_offset,
                "actual_onset": actual_onset,
                "actual_offset": actual_offset,
                "advice": sleep_advice,
            },
            light_advice=self._light_advice(solar),
            eating_window=self._eating_window(actual_onset, actual_offset),
        )

    def _detect_chronotype(self, user_id: str) -> str | None:
        try:
            with self.uow:
                sleep_md = self.uow.metric_definitions.find_by_code("sleep")
                if sleep_md is None:
                    return None
                sleeps = self.uow.measurements.find_by_metric_type(
                    metric_code="sleep", user_id=user_id
                )
                onset_times: list[float] = []
                daylight_hours: list[float] = []
                for s in sleeps[:14]:
                    if s.start_time is None:
                        continue
                    onset_hour = s.start_time.hour + s.start_time.minute / 60.0
                    onset_times.append(onset_hour)
                    doy = s.start_time.timetuple().tm_yday
                    lat = 52.52
                    decl = 23.45 * math.sin(
                        math.radians((360 / 365) * (284 + doy))
                    )
                    day_len = (
                        24.0
                        - (24.0 / 180.0)
                        * math.degrees(
                            math.acos(
                                -math.tan(math.radians(lat))
                                * math.tan(math.radians(decl))
                            )
                        )
                        if abs(math.tan(math.radians(lat)) * math.tan(math.radians(decl))) < 1
                        else (24.0 if math.tan(math.radians(lat)) * math.tan(math.radians(decl)) < 0 else 0.0)
                    )
                    daylight_hours.append(day_len)
                if len(onset_times) < 7:
                    return None
                n = min(len(onset_times), len(daylight_hours))
                corr = pearson(daylight_hours[:n], onset_times[:n])
                if corr and abs(corr.r) > 0.3:
                    if corr.r > 0:
                        return "owl"
                    return "lark"
                return None
        except Exception:
            logger.exception("Chronotype detection failed")
            return None
