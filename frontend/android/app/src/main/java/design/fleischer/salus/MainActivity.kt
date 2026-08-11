package design.fleischer.salus

import android.os.Bundle
import com.getcapacitor.BridgeActivity
import design.fleischer.salus.plugins.HealthConnectPlugin

class MainActivity : BridgeActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        registerPlugin(HealthConnectPlugin::class.java)
        super.onCreate(savedInstanceState)
    }
}
