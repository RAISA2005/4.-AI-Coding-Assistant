#!/usr/bin/env python3
"""
AI LIBRARY ASSISTANT LAUNCHER
Run this file: python stream.py
"""

import subprocess
import sys
import os
import socket

def check_port_available(port):
    """Check if port is available"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result != 0  # Port is available if connection fails
    except:
        return True

def find_available_port():
    """Find an available port starting from 8501"""
    for port in [8501, 8502, 8503, 8504, 8505]:
        if check_port_available(port):
            return port
    return 8501  # Default if none available

def check_requirements():
    """Check if all requirements are met"""
    print("\n" + "="*60)
    print("📚 AI LIBRARY ASSISTANT - SETUP CHECK")
    print("="*60)
    
    # Check .env file
    if not os.path.exists('.env'):
        print("❌ ERROR: .env file not found!")
        print("\nCreate a .env file with this content:")
        print("HF_TOKEN=your_actual_huggingface_token_here")
        print("\nGet token from: https://huggingface.co/settings/tokens")
        return False
    
    # Check HF_TOKEN
    try:
        with open('.env', 'r') as f:
            content = f.read()
            if 'HF_TOKEN=' not in content:
                print("❌ ERROR: HF_TOKEN not found in .env file!")
                return False
            if 'your_token' in content:
                print("⚠️  WARNING: Using placeholder token in .env")
                print("   Replace 'your_token' with your actual Hugging Face token")
    except:
        print("❌ ERROR: Cannot read .env file")
        return False
    
    print("✅ .env file check passed")
    
    # Check Python packages
    try:
        import streamlit
        print("✅ Streamlit installed")
    except:
        print("❌ Streamlit not installed")
        print("   Run: pip install streamlit")
        return False
    
    return True

def main():
    """Main function to launch the app"""
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Setup failed. Please fix the issues above.")
        return 1
    
    # Find available port
    port = find_available_port()
    
    print(f"\n🚀 STARTING AI LIBRARY ASSISTANT")
    print("-"*40)
    print(f"📁 Directory: {os.getcwd()}")
    print(f"🔌 Using port: {port}")
    print(f"🌐 URL: http://localhost:{port}")
    print("\n⏳ Loading... (first time may take 30-60 seconds)")
    print("\n" + "="*60)
    print("✨ FEATURES:")
    print("  • Age-based filtering")
    print("  • Student status detection")
    print("  • Real-time web search for books")
    print("  • AI-generated summaries")
    print("  • Smart book suggestions")
    print("  • Student discounts (25% off)")
    print("="*60)
    print("\nPress Ctrl+C to stop the application")
    print("="*60 + "\n")
    
    try:
        # Launch Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            "app.py",
            f"--server.port={port}",
            "--server.address=localhost",
            "--theme.base=light",
            "--browser.gatherUsageStats=false"
        ]
        
        process = subprocess.Popen(cmd)
        process.wait()
        
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("👋 APPLICATION STOPPED")
        print("="*60)
        return 0
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())