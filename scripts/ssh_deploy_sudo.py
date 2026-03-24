#!/usr/bin/env python3
import paramiko
import sys
import time

def deploy_with_sudo(host, port, username, password, remote_path):
    print(f"[*] Connecting to {host}:{port}...")
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, port=port, username=username, password=password, timeout=30)
        print(f"[+] Connected!")
        
        # Check current user and groups
        stdin, stdout, stderr = client.exec_command("id")
        print(f"[*] Current user: {stdout.read().decode()}")
        
        # Try to add user to docker group
        print(f"[*] Trying to add user to docker group...")
        stdin, stdout, stderr = client.exec_command(f"echo '{password}' | sudo -S usermod -aG docker {username}")
        print(f"=== sudo usermod ===\n{stdout.read().decode()}\n{stderr.read().decode()}")
        
        # Try alternative - make docker socket accessible
        print(f"[*] Trying to fix Docker socket permissions...")
        stdin, stdout, stderr = client.exec_command(f"echo '{password}' | sudo -S chmod 666 /var/run/docker.sock")
        print(f"=== chmod socket ===\n{stdout.read().decode()}\n{stderr.read().decode()}")
        
        # Check docker now
        stdin, stdout, stderr = client.exec_command("docker ps")
        print(f"=== Docker check ===\n{stdout.read().decode()}\n{stderr.read().decode()}")
        
        # If still not working, try docker compose with sudo
        print(f"[*] Attempting docker compose up with sudo...")
        stdin, stdout, stderr = client.exec_command(f"echo '{password}' | sudo -S bash -c 'cd {remote_path} && docker compose up -d --build'")
        print(f"=== docker compose up ===\n{stdout.read().decode()}\n{stderr.read().decode()}")
        
        # Check containers
        time.sleep(15)
        stdin, stdout, stderr = client.exec_command(f"echo '{password}' | sudo -S docker compose -f {remote_path}/docker-compose.yml ps")
        print(f"=== Container status ===\n{stdout.read().decode()}")
        
        # Try health check via sudo curl
        stdin, stdout, stderr = client.exec_command(f"echo '{password}' | sudo -S curl -s http://localhost:8000/health")
        print(f"=== Health check ===\n{stdout.read().decode()}")
        
        client.close()
        print("\n[+] Done!")
        return True
        
    except Exception as e:
        print(f"[!] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    HOST = "10.14.0.41"
    PORT = 22
    USER = "admin1"
    PASS = "1q2w3e4r"
    REMOTE_PATH = "/home/admin1/projeckt"
    
    success = deploy_with_sudo(HOST, PORT, USER, PASS, REMOTE_PATH)
    sys.exit(0 if success else 1)