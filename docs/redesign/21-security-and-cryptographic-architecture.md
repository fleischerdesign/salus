# Salus 2.0 — Sicherheits- & Kryptographie-Architektur (E2EE)
**Dokument:** `21-security-and-cryptographic-architecture.md`  
**Status:** Verbindlich  
**Zweck:** Mathematische und kryptographische Spezifikation der Zero-Knowledge Ende-zu-Ende-Verschlüsselung (E2EE) für Arzt-Freigaben, Token-Sicherheit und XSS/CSRF-Härtung.

---

## 1. Zero-Knowledge Arzt-Freigaben (WebCrypto API)

Wenn ein Nutzer Gesundheitsdaten für einen Arzt oder Ernährungsberater freigibt:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                 E2EE FREIGABE-ABLAUF                                    │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Clientseitige Schlüsselgenerierung (Browser des Nutzers):                             │
│    • Erzeugung eines symmetrischen AES-GCM 256-Bit Schlüssels (`K_sym`).               │
│    • Verschlüsselung der ausgewählten Daten (Blutdruck, Labore) mit `K_sym` + IV.       │
│                                                                                         │
│ 2. Server-Rolle (Zero-Knowledge Speicher):                                              │
│    • Server erhält NUR den verschlüsselten Ciphertext-Blob + Share-ID (`UUID`).         │
│    • Der Server kennt den Schlüssel `K_sym` zu KEINEM Zeitpunkt.                        │
│                                                                                         │
│ 3. Link-Generierung:                                                                    │
│    • Link: `https://salus.app/s/<UUID>#key=<Base64(K_sym)>&pin_salt=<Salt>`            │
│    • Der Hash-Teil (`#key=...`) wird laut HTTP-Standard NIEMALS an den Server gesendet!│
│                                                                                         │
│ 4. Abruf durch den Arzt:                                                                │
│    • Arzt öffnet den Link -> Browser extrahiert `K_sym` aus dem URL-Hash.              │
│    • Falls PIN geschützt: `K_sym` wird zusätzlich mit PBKDF2(PIN, Salt) entschlüsselt. │
│    • Lokale Entschlüsselung und Darstellung im Arzt-Dashboard.                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Authentifizierung & Session-Härtung

1. **Session-Cookie:** `salus_session` mit `HttpOnly; Secure; SameSite=Lax`.
2. **Content Security Policy (CSP):** `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self' wss:`.
3. **API-Token Scopes:** Granulare Token-Rechte (`metrics:read`, `metrics:write`, `workouts:read`, `labs:read`) für externe Skripte und Wearable-Webhooks.
