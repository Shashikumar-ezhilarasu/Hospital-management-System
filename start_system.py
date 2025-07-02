#!/usr/bin/env python3
"""
Hospital Management System Startup Script
This script helps you start both the Flask server and CLI interface
"""
import subprocess
import time
import sys
import os
import requests
from colorama import Fore, Style, init

init()

def check_server_running(url="http://127.0.0.1:5002/api/query", timeout=5):
    """Check if the Flask server is running"""
    try:
        response = requests.post(url, json={"query": "test"}, timeout=timeout)
        return True
    except:
        return False

def start_flask_server():
    """Start the Flask server in the background"""
    print(f"{Fore.YELLOW}🚀 Starting Flask server...{Style.RESET_ALL}")
    
    # Get the Python executable path
    python_path = "/Users/shashikumarezhil/Documents/JOB/.venv/bin/python"
    
    if not os.path.exists(python_path):
        python_path = "python3"  # Fallback
    
    try:
        # Start Flask server in background
        process = subprocess.Popen([python_path, "new.py"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server is running
        if check_server_running():
            print(f"{Fore.GREEN}✅ Flask server started successfully on port 5002{Style.RESET_ALL}")
            return process
        else:
            print(f"{Fore.RED}❌ Failed to start Flask server{Style.RESET_ALL}")
            return None
            
    except Exception as e:
        print(f"{Fore.RED}❌ Error starting Flask server: {e}{Style.RESET_ALL}")
        return None

def start_cli():
    """Start the CLI interface"""
    print(f"{Fore.YELLOW}🎯 Starting CLI interface...{Style.RESET_ALL}")
    time.sleep(1)
    
    # Get the Python executable path
    python_path = "/Users/shashikumarezhil/Documents/JOB/.venv/bin/python"
    
    if not os.path.exists(python_path):
        python_path = "python3"  # Fallback
    
    try:
        subprocess.run([python_path, "query_cli.py"])
    except Exception as e:
        print(f"{Fore.RED}❌ Error starting CLI: {e}{Style.RESET_ALL}")

def main():
    """Main startup function"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}🏥 Hospital Management System Startup")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    # Check if server is already running
    if check_server_running():
        print(f"{Fore.GREEN}✅ Flask server is already running{Style.RESET_ALL}")
        start_cli()
    else:
        # Start Flask server
        server_process = start_flask_server()
        
        if server_process:
            try:
                # Start CLI
                start_cli()
            finally:
                # Cleanup: terminate server when CLI exits
                print(f"\n{Fore.YELLOW}🔄 Shutting down Flask server...{Style.RESET_ALL}")
                server_process.terminate()
                server_process.wait()
                print(f"{Fore.GREEN}✅ System shutdown complete{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
