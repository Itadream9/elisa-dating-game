"""
IL CUSTODE DEL CAVEAU - System Launcher
Starts all components: Ollama, Backend, Frontend, ngrok tunnel
"""
import subprocess
import sys
import time
import os
import signal
import threading
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

BACKEND_PORT = 8000
FRONTEND_PORT = 5173

# Store process references for cleanup
processes = []


def run_command(cmd, cwd=None, name="Process", env=None):
    """Run a command and return the process."""
    print(f"[{name}] Starting: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    
    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        shell=isinstance(cmd, str),
        env=env or os.environ.copy(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    processes.append((name, process))
    return process


def stream_output(process, name):
    """Stream process output to console."""
    try:
        for line in iter(process.stdout.readline, ''):
            if line:
                print(f"[{name}] {line.rstrip()}")
            if process.poll() is not None:
                break
    except Exception as e:
        print(f"[{name}] Output stream error: {e}")


def cleanup():
    """Clean up all running processes."""
    print("\n[System] Shutting down...")
    for name, proc in processes:
        try:
            proc.terminate()
            print(f"[{name}] Terminated")
        except Exception as e:
            print(f"[{name}] Error terminating: {e}")
    sys.exit(0)


def check_ollama():
    """Check if Ollama is running and start if needed."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("[Ollama] Service is running")
            return True
    except Exception:
        pass
    
    print("[Ollama] Starting Ollama service...")
    try:
        # Start ollama serve in background
        proc = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        processes.append(("Ollama", proc))
        time.sleep(3)  # Wait for service to start
        return True
    except Exception as e:
        print(f"[Ollama] Failed to start: {e}")
        return False


def start_backend():
    """Start the FastAPI backend."""
    print("[Backend] Starting FastAPI server...")
    
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    
    proc = run_command(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(BACKEND_PORT), "--reload"],
        cwd=str(BACKEND_DIR),
        name="Backend",
        env=env
    )
    
    # Stream output in thread
    thread = threading.Thread(target=stream_output, args=(proc, "Backend"), daemon=True)
    thread.start()
    
    return proc


def start_frontend():
    """Start the Vite frontend development server."""
    print("[Frontend] Starting Vite dev server...")
    
    proc = run_command(
        "npm run dev",
        cwd=str(FRONTEND_DIR),
        name="Frontend"
    )
    
    # Stream output in thread
    thread = threading.Thread(target=stream_output, args=(proc, "Frontend"), daemon=True)
    thread.start()
    
    return proc


def setup_ngrok():
    """Setup ngrok tunnel to frontend."""
    print("[ngrok] Setting up tunnel...")
    
    try:
        from pyngrok import ngrok, conf
        
        # Configure ngrok (you may need to set auth token)
        # conf.get_default().auth_token = "YOUR_AUTH_TOKEN"
        
        # Create tunnel to frontend
        tunnel = ngrok.connect(FRONTEND_PORT, "http")
        public_url = tunnel.public_url

        # Save URL to file for AI/User
        with open("ngrok_url_final.txt", "w") as f:
            f.write(public_url)
        
        print("\n" + "="*60)
        print("🔥 HARD TO GET (ELISA) - SISTEMA ATTIVO 🔥")
        print("="*60)
        print(f"\n📡 URL PUBBLICO: {public_url}")
        print(f"\n🖥️  URL LOCALE Frontend: http://localhost:{FRONTEND_PORT}")
        print(f"⚙️  URL LOCALE Backend:  http://localhost:{BACKEND_PORT}")
        print("\n" + "="*60)
        print("Premi Ctrl+C per terminare il sistema")
        print("="*60 + "\n")
        
        return public_url
        
    except Exception as e:
        print(f"[ngrok] Error: {e}")
        print("[ngrok] Tunnel non configurato. Accedi localmente.")
        print(f"\n🖥️  URL LOCALE: http://localhost:{FRONTEND_PORT}")
        return None


def main():
    """Main entry point."""
    print("\n" + "="*60)
    print("    HARD TO GET AI - AVVIO SISTEMA")
    print("    Dating Sim Challenge")
    print("="*60 + "\n")
    
    # Setup signal handler for cleanup
    signal.signal(signal.SIGINT, lambda s, f: cleanup())
    signal.signal(signal.SIGTERM, lambda s, f: cleanup())
    
    # Step 1: Check Ollama
    if not check_ollama():
        print("[ERROR] Ollama non disponibile. Assicurati che sia installato.")
        return
    
    # Step 2: Verify custode model exists
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True
        )
        if "custode" not in result.stdout:
            print("[Warning] Modello 'custode' non trovato. Crealo con: ollama create custode -f Modelfile")
    except Exception:
        pass
    
    # Step 3: Install frontend dependencies if needed
    if not (FRONTEND_DIR / "node_modules").exists():
        print("[Frontend] Installing npm dependencies...")
        result = subprocess.run(
            "npm install",
            cwd=str(FRONTEND_DIR),
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"[Frontend] npm install failed: {result.stderr}")
            return
    
    # Step 4: Start backend
    start_backend()
    time.sleep(2)  # Let backend start
    
    # Step 5: Start frontend
    start_frontend()
    time.sleep(3)  # Let frontend start
    
    # Step 6: Setup ngrok
    setup_ngrok()
    
    # Keep running
    try:
        while True:
            time.sleep(1)
            # Check if processes are still running
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"[{name}] Process exited with code {proc.returncode}")
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    main()
