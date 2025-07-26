import platform
import psutil
import os
from datetime import datetime

def get_system_info():
    """Gather comprehensive system information."""
    info = {
        'system': {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'hostname': platform.node(),
            'processor': platform.processor(),
            'python_version': platform.python_version()
        },
        'memory': {
            'total': psutil.virtual_memory().total,
            'available': psutil.virtual_memory().available,
            'percent': psutil.virtual_memory().percent,
            'used': psutil.virtual_memory().used,
            'free': psutil.virtual_memory().free
        },
        'disk': {},
        'network': {},
        'timestamp': datetime.now().isoformat()
    }
    
    # Disk information
    disk_partitions = psutil.disk_partitions()
    for partition in disk_partitions:
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
            info['disk'][partition.device] = {
                'mountpoint': partition.mountpoint,
                'file_system': partition.fstype,
                'total_size': partition_usage.total,
                'used': partition_usage.used,
                'free': partition_usage.free,
                'percentage': (partition_usage.used / partition_usage.total) * 100
            }
        except PermissionError:
            continue
    
    # Network information
    network_stats = psutil.net_io_counters()
    info['network'] = {
        'bytes_sent': network_stats.bytes_sent,
        'bytes_received': network_stats.bytes_recv,
        'packets_sent': network_stats.packets_sent,
        'packets_received': network_stats.packets_recv
    }
    
    return info

def format_bytes(bytes_value):
    """Convert bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"

def print_system_info():
    """Print formatted system information."""
    info = get_system_info()
    
    print("=" * 50)
    print("SYSTEM INFORMATION")
    print("=" * 50)
    
    print(f"Platform: {info['system']['platform']} {info['system']['platform_release']}")
    print(f"Architecture: {info['system']['architecture']}")
    print(f"Hostname: {info['system']['hostname']}")
    print(f"Processor: {info['system']['processor']}")
    print(f"Python Version: {info['system']['python_version']}")
    
    print("\n" + "=" * 50)
    print("MEMORY INFORMATION")
    print("=" * 50)
    print(f"Total: {format_bytes(info['memory']['total'])}")
    print(f"Available: {format_bytes(info['memory']['available'])}")
    print(f"Used: {format_bytes(info['memory']['used'])} ({info['memory']['percent']}%)")
    print(f"Free: {format_bytes(info['memory']['free'])}")
    
    print("\n" + "=" * 50)
    print("DISK INFORMATION")
    print("=" * 50)
    for device, disk_info in info['disk'].items():
        print(f"Device: {device}")
        print(f"  Mountpoint: {disk_info['mountpoint']}")
        print(f"  File System: {disk_info['file_system']}")
        print(f"  Total: {format_bytes(disk_info['total_size'])}")
        print(f"  Used: {format_bytes(disk_info['used'])} ({disk_info['percentage']:.1f}%)")
        print(f"  Free: {format_bytes(disk_info['free'])}")
        print()
    
    print("=" * 50)
    print("NETWORK INFORMATION")
    print("=" * 50)
    print(f"Bytes Sent: {format_bytes(info['network']['bytes_sent'])}")
    print(f"Bytes Received: {format_bytes(info['network']['bytes_received'])}")
    print(f"Packets Sent: {info['network']['packets_sent']:,}")
    print(f"Packets Received: {info['network']['packets_received']:,}")

if __name__ == "__main__":
    print_system_info()
