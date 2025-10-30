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

def start_grafana():
    """Start Grafana dashboard"""
    print("Starting Grafana...")
    
    # Set Grafana environment variables
    env = os.environ.copy()
    env['GF_PATHS_DATA'] = 'monitoring/grafana_data'
    env['GF_PATHS_LOGS'] = 'monitoring/grafana_logs'
    env['GF_PATHS_PROVISIONING'] = 'monitoring/grafana/provisioning'
    
    grafana_process = subprocess.Popen([
        r'C:\grafana-12.2.1\bin\grafana-server',
        '--config=monitoring/grafana.ini',
        '--homepath=/usr/share/grafana'
    ], env=env)
    
    return grafana_process

if __name__ == '__main__':
    print("Starting Monitoring Stack...")
    
    try:
        # Start Prometheus
        prometheus = start_prometheus()
        
        # Start Grafana
        # grafana = start_grafana()
        
        print(f"Prometheus started at: http://localhost:{Config.PROMETHEUS_PORT}")
        # print(f"Grafana started at: http://localhost:{Config.GRAFANA_PORT}")
        print("Monitoring stack is running. Press Ctrl+C to stop.")
        
        # Keep the script running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping monitoring stack...")
        prometheus.terminate()
        # grafana.terminate()
        print("Monitoring stack stopped.")