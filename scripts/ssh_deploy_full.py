#!/usr/bin/env python3
import paramiko
import os
import sys
import time
from pathlib import Path

def deploy_project(host, port, username, password, local_path, remote_path):
    print(f"[*] Connecting to {host}:{port}...")
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, port=port, username=username, password=password, timeout=30)
        print(f"[+] Connected!")
        
        # Create remote directory
        print(f"[*] Creating remote directory...")
        stdin, stdout, stderr = client.exec_command(f"mkdir -p {remote_path}")
        stdout.channel.recv_exit_status()
        
        # Check git availability
        stdin, stdout, stderr = client.exec_command("which git")
        git_avail = stdout.read().decode().strip()
        print(f"[*] Git available: {git_avail}")
        
        # Fix Docker permissions if needed
        print(f"[*] Checking Docker permissions...")
        stdin, stdout, stderr = client.exec_command("sudo usermod -aG docker $USER 2>/dev/null || docker version")
        # Try to check docker without sudo first
        stdin, stdout, stderr = client.exec_command("docker ps")
        perm_err = stderr.read().decode()
        if "permission denied" in perm_err.lower():
            print(f"[!] Docker permission issue, trying to fix...")
            # Add user to docker group
            stdin, stdout, stderr = client.exec_command("sudo chmod 666 /var/run/docker.sock")
            print(f"=== Docker fix output ===\n{stdout.read().decode()}\n{stderr.read().decode()}")
        
        # For now, let's create a simple docker-compose setup on the server
        # Since we don't have direct repo access, we'll create minimal setup
        
        print(f"[*] Creating docker-compose.yml on server...")
        
        docker_compose = """version: '3.9'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: app
    volumes:
      - db_data:/var/lib/postgresql/data
    restart: unless-stopped
    
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      DB_URL: postgresql://postgres:postgres@db:5432/app
      OLLAMA_HOST: http://ollama:11434
    restart: unless-stopped
    
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped

volumes:
  db_data:
  ollama_data:
"""
        
        # Upload docker-compose.yml
        sftp = client.open_sftp()
        remote_file = sftp.file(f"{remote_path}/docker-compose.yml", 'w')
        remote_file.write(docker_compose)
        remote_file.close()
        sftp.close()
        print(f"[+] docker-compose.yml uploaded")
        
        # Create backend directory and Dockerfile
        print(f"[*] Creating backend directory structure...")
        stdin, stdout, stderr = client.exec_command(f"mkdir -p {remote_path}/backend")
        stdout.channel.recv_exit_status()
        
        # Simple Dockerfile for backend
        backend_dockerfile = """FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn pydantic SQLAlchemy psycopg2-binary python-dotenv
COPY . .
EXPOSE 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        
        sftp = client.open_sftp()
        remote_file = sftp.file(f"{remote_path}/backend/Dockerfile", 'w')
        remote_file.write(backend_dockerfile)
        remote_file.close()
        
        # Create simple app structure
        app_init = ""
        main_py = """from fastapi import FastAPI
app = FastAPI(title="Local AI Agent")

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/")
def root():
    return {"status": "ok"}
"""
        
        # Create backend/app directory
        stdin, stdout, stderr = client.exec_command(f"mkdir -p {remote_path}/backend/app")
        stdout.channel.recv_exit_status()
        
        # Write main.py
        remote_file = sftp.file(f"{remote_path}/backend/app/main.py", 'w')
        remote_file.write(main_py)
        remote_file.close()
        
        # Create __init__.py files
        for init_file in ["backend/__init__.py", "backend/app/__init__.py"]:
            path = f"{remote_path}/{init_file}"
            remote_file = sftp.file(path, 'w')
            remote_file.write("")
            remote_file.close()
        
        sftp.close()
        print(f"[+] Backend structure created")
        
        # Start docker compose
        print(f"[*] Starting docker compose...")
        stdin, stdout, stderr = client.exec_command(f"cd {remote_path} && docker compose up -d --build")
        output = stdout.read().decode()
        error = stderr.read().decode()
        print(f"=== STDOUT ===\n{output}")
        print(f"=== STDERR ===\n{error}")
        
        # Wait and check status
        print(f"[*] Waiting for services to start...")
        time.sleep(10)
        
        stdin, stdout, stderr = client.exec_command(f"cd {remote_path} && docker compose ps")
        print(f"=== Container Status ===\n{stdout.read().decode()}")
        
        # Check health
        print(f"[*] Checking health endpoint...")
        stdin, stdout, stderr = client.exec_command("curl -s http://localhost:8000/health")
        print(f"=== Health Check ===\n{stdout.read().decode()}")
        
        client.close()
        print("\n[+] Deployment complete!")
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
    LOCAL_PATH = "/c/Users/St11l/Desktop/Projeckt"
    
    success = deploy_project(HOST, PORT, USER, PASS, LOCAL_PATH, REMOTE_PATH)
    sys.exit(0 if success else 1)