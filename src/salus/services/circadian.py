import math
from datetime import datetime
from typing import Any

from salus.models.circadian import CircadianProfile
from salus.repositories.unit_of_work import IUnitOfWork
from salus.schemas.circadian import CircadianProfileCreate, CircadianAdviceResponse, SolarTimes


class CircadianService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    def get_or_create_profile(self, user_id: int) -> CircadianProfile:
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
                self.uow.commit()
            return profile

    def save_profile(self, user_id: int, data: CircadianProfileCreate) -> CircadianProfile:
        with self.uow:
            profile = self.uow.circadian_profiles.find_by_user(user_id)
            if not profile:
                profile = CircadianProfile(user_id=user_id)
                self.uow.circadian_profiles.add(profile)
            
            profile.latitude = data.latitude
            profile.longitude = data.longitude
            profile.timezone_offset_hours = data.timezone_offset_hours
            profile.configured_chronotype = data.configured_chronotype
            
            self.uow.commit()
            return profile

    def calculate_solar_times(self, date: datetime, latitude: float, longitude: float, tz_offset: float) -> dict[str, Any]:
        """
        Pure-Python local solar calculation following the NOAA Solar Calculator.
        """
        y, m, d = date.year, date.month, date.day
        if m <= 2:
            y -= 1
            m += 12
        a = math.floor(y / 100)
        b = 2 - a + math.floor(a / 4)
        jd = math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + b - 1524.5

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
        obliquity = (23.439291 - t * (0.013004167 + t * (0.000000164 - t * 0.0000005036)))
        declination = math.degrees(math.asin(math.sin(math.radians(obliquity)) * math.sin(math.radians(sun_true_long))))

        y_var = math.tan(math.radians(obliquity / 2.0)) ** 2
        eq_time = 4.0 * math.degrees(
            y_var * math.sin(math.radians(2.0 * l0))
            - 2.0 * e * math.sin(math.radians(g))
            + 4.0 * e * y_var * math.sin(math.radians(g)) * math.cos(math.radians(2.0 * l0))
            - 0.5 * (y_var ** 2) * math.sin(math.radians(4.0 * l0))
            - 1.25 * (e ** 2) * math.sin(math.radians(2.0 * g))
        )

        solar_noon_mins = 720.0 - 4.0 * longitude - eq_time + tz_offset * 60.0

        # Sunrise / Sunset Hour Angle
        cos_ha = (math.cos(math.radians(90.833)) - math.sin(math.radians(latitude)) * math.sin(math.radians(declination))) / (
            math.cos(math.radians(latitude)) * math.cos(math.radians(declination))
        )

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
        cos_ha_civil = (math.cos(math.radians(96.0)) - math.sin(math.radians(latitude)) * math.sin(math.radians(declination))) / (
            math.cos(math.radians(latitude)) * math.cos(math.radians(declination))
        )

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

        def min_to_str(m: float) -> str:
            m = int(m % 1440)
            return f"{m // 60:02d}:{m % 60:02d}"

        return {
            "sunrise": min_to_str(sunrise_mins),
            "sunset": min_to_str(sunset_mins),
            "solar_noon": min_to_str(solar_noon_mins),
            "dawn": min_to_str(dawn_mins),
            "dusk": min_to_str(dusk_mins),
            "sunrise_mins": sunrise_mins,
            "sunset_mins": sunset_mins,
            "solar_noon_mins": solar_noon_mins,
        }

    def calculate_advice(self, user_id: int) -> CircadianAdviceResponse:
        profile = self.get_or_create_profile(user_id)
        
        # Calculate solar times for today
        today = datetime.now()
        solar = self.calculate_solar_times(
            today, profile.latitude, profile.longitude, profile.timezone_offset_hours
        )

        # Retrieve recent sleep measurements
        actual_onset = "23:00"
        actual_offset = "07:00"
        
        with self.uow:
            sleep_mt = self.uow.metric_types.find_by_name_and_user("Sleep", user_id)
            if sleep_mt and sleep_mt.id is not None:
                sleeps = self.uow.measurements.find_by_metric_type(
                    metric_type_id=sleep_mt.id, user_id=user_id
                )
                # Take the most recent sleep log to get actual onset/offset times
                valid_sleeps = [s for s in sleeps if s.end_time is not None]
                if valid_sleeps:
                    last_sleep = valid_sleeps[0]
                    # Format as HH:MM
                    actual_onset = last_sleep.start_time.strftime("%H:%M")
                    if last_sleep.end_time:
                        actual_offset = last_sleep.end_time.strftime("%H:%M")

        # Circadian rule engine calculations
        # Melatonin onset is typically ~4 hours after sunset
        sunset_mins = solar["sunset_mins"]
        target_onset_mins = (sunset_mins + 240) % 1440
        target_offset_mins = (target_onset_mins + 480) % 1440  # 8 hours sleep target

        def mins_to_str(mins: float) -> str:
            m = int(mins)
            return f"{m // 60:02d}:{m % 60:02d}"

        target_onset = mins_to_str(target_onset_mins)
        target_offset = mins_to_str(target_offset_mins)

        # Calculate alignment score
        # Compare actual sleep onset with target sleep onset
        def time_to_mins(t_str: str) -> int:
            parts = t_str.split(":")
            return int(parts[0]) * 60 + int(parts[1])

        actual_onset_mins = time_to_mins(actual_onset)
        diff = abs(actual_onset_mins - target_onset_mins)
        if diff > 720:
            diff = 1440 - diff
        
        score_deduction = int(diff / 10)  # Deduct 1 point for every 10 minutes offset
        alignment_score = max(0, 100 - score_deduction)

        # Generate sleep advice
        sleep_advice = ""
        if alignment_score >= 85:
            sleep_advice = "Excellent! Your sleep onset aligns perfectly with your local biological melatonin rise."
        else:
            sleep_advice = f"Try moving your sleep window closer to {target_onset} to align sleep pressure with melatonin release."

        # Generate light advice
        light_advice = [
            {
                "time_window": f"{solar['sunrise']} - {mins_to_str(solar['sunrise_mins'] + 120)}",
                "action": "Morning Daylight Anchor",
                "description": "Expose eyes to bright outdoor daylight (10,000+ Lux) for 15-30 minutes. Suppresses remaining melatonin and sets the 16-hour wake timer."
            },
            {
                "time_window": f"After {solar['sunset']}",
                "action": "Minimize Blue Light",
                "description": "Dim indoor lighting and use red/warm light sources to avoid suppressing evening melatonin onset."
            }
        ]

        # Generate eating advice (Time-restricted eating window: wake + 1h to sleep - 3h)
        actual_offset_mins = time_to_mins(actual_offset)
        eating_start_mins = (actual_offset_mins + 60) % 1440
        eating_end_mins = (actual_onset_mins - 180) % 1440

        eating_window = {
            "start": mins_to_str(eating_start_mins),
            "end": mins_to_str(eating_end_mins),
            "advice": "Keep your daily eating window within these times. Digesting food close to bedtime disrupts cellular melatonin repairs and sleep quality."
        }

        # Chronotype detection
        chronotype = profile.configured_chronotype

        return CircadianAdviceResponse(
            solar_times=SolarTimes(
                sunrise=solar["sunrise"],
                sunset=solar["sunset"],
                solar_noon=solar["solar_noon"],
                dawn=solar["dawn"],
                dusk=solar["dusk"]
            ),
            chronotype=chronotype,
            alignment_score=alignment_score,
            sleep_window={
                "target_onset": target_onset,
                "target_offset": target_offset,
                "actual_onset": actual_onset,
                "actual_offset": actual_offset,
                "advice": sleep_advice
            },
            light_advice=light_advice,
            eating_window=eating_window
        )
