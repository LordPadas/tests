#!/usr/bin/env python3
import paramiko
import sys
import time

def deploy_to_server(host, port, username, password, remote_path):
    print(f"[*] Connecting to {host}:{port}...")
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, port=port, username=username, password=password, timeout=30)
        print(f"[+] Connected!")
        
        # Check if remote directory exists
        stdin, stdout, stderr = client.exec_command(f"ls -la {remote_path}")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status != 0:
            print(f"[*] Creating remote directory: {remote_path}")
            stdin, stdout, stderr = client.exec_command(f"mkdir -p {remote_path}")
            stdout.channel.recv_exit_status()
        
        # Get current local files to transfer
        print(f"[*] Checking local files...")
        
        # Create a simple test command
        test_cmd = "echo 'Connection works!' && docker --version && docker compose version"
        print(f"[*] Running test command: {test_cmd}")
        stdin, stdout, stderr = client.exec_command(test_cmd)
        
        print(f"\n=== STDOUT ===\n{stdout.read().decode()}")
        print(f"\n=== STDERR ===\n{stderr.read().decode()}")
        
        client.close()
        print("\n[+] Done!")
        return True
        
    except paramiko.AuthenticationException:
        print("[!] Authentication failed!")
        return False
    except Exception as e:
        print(f"[!] Error: {e}")
        return False

if __name__ == "__main__":
    HOST = "10.14.0.41"
    PORT = 22
    USER = "admin1"
    PASS = "1q2w3e4r"
    REMOTE_PATH = "/home/admin1/projeckt"
    
    success = deploy_to_server(HOST, PORT, USER, PASS, REMOTE_PATH)
    sys.exit(0 if success else 1)