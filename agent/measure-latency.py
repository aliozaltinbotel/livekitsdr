#!/usr/bin/env python3
"""
Measure latency between Azure services and LiveKit Cloud
"""

import asyncio
import time
import statistics
import socket
from urllib.parse import urlparse
import subprocess
import json

# Your services
LIVEKIT_URL = "wss://botelsdr-5apszb2n.livekit.cloud"
AZURE_REGION = "eastus"

def get_hostname_from_ws_url(ws_url):
    """Extract hostname from WebSocket URL"""
    parsed = urlparse(ws_url)
    return parsed.hostname

def ping_host(hostname, count=10):
    """Ping a host and return latency statistics"""
    try:
        # Use ping command
        cmd = ["ping", "-c", str(count), hostname]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return None
        
        # Parse ping output
        lines = result.stdout.split('\n')
        latencies = []
        
        for line in lines:
            if "time=" in line:
                # Extract time value
                time_part = line.split("time=")[1].split()[0]
                latency = float(time_part.replace("ms", ""))
                latencies.append(latency)
        
        if latencies:
            return {
                "min": min(latencies),
                "max": max(latencies),
                "avg": statistics.mean(latencies),
                "samples": len(latencies)
            }
    except Exception as e:
        print(f"Error pinging {hostname}: {e}")
    
    return None

def resolve_hostname(hostname):
    """Resolve hostname to IP address"""
    try:
        ip = socket.gethostbyname(hostname)
        return ip
    except:
        return None

def main():
    print("🔍 LiveKit Cloud Latency Analysis")
    print("=" * 50)
    
    # Extract LiveKit hostname
    livekit_host = get_hostname_from_ws_url(LIVEKIT_URL)
    print(f"LiveKit Cloud URL: {LIVEKIT_URL}")
    print(f"LiveKit Hostname: {livekit_host}")
    
    # Resolve IP
    livekit_ip = resolve_hostname(livekit_host)
    if livekit_ip:
        print(f"LiveKit IP: {livekit_ip}")
    
    print(f"\nYour Azure Region: {AZURE_REGION}")
    print("\n📊 Latency Measurements (10 pings)")
    print("-" * 50)
    
    # Measure latency to LiveKit
    print(f"\nPinging LiveKit Cloud ({livekit_host})...")
    livekit_stats = ping_host(livekit_host)
    
    if livekit_stats:
        print(f"✅ LiveKit Cloud Latency:")
        print(f"   Min: {livekit_stats['min']:.2f} ms")
        print(f"   Max: {livekit_stats['max']:.2f} ms")
        print(f"   Avg: {livekit_stats['avg']:.2f} ms")
        print(f"   Samples: {livekit_stats['samples']}")
    else:
        print("❌ Could not measure LiveKit latency")
    
    # Test Azure endpoints for comparison
    azure_endpoints = {
        "Azure East US": "eastus.api.cognitive.microsoft.com",
        "Azure West US": "westus.api.cognitive.microsoft.com",
        "Azure West Europe": "westeurope.api.cognitive.microsoft.com"
    }
    
    print("\n📍 Azure Region Latencies (for comparison):")
    print("-" * 50)
    
    for region, endpoint in azure_endpoints.items():
        stats = ping_host(endpoint, count=5)
        if stats:
            print(f"\n{region} ({endpoint}):")
            print(f"   Avg latency: {stats['avg']:.2f} ms")
    
    # Recommendations
    print("\n💡 Latency Optimization Recommendations:")
    print("-" * 50)
    
    if livekit_stats and livekit_stats['avg'] < 20:
        print("✅ Excellent latency (<20ms) - LiveKit server is likely in the same region")
    elif livekit_stats and livekit_stats['avg'] < 50:
        print("✅ Good latency (<50ms) - Suitable for real-time voice")
    elif livekit_stats and livekit_stats['avg'] < 100:
        print("⚠️  Moderate latency (50-100ms) - May notice slight delays")
    else:
        print("❌ High latency (>100ms) - Consider requesting a closer LiveKit region")
    
    print("\n📝 Total Round-Trip Latency Estimation:")
    print("- User → LiveKit: ~X ms (depends on user location)")
    if livekit_stats:
        print(f"- LiveKit → Azure (your agent): ~{livekit_stats['avg']:.2f} ms")
        print(f"- Azure processing: ~50-100 ms (STT + LLM + TTS)")
        print(f"- Total agent latency: ~{livekit_stats['avg'] + 75:.0f} ms + user latency")

if __name__ == "__main__":
    main()