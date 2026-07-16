# Device Management

## Overview
Verwalte externe Geräte (Bluetooth, API-connected) die Daten an Salus senden.
Einheitliche Abstraktion für CGM, Blutdruck-Messgeräte, Ketone-Messgeräte, Fitness-Tracker etc.

## Motivation
Mehrere Features (Blood Glucose, Blood Pressure, Fasting Ketones) benötigen Integration mit externen Geräten.
Statt jedes Gerät ad-hoc zu integrieren, brauchen wir ein einheitliches Device-Management-System:
- Devices registrieren und konfigurieren
- Daten von Devices empfangen (Webhook, Bluetooth, API-Polling)
- Device-Status tracken (online/offline, Batteriestand, letzte Synchronisation)
- Mehrere Devices pro User, mehrere User pro Device? (Familienkonto?)

## Data Model

### device_type
(Referenztabelle, seeded)

| Column | Type | Notes |
|---|---|---|
| code | str | PK — "dexcom_g7", "freestyle_libre_3", "omron_m7", "withings_bpm", "ketoscan" |
| name | str | "Dexcom G7" |
| manufacturer | str | "Dexcom" |
| category | enum | cgm / blood_pressure / ketone / scale / fitness_tracker / wearable / other |
| connection_type | enum | api_oauth / api_key / bluetooth / nfc / webhook |
| data_types | json | ["blood_glucose"] — welche Metriken dieses Gerät liefert |
| setup_instructions | str? | Markdown — Anleitung zur Einrichtung |
| icon | str | Material Symbols |
| is_active | bool | |

### device
| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → user |
| device_type_code | str | FK → device_type |
| nickname | str? | "Mein Dexcom" |
| config_json | json | Geräte-spezifische Konfiguration (API-Key, Pairing-Code, etc.) |
| is_active | bool | |
| last_seen_at | datetime? | Letzte Datenübertragung |
| battery_level | int? | 0-100 |
| firmware_version | str? | |
| error_message | str? | Letzte Fehlermeldung |
| created_at | datetime | |
| updated_at | datetime | |

### device_reading_log
(Audit-Trail — welche Daten kamen von welchem Gerät?)

| Column | Type | Notes |
|---|---|---|
| id | UUID | PK |
| device_id | UUID | FK → device |
| received_at | datetime | |
| data_type | str | "blood_glucose", "blood_pressure" |
| raw_payload_json | json | Original-Daten vom Gerät |
| measurement_ids | json | [uuid, uuid] — verknüpfte Measurement-Rows |
| processing_status | enum | success / partial / failed / ignored |
| error_details | str? | |

## API Endpoints

### Device Types (referenz)
| Method | Path | Description |
|---|---|---|
| GET | /api/v1/devices/types | List supported device types |
| GET | /api/v1/devices/types/{code} | Device type detail + setup instructions |

### Devices (user)
| Method | Path | Description |
|---|---|---|
| GET | /api/v1/devices | List my devices |
| POST | /api/v1/devices | Register new device |
| GET | /api/v1/devices/{id} | Device details |
| PUT | /api/v1/devices/{id} | Update config |
| DELETE | /api/v1/devices/{id} | Remove device |
| POST | /api/v1/devices/{id}/pair | Initiate pairing (Bluetooth/NFC) |
| POST | /api/v1/devices/{id}/unpair | Unpair |
| POST | /api/v1/devices/{id}/sync | Trigger manual sync |

### Device Readings
| Method | Path | Description |
|---|---|---|
| GET | /api/v1/devices/{id}/readings | Reading log (paginated) |
| GET | /api/v1/devices/{id}/readings/latest | Latest reading per data type |

### Device Callback (for devices that push data)
| Method | Path | Description |
|---|---|---|
| POST | /api/v1/devices/callback/{device_type_code} | Webhook callback from device/cloud |
| POST | /api/v1/devices/callback/{device_type_code}/{device_id} | Authenticated callback |

