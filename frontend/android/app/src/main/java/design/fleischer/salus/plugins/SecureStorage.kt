package design.fleischer.salus.plugins

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

/**
 * Hardware-backed encrypted preference store. Single source of truth for
 * secrets and the background-sync durable state, shared by the foreground
 * Capacitor bridge (SecureStoragePlugin) and the background HealthSyncWorker.
 */
object SecureStorage {

    private const val PREF_NAME = "salus_secure"

    private const val KEY_TOKEN = "auth_token"
    private const val KEY_SERVER_URL = "server_url"
    private const val KEY_LAST_HARVEST = "last_harvest_at"

    private fun prefs(context: Context): SharedPreferences {
        val masterKey = MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
        return EncryptedSharedPreferences.create(
            context,
            PREF_NAME,
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    }

    private fun getString(context: Context, key: String): String? {
        return try {
            prefs(context).getString(key, null)
        } catch (e: Exception) {
            null
        }
    }

    private fun setString(context: Context, key: String, value: String?) {
        try {
            prefs(context).edit().apply {
                if (value.isNullOrEmpty()) remove(key) else putString(key, value)
            }.apply()
        } catch (_: Exception) {
            // ignore — storage failures must never crash the app
        }
    }

    fun token(context: Context): String? = getString(context, KEY_TOKEN)

    fun setToken(context: Context, token: String?) = setString(context, KEY_TOKEN, token)

    fun serverUrl(context: Context): String? = getString(context, KEY_SERVER_URL)

    fun setServerUrl(context: Context, url: String?) = setString(context, KEY_SERVER_URL, url)

    fun lastHarvestAt(context: Context): String? = getString(context, KEY_LAST_HARVEST)

    fun setLastHarvestAt(context: Context, value: String?) = setString(context, KEY_LAST_HARVEST, value)
}
