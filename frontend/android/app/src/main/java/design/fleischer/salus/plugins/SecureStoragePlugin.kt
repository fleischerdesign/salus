package design.fleischer.salus.plugins

import com.getcapacitor.Plugin
import com.getcapacitor.PluginCall
import com.getcapacitor.PluginMethod
import com.getcapacitor.annotation.CapacitorPlugin

/**
 * Exposes the hardware-backed SecureStorage to the JS bridge so the SPA can
 * persist the auth token and server URL for the background sync worker.
 */
@CapacitorPlugin(name = "SecureStoragePlugin")
class SecureStoragePlugin : Plugin() {

    @PluginMethod
    fun setToken(call: PluginCall) {
        SecureStorage.setToken(context, call.getString("token"))
        call.resolve()
    }

    @PluginMethod
    fun setServerUrl(call: PluginCall) {
        SecureStorage.setServerUrl(context, call.getString("url"))
        call.resolve()
    }

    @PluginMethod
    fun clear(call: PluginCall) {
        SecureStorage.setToken(context, null)
        SecureStorage.setServerUrl(context, null)
        call.resolve()
    }
}
