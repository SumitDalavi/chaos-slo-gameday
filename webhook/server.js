const express = require('express');
const { exec } = require('child_process');

const app = express();
app.use(express.json());

const PORT = 8080;

app.post('/alert', (req, res) => {
  const alert = req.body;
  
  console.log(`[Webhook] Received alert: ${JSON.stringify(alert.alerts[0].labels.alertname)}`);

  // Check if this is the ErrorBudgetBurnRateCritical alert
  if (alert.alerts.some(a => a.labels.alertname === 'ErrorBudgetBurnRateCritical' && a.status === 'firing')) {
    console.log('[ACTION] Error budget exhausted! Initiating deployment freeze...');
    
    // Simulate triggering a deployment freeze in CI/CD (e.g. via GitHub API)
    // In a real K8s environment, this could also involve annotating the namespace or scaling down
    console.log('  -> Calling CI/CD API to lock deployments to "production" namespace');
    
    // Example: Annotate namespace to block changes (if using OPA/Kyverno rules)
    const cmd = `kubectl annotate namespace default change-freeze="true" --overwrite`;
    
    exec(cmd, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error executing freeze command: ${error.message}`);
        return res.status(500).json({ status: 'error', message: 'Failed to freeze deployments' });
      }
      console.log(`  -> Freeze successful: ${stdout}`);
      return res.status(200).json({ status: 'success', action: 'deployment_freeze' });
    });
  } else {
    res.status(200).json({ status: 'ignored', message: 'Not an error budget critical alert' });
  }
});

app.listen(PORT, () => {
  console.log(`SLO Webhook receiver listening on port ${PORT}`);
});
