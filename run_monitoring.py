import subprocess
import time
import os
from config.settings import Config

def ensure_dir(path):
    """Create directory if it doesn't exist with proper permissions"""
    abs_path = os.path.abspath(path)
    os.makedirs(abs_path, exist_ok=True)
    return abs_path

def start_prometheus():
    """Start Prometheus monitoring"""
    print("Starting Prometheus...")
    
    # Ensure data directory exists with proper permissions
    data_dir = ensure_dir('monitoring/prometheus_data')
    config_file = os.path.abspath('monitoring/prometheus.yml')
    
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Prometheus config file not found: {config_file}")
    
    prometheus_process = subprocess.Popen([
        r'C:\prometheus-3.7.3.windows-amd64\prometheus.exe',
        f'--config.file={config_file}',
        '--web.listen-address=:9090',
        f'--storage.tsdb.path={data_dir}',
        '--web.enable-lifecycle'  # Enable hot reload
    ])
    return prometheus_process

if __name__ == '__main__':
    print("Starting Monitoring Stack...")
    
    try:
        # Start Prometheus
        prometheus = start_prometheus()
        
        print(f"Prometheus started at: http://localhost:{Config.PROMETHEUS_PORT}")
        print(f"Grafana is running at: http://localhost:{Config.GRAFANA_PORT}")
        print("\nTo configure Grafana with Prometheus:")
        print("1. Open Grafana at http://localhost:3000")
        print("2. Log in with default credentials (admin/admin) if you haven't changed them")
        print("3. Go to 'Configuration' -> 'Data Sources'")
        print("4. Click 'Add data source' and select 'Prometheus'")
        print("5. Set URL to 'http://localhost:9090'")
        print("6. Click 'Save & Test'\n")
        print("Monitoring stack is running. Press Ctrl+C to stop.")
        
        # Keep the script running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping monitoring stack...")
        prometheus.terminate()
        print("Prometheus stopped. Grafana is still running as a Windows service.")