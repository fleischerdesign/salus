package design.fleischer.salus

import android.os.Bundle
import androidx.work.Constraints
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.NetworkType
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import com.getcapacitor.BridgeActivity
import design.fleischer.salus.plugins.HealthConnectPlugin
import design.fleischer.salus.plugins.HealthSyncWorker
import design.fleischer.salus.plugins.SecureStoragePlugin
import java.util.concurrent.TimeUnit

class MainActivity : BridgeActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        registerPlugin(HealthConnectPlugin::class.java)
        registerPlugin(SecureStoragePlugin::class.java)
        super.onCreate(savedInstanceState)
        scheduleBackgroundSync()
    }

    private fun scheduleBackgroundSync() {
        val constraints = Constraints.Builder()
            .setRequiresBatteryNotLow(true)
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()

        val request = PeriodicWorkRequestBuilder<HealthSyncWorker>(15, TimeUnit.MINUTES)
            .setConstraints(constraints)
            .build()

        WorkManager.getInstance(this).enqueueUniquePeriodicWork(
            "salus_health_sync",
            ExistingPeriodicWorkPolicy.KEEP,
            request
        )
    }
}
