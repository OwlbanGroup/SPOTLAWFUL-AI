import time
import threading

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'accuracy': [],
            'latency': [],
            'error_rate': [],
            'user_satisfaction': []
        }
        self.alert_thresholds = {
            'accuracy': 0.8,
            'latency': 1.0,  # seconds
            'error_rate': 0.05,
            'user_satisfaction': 0.7
        }
        self.alerts = []

    def record_metric(self, metric_name, value):
        if metric_name in self.metrics:
            self.metrics[metric_name].append(value)
            self.check_alerts(metric_name, value)

    def check_alerts(self, metric_name, value):
        threshold = self.alert_thresholds.get(metric_name)
        if threshold is not None:
            if (metric_name in ['accuracy', 'user_satisfaction'] and value < threshold) or \
               (metric_name in ['latency', 'error_rate'] and value > threshold):
                alert_msg = f"Alert: {metric_name} value {value} crossed threshold {threshold}"
                self.alerts.append(alert_msg)
                print(alert_msg)

    def get_latest_metrics(self):
        return {k: v[-1] if v else None for k, v in self.metrics.items()}

    def start_monitoring(self, interval=60):
        def monitor_loop():
            while True:
                latest_metrics = self.get_latest_metrics()
                print(f"Performance Metrics: {latest_metrics}")
                time.sleep(interval)
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
