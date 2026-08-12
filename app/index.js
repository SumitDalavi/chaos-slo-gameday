const express = require('express');
const promClient = require('prom-client');

const app = express();
const PORT = 3000;

// Prometheus metrics
const register = promClient.register;
promClient.collectDefaultMetrics();

const httpRequestDuration = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status'],
  buckets: [0.01, 0.05, 0.1, 0.3, 0.5, 1, 2, 5]
});

const httpRequestTotal = new promClient.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status']
});

// Middleware to track metrics
app.use((req, res, next) => {
  const end = httpRequestDuration.startTimer();
  res.on('finish', () => {
    end({ method: req.method, route: req.path, status: res.statusCode });
    httpRequestTotal.inc({ method: req.method, route: req.path, status: res.statusCode });
  });
  next();
});

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

app.get('/api/data', (req, res) => {
  // Simulate variable latency
  const delay = Math.random() * 300;
  setTimeout(() => {
    if (Math.random() < 0.02) { // 2% error rate
      res.status(500).json({ error: 'Internal server error' });
    } else {
      res.json({ data: 'sample response', latency_ms: delay.toFixed(0) });
    }
  }, delay);
});

app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.send(await register.metrics());
});

app.listen(PORT, () => console.log(`Target app listening on port ${PORT}`));