## Device Adapter Architecture

Statt harter Integration pro Gerät → Adapter-Pattern:

```python
class DeviceAdapter(ABC):
    """Abstract adapter for a device type."""
    
    device_type_code: str
    
    async def pair(self, device: Device) -> bool: ...
    async def unpair(self, device: Device) -> None: ...
    async def fetch_data(self, device: Device) -> list[Measurement]: ...
    async def handle_callback(self, device: Device, payload: dict) -> list[Measurement]: ...
    def get_setup_instructions(self) -> str: ...
    def validate_config(self, config: dict) -> bool: ...
```

### Konkrete Adapter (Priorität)

#### Phase 1 — Webhook/API-basiert (einfacher)
| Adapter | Connection | Data Type |
|---|---|---|
| NightscoutAdapter | API Key (Nightscout URL) | blood_glucose (CGM) |
| AppleHealthAdapter | Webhook (via Apple Health Export) | steps, heart_rate, sleep, weight |
| GoogleFitAdapter | OAuth | steps, heart_rate, weight |

#### Phase 2 — Geräte-spezifisch
| Adapter | Connection | Notes |
|---|---|---|
| DexcomAdapter | Dexcom API (OAuth/API Key) | CGM data |
| LibreLinkAdapter | LibreLinkUp API | CGM data via LibreLink |
| OmronAdapter | Omron Connect API | Blood pressure |
| WithingsAdapter | Withings API (OAuth) | BP, weight, sleep |

#### Phase 3 — Bluetooth/BLE
| Adapter | Connection | Notes |
|---|---|---|
| BluetoothDeviceAdapter | Web Bluetooth API (Browser) | Generic BLE Health Devices |
| KetoneAdapter | BLE (Keto-Mojo, etc.) | Ketone readings |

## Frontend

- **DeviceList** — Alle registrierten Geräte mit Status (online/offline/error)
- **DeviceSetupWizard** — Step-by-Step: Gerätetyp auswählen → Konfiguration → Testen → Aktivieren
- **DeviceTypeBrowser** — Unterstützte Geräte durchsuchen mit Setup-Anleitungen
- **DeviceCard** — Geräte-Status mit letztem Reading, Batterie, Sync-Button
- **DeviceErrorBanner** — Zeigt Fehlermeldung wenn Gerät nicht erreichbar

## Integration Points
- **Metric System** → Devices schreiben in MetricDefinitions (blood_glucose, systolic_bp, etc.)
- **Webhook Ingest** → Device Callbacks gehen durch den existierenden Webhook-Parser
- **Notifications** → "Dexcom Sensor läuft in 24h ab", "Blutdruck-Messgerät Batterie niedrig"
- **Insights/AI Coach** → "Deine CGM-Daten zeigen verbesserte Time-in-Range diese Woche"
- **Reminders** → "Zeit für die tägliche Blutdruck-Messung"

## Security
- Device-Konfiguration (API Keys, Tokens) verschlüsselt in config_json speichern
- Device Callbacks: Signatur-Verifikation (HMAC) für eingehende Daten
- OAuth Tokens: Refresh-Token-Handling, kein Plain-Text-Client-Secret im Frontend
- Bluetooth: Pairing nur mit Bestätigung des Users, keine Auto-Connect

## Open Questions
- Bluetooth/BLE: Browser-API (`navigator.bluetooth`) oder Native-App? Mobile-first?
- Soll es eine "Health Connect" (Android) / "HealthKit" (iOS) Bridge geben statt einzelner Geräte-Adapter?
- Device-Sharing: Soll ein Device mehreren Usern zugeordnet werden können (Familie)?
- Sollen Device-Daten auch offline ohne Gerät funktionieren? (Manuelle Eingabe immer möglich, Device ist optional)
- Priorisierung: Welche Devices zuerst? Nightscout (größte User-Basis, einfachste Integration)?
