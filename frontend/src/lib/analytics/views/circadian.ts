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
  const d = new Date(date + 'T12:00:00');
  const jd = toJulian(d, tzOffset);

  const n = jd - 2451545.0;
  const ls = (280.46 + 0.9856474 * n) % 360;
  const g = (357.528 + 0.9856003 * n) % 360;
  const lam = (ls + 1.915 * Math.sin(deg2rad(g)) + 0.02 * Math.sin(deg2rad(2 * g))) % 360;
  const eps = 23.44 - 0.0000004 * n;
  const ra = Math.atan2(Math.cos(deg2rad(eps)) * Math.sin(deg2rad(lam)), Math.cos(deg2rad(lam)));
  const dec = Math.asin(Math.sin(deg2rad(eps)) * Math.sin(deg2rad(lam)));

  const ha = Math.acos(
    (Math.sin(deg2rad(-0.833)) - Math.sin(deg2rad(lat)) * Math.sin(dec)) /
      (Math.cos(deg2rad(lat)) * Math.cos(dec))
  );

  const jdTransit = 2451545.0 + n + (rad2deg(ra) - rad2deg(ls)) / 360.0;
  const jdSet = jdTransit + rad2deg(ha) / 360.0;
  const jdRise = jdTransit - rad2deg(ha) / 360.0;

  const haCivil = Math.acos(
    (Math.sin(deg2rad(-6)) - Math.sin(deg2rad(lat)) * Math.sin(dec)) /
      (Math.cos(deg2rad(lat)) * Math.cos(dec))
  );
  const jdDawn = jdTransit - rad2deg(haCivil) / 360.0;
  const jdDusk = jdTransit + rad2deg(haCivil) / 360.0;

  const sunrise_mins = jdToMins(jdRise, tzOffset);
  const sunset_mins = jdToMins(jdSet, tzOffset);
  const solar_noon_mins = jdToMins(jdTransit, tzOffset);

  return {
    sunrise: jdToTime(jdRise, tzOffset),
    sunset: jdToTime(jdSet, tzOffset),
    solar_noon: jdToTime(jdTransit, tzOffset),
    dawn: jdToTime(jdDawn, tzOffset),
    dusk: jdToTime(jdDusk, tzOffset),
    sunrise_mins,
    sunset_mins,
    solar_noon_mins
  };
}

function deg2rad(d: number): number {
  return (d * Math.PI) / 180;
}
function rad2deg(r: number): number {
  return (r * 180) / Math.PI;
}

function toJulian(d: Date, tzOffset: number): number {
  return d.getTime() / 86400000 + 2440587.5 - tzOffset / 24;
}

function jdToTime(jd: number, tzOffset: number): string {
  const frac = jd - Math.floor(jd);
  const totalHours = frac * 24 + tzOffset;
  const h = Math.floor(((totalHours % 24) + 24) % 24);
  const m = Math.floor(((totalHours % 1) * 60 + 60) % 60);
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
}

function jdToMins(jd: number, tzOffset: number): number {
  const frac = jd - Math.floor(jd);
  const totalHours = frac * 24 + tzOffset;
  return Math.round((((totalHours % 24) + 24) % 24) * 60 + (((totalHours % 1) * 60 + 60) % 60));
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
  const sleepMeasurements = sleepMT?.code
    ? await db.measurement
        .where('metric_code')
        .equals(sleepMT.code)
        .filter((m) => !m.deleted_at && m.end_time != null)
        .toArray()
    : [];

  return calculateCircadianAdvice({
    latitude: lat,
    longitude: lng,
    tzOffset,
    chronotype,
    sleepMeasurements
  });
}
