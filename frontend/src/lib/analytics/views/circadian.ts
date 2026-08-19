import Dexie from 'dexie';
import { MS_PER_DAY } from '$lib/utils/datetime';

interface SolarTimes {
  sunrise: string;
  sunset: string;
  solar_noon: string;
  dawn: string;
  dusk: string;
  sunrise_mins: number;
  sunset_mins: number;
  solar_noon_mins: number;
}

export function calculateSolarTimes(
  date: string,
  lat: number,
  lng: number,
  tzOffset: number
): SolarTimes {
  const d = new Date(date + 'T00:00:00Z');
  const start = new Date(Date.UTC(d.getUTCFullYear(), 0, 0));
  const diff = d.getTime() - start.getTime();
  const dayOfYear = Math.floor(diff / (1000 * 60 * 60 * 24));

  // Fractional year in radians
  const gamma = ((2 * Math.PI) / 365) * (dayOfYear - 1);

  // Equation of time in minutes (NOAA standard)
  const eqtime =
    229.18 *
    (0.000075 +
      0.001868 * Math.cos(gamma) -
      0.032077 * Math.sin(gamma) -
      0.014615 * Math.cos(2 * gamma) -
      0.040849 * Math.sin(2 * gamma));

  // Solar declination angle in radians (NOAA)
  const decl =
    0.006918 -
    0.399912 * Math.cos(gamma) +
    0.070257 * Math.sin(gamma) -
    0.006758 * Math.cos(2 * gamma) +
    0.000907 * Math.sin(2 * gamma) -
    0.002697 * Math.cos(3 * gamma) +
    0.00148 * Math.sin(3 * gamma);

  // Hour angle for sunrise/sunset (90.833° zenith)
  const latRad = (lat * Math.PI) / 180;
  const cosHa =
    Math.cos((90.833 * Math.PI) / 180) / (Math.cos(latRad) * Math.cos(decl)) -
    Math.tan(latRad) * Math.tan(decl);

  const haDeg = Math.acos(Math.max(-1, Math.min(1, cosHa))) * (180 / Math.PI);

  // Solar noon and sunrise/sunset in minutes from local midnight
  const solar_noon_mins = 720 - 4 * lng - eqtime + tzOffset * 60;
  const sunrise_mins = solar_noon_mins - haDeg * 4;
  const sunset_mins = solar_noon_mins + haDeg * 4;

  // Civil Twilight (96° zenith)
  const cosHaCivil =
    Math.cos((96 * Math.PI) / 180) / (Math.cos(latRad) * Math.cos(decl)) -
    Math.tan(latRad) * Math.tan(decl);
  const haCivilDeg = Math.acos(Math.max(-1, Math.min(1, cosHaCivil))) * (180 / Math.PI);
  const dawn_mins = solar_noon_mins - haCivilDeg * 4;
  const dusk_mins = solar_noon_mins + haCivilDeg * 4;

  function minsToStr(mins: number): string {
    const total = ((Math.round(mins) % 1440) + 1440) % 1440;
    const h = Math.floor(total / 60);
    const m = total % 60;
    return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
  }

  return {
    sunrise: minsToStr(sunrise_mins),
    sunset: minsToStr(sunset_mins),
    solar_noon: minsToStr(solar_noon_mins),
    dawn: minsToStr(dawn_mins),
    dusk: minsToStr(dusk_mins),
    sunrise_mins: ((Math.round(sunrise_mins) % 1440) + 1440) % 1440,
    sunset_mins: ((Math.round(sunset_mins) % 1440) + 1440) % 1440,
    solar_noon_mins: ((Math.round(solar_noon_mins) % 1440) + 1440) % 1440
  };
}

function timeToMins(t: string): number {
  const [h, m] = t.split(':').map(Number);
  return h * 60 + m;
}

function minsToTime(mins: number): string {
  const m = Math.round(mins) % 1440;
  const h = Math.floor(m / 60);
  const mm = Math.round(m % 60);
  return `${String(h).padStart(2, '0')}:${String(mm).padStart(2, '0')}`;
}

export interface CircadianAdvice {
  solar_times: { sunrise: string; sunset: string; solar_noon: string; dawn: string; dusk: string };
  chronotype: string;
  alignment_score: number;
  sleep_window: {
    target_onset: string;
    target_offset: string;
    actual_onset: string;
    actual_offset: string;
    advice: string;
  };
  light_advice: { time_window: string; action: string; description: string }[];
  eating_window: { start: string; end: string; advice: string };
}

export function calculateCircadianAdvice(params: {
  latitude: number;
  longitude: number;
  tzOffset: number;
  chronotype: string;
  sleepMeasurements: { start_time: string; end_time: string | null }[];
}): CircadianAdvice {
  const { latitude, longitude, tzOffset, chronotype, sleepMeasurements } = params;
  const today = new Date().toISOString().slice(0, 10);
  const solar = calculateSolarTimes(today, latitude, longitude, tzOffset);

  let actualOnset = '23:00';
  let actualOffset = '07:00';

  const validSleeps = sleepMeasurements.filter((s) => s.end_time);
  if (validSleeps.length > 0) {
    const last = validSleeps[0];
    actualOnset = last.start_time.slice(11, 16);
    actualOffset = last.end_time!.slice(11, 16);
  }

  const targetOnsetMins = (solar.sunset_mins + 240) % 1440;
  const targetOffsetMins = (targetOnsetMins + 480) % 1440;
  const targetOnset = minsToTime(targetOnsetMins);
  const targetOffset = minsToTime(targetOffsetMins);

  const actualOnsetMins = timeToMins(actualOnset);
  let diff = Math.abs(actualOnsetMins - targetOnsetMins);
  if (diff > 720) diff = 1440 - diff;
  const alignmentScore = Math.max(0, 100 - Math.floor(diff / 10));

  let sleepAdvice: string;
  if (alignmentScore >= 85) {
    sleepAdvice =
      'Excellent! Your sleep onset aligns perfectly with your local biological melatonin rise.';
  } else {
    sleepAdvice = `Try moving your sleep window closer to ${targetOnset} to align sleep pressure with melatonin release.`;
  }

  const lightAdvice = [
    {
      time_window: `${solar.sunrise} - ${minsToTime(solar.sunrise_mins + 120)}`,
      action: 'Morning Daylight Anchor',
      description:
        'Expose eyes to bright outdoor daylight (10,000+ Lux) for 15–30 minutes. Suppresses remaining melatonin and sets the 16-hour wake timer.'
    },
    {
      time_window: `After ${solar.sunset}`,
      action: 'Minimize Blue Light',
      description:
        'Dim indoor lighting and use red/warm light sources to avoid suppressing evening melatonin onset.'
    }
  ];

  const actualOffsetMins = timeToMins(actualOffset);
  const eatingStartMins = (actualOffsetMins + 60) % 1440;
  const eatingEndMins = (actualOnsetMins - 180 + 1440) % 1440;
  const eatingWindow = {
    start: minsToTime(eatingStartMins),
    end: minsToTime(eatingEndMins),
    advice:
      'Keep your daily eating window within these times. Digesting food close to bedtime disrupts cellular melatonin repairs and sleep quality.'
  };

  return {
    solar_times: {
      sunrise: solar.sunrise,
      sunset: solar.sunset,
      solar_noon: solar.solar_noon,
      dawn: solar.dawn,
      dusk: solar.dusk
    },
    chronotype,
    alignment_score: alignmentScore,
    sleep_window: {
      target_onset: targetOnset,
      target_offset: targetOffset,
      actual_onset: actualOnset,
      actual_offset: actualOffset,
      advice: sleepAdvice
    },
    light_advice: lightAdvice,
    eating_window: eatingWindow
  };
}

export async function fetchCircadianAdvice(
  db: import('$lib/db/database').SalusDB
): Promise<CircadianAdvice> {
  const profiles = await db.circadian_profile.filter((p) => !p.deleted_at).toArray();
  const profile = profiles[0];
  const lat = profile?.latitude ?? 52.52;
  const lng = profile?.longitude ?? 13.4;
  const tzOffset = profile?.timezone_offset_hours ?? 1;
  const chronotype = profile?.configured_chronotype ?? 'intermediate';

  const metricTypes = await db.metric_definition
    .where('source_data_type')
    .equals('sleep')
    .toArray();
  const sleepMT = metricTypes[0];
  const cutoff = new Date(Date.now() - 14 * MS_PER_DAY).toISOString();
  const rawSleeps = sleepMT?.code
    ? await db.measurement
        .where('[metric_code+start_time]')
        .between([sleepMT.code, cutoff], [sleepMT.code, Dexie.maxKey])
        .toArray()
    : [];
  const sleepMeasurements = rawSleeps.filter((m) => !m.deleted_at && m.end_time != null);

  return calculateCircadianAdvice({
    latitude: lat,
    longitude: lng,
    tzOffset,
    chronotype,
    sleepMeasurements
  });
}
