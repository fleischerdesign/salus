# 12. Food data sources and barcode lookup strategy

- Status: Proposed
- Date: 2026-08-15

## Context

Barcode scanning (Yazio-style) requires a food database. Most commercial
databases (FatSecret, Nutritionix, Edamam, Chomp) forbid caching, storage and
redistribution in their terms of service — incompatible with a self-hosted,
offline-first app. The app runs in three modes (offline-only local profile,
offline-with-sync, online instance), each with different access to a central
server and to the internet.

## Decision

### 1. Sources: only free + redistributable

| Source | License | Role |
|---|---|---|
| **OpenFoodFacts (OFF)** | ODbL — copying/redistribution allowed with attribution | **Primary** (global + regional mirrors: `world/de/us/….openfoodfacts.org`) |
| **USDA FoodData Central** | US government, public-domain foundation data | **Secondary** (US-centric, API key) |
| Commercial APIs (FatSecret/Nutritionix/Edamam/…) | TOS forbids caching/redistribution | **Excluded** |

Source priority and enabled set are configurable per instance (admin settings).

### 2. `FoodDataSource` abstraction — one lookup path per mode

A pluggable source (same pattern as `INetworkProvider`):

```
FoodDataSource
├─ ServerProxyFoodSource       (server mode)    → Salus server → OFF/USDA → cache → sync
└─ DirectOpenFoodFactsSource   (local profile)  → OFF directly (User-Agent, optional user key)
```

- **Server mode:** client → `GET /api/v1/food/items/barcode/{code}` on the Salus
  server. The server calls the external API, **caches the result as a system
  `food_item`** (`user_id=null`, `is_verified=true`, `source="openfoodfacts"`),
  and returns it. Because `food_item` is `shared_nullable`, every cached item
  syncs to all clients — a food looked up once is available offline everywhere
  afterwards. One central cache, shared rate limits, no per-client CORS.
- **Local profile (no server):** the client calls OFF directly
  (`https://world.openfoodfacts.org/api/v2/product/{barcode}.json`) with a
  `User-Agent`. In the native APK/WebView this is a plain fetch; in the PWA the
  direct route depends on OFF's CORS headers (**open item: verify**). Results
  are written to the local Dexie `food_item`. Optional user-provided OFF key for
  higher rate limits.
- **Manual fallback:** no source resolves → user creates the food manually.

Both paths converge on the same local `food_item` persistence.

### 3. Offline matrix

| Mode | Lookup | Food data |
|---|---|---|
| Offline-only (local profile) | direct OFF if enabled, else none | seed subset + user-created + previously cached |
| Offline-with-sync | server proxy when online; synced cache when offline | seed + cached OFF + user |
| Online instance | full server proxy + cache | everything + optional bulk import |

### 4. Seed and bulk data

- **Seed:** a small set (~50–100 common foods) shipped in `reference.json`
  (`seedReferenceData`), keeping the APK/PWA bundle small (~20–30 KB).
- **Bulk import (v2, admin):** one-time OFF dataset import into the instance
  makes it fully self-contained; data lives server-side and syncs down — it is
  never shipped in the client bundle.

### 5. Settings granularity

| Level | Setting | Storage |
|---|---|---|
| Admin (instance) | source enable/priority, instance API keys, proxy-cache on/off, rate limits, bulk import | server config |
| User/Device | direct-API-in-local-mode on/off, own OFF/USDA key | device-local (localStorage/Dexie) — API keys are credentials and are **never cloud-synced** (Device-Local vs Cloud-Synced rule) |

## Consequences

- Barcode lookup works in every mode with one code path (`FoodDataSource`).
- Cached lookups become durable, synced system foods (offline benefit grows
  with usage).
- Self-hosting stays license-clean (OFF/USDA only).
- PWA direct-to-OFF CORS must be verified during implementation; the APK path
  is unaffected.
