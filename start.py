#!/usr/bin/env python3
"""
DU Admission Analyzer - Full Stack Application Startup Script
Production-ready web application with advanced features
"""

import sys
import os
import subprocess
import platform
import webbrowser
from pathlib import Path
import time
import socket

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {platform.python_version()}")
        return False
    print(f"✅ Python {platform.python_version()} detected")
    return True

def check_port_available(port=8000):
    """Check if port is available"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def find_available_port(start_port=8000):
    """Find an available port starting from start_port"""
    port = start_port
    while port < start_port + 100:
        if check_port_available(port):
            return port
        port += 1
    return None

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def setup_directories():
    """Create necessary directories"""
    print("📁 Setting up directories...")
    directories = ["data", "outputs", "uploads", "static", "templates"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Directories created")

def check_java_installation():
    """Check if Java is installed (required for tabula-py)"""
    try:
        result = subprocess.run(["java", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Java is installed")
            return True
    except FileNotFoundError:
        pass
    
    print("⚠️  Warning: Java not found. Some PDF extraction features may not work.")
    print("   Please install Java 8 or higher for full functionality.")
    return False

def start_server(port=8000, debug=False):
    """Start the FastAPI server"""
    print(f"🚀 Starting DU Admission Analyzer on port {port}...")
    
    # Prepare environment
    env = os.environ.copy()
    env['PYTHONPATH'] = str(Path.cwd())
    
    # Server command
    cmd = [
        sys.executable, 
        "-m", "uvicorn", 
        "app:app",
        "--host", "0.0.0.0",
        "--port", str(port)
    ]
    
    if debug:
        cmd.extend(["--reload", "--log-level", "debug"])
    
    try:
        # Start server in background for URL opening
        process = subprocess.Popen(cmd, env=env)
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Open browser
        url = f"http://localhost:{port}"
        print(f"🌐 Application running at: {url}")
        
        if not debug:
            try:
                webbrowser.open(url)
                print("🔗 Opening in your default browser...")
            except Exception as e:
                print(f"Could not open browser automatically: {e}")
                print(f"Please visit {url} manually")
        
        # Wait for server
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        if 'process' in locals():
            process.terminate()
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🎓 DU Admission Analyzer - Full Stack Application")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Setup directories
    setup_directories()
    
    # Check Java (optional)
    check_java_installation()
    
    # Parse command line arguments
    debug_mode = "--debug" in sys.argv or "--dev" in sys.argv
    skip_install = "--skip-install" in sys.argv
    port = 8000
    
    # Parse port from arguments
    for arg in sys.argv:
        if arg.startswith("--port="):
            try:
                port = int(arg.split("=")[1])
            except ValueError:
                print("❌ Invalid port number")
                return 1
    
    # Find available port
    if not check_port_available(port):
        new_port = find_available_port(port)
        if new_port:
            print(f"⚠️  Port {port} is busy, using port {new_port}")
            port = new_port
        else:
            print(f"❌ No available ports found starting from {port}")
            return 1
    
    # Install dependencies
    if not skip_install:
        if not install_dependencies():
            return 1
    else:
        print("⏭️  Skipping dependency installation")
    
    # Start server
    success = start_server(port, debug_mode)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
