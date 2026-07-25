# # Deployment Guide - AI Research & Knowledge Assistant

This guide covers all step-by-step methods to deploy the **AI Research & Knowledge Assistant** into production environments.

---

## 🚀 Option 1: Docker & Docker Compose Deployment (Recommended)

### 1. Build and Run Container with Docker Compose
Ensure Docker Desktop or Docker Engine is installed, then run:

```bash
# 1. Clone repository
git clone https://github.com/your-username/ai-research-assistant.git
cd "ai-research-assistant"

# 2. Configure environment variables
cp .env.example .env
# Edit .env and set OPENAI_API_KEY (optional for basic embeddings/summaries)

# 3. Build & start application in background
docker compose up -d --build
```

### 4. Verify Docker Container
```bash
# Check container logs
docker compose logs -f

# App available at: http://localhost:8000
```

---

## ☁️ Option 2: Cloud Deployment (Render / AWS App Runner / DigitalOcean App Platform)

### Render.com Deployment Steps
1. Push your repository to GitHub.
2. Log into [Render.com](https://render.com) and click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Select **Environment**: `Docker` or `Python 3`.
5. If using Python runtime:
   - **Build Command**: `pip install -r requirements.txt && python -m src.ml.train_classifier`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add Environment Variable:
   - `OPENAI_API_KEY`: `your_openai_key`
7. Click **Create Web Service**.

---

## 🖥️ Option 3: Traditional Linux VM Deployment (Ubuntu / AWS EC2 / GCP Compute)

### 1. System Dependencies & Virtual Environment
```bash
# Update Ubuntu packages
sudo apt update && sudo apt install -y python3-pip python3-venv git

# Clone repository
git clone https://github.com/your-username/ai-research-assistant.git
cd "ai-research-assistant"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements & train classifier model
pip install -r requirements.txt
python -m src.ml.train_classifier
```

### 2. Configure Systemd Service (Process Manager)
Create a systemd unit file to run the app reliably in the background:

```bash
sudo nano /etc/systemd/system/ai-assistant.service
```

Paste the following configuration (adjust path to match your user path):
```ini
[Unit]
Description=AI Research & Knowledge Assistant Service
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-research-assistant
ExecStart=/home/ubuntu/ai-research-assistant/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl start ai-assistant
sudo systemctl enable ai-assistant
```

---

## 🛡️ Option 4: Production Nginx Reverse Proxy Setup (HTTPS / Domain)

To bind a custom domain with SSL certificates (Let's Encrypt), set up Nginx:

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

Configure Nginx site (`/etc/nginx/sites-available/ai-assistant`):
```nginx
server {
    server_name research.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable Nginx config & install SSL certificate:
```bash
sudo ln -s /etc/nginx/sites-available/ai-assistant /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Install free SSL certificate
sudo certbot --nginx -d research.yourdomain.com
```

---

## 📋 Summary of Key Commands

| Task | Command |
| --- | --- |
| **Local Dev** | `python main.py` or `uvicorn main:app --reload` |
| **Run Pytest** | `python -m pytest tests/test_assistant.py` |
| **Train ML Model** | `python -m src.ml.train_classifier` |
| **Docker Build** | `docker build -t ai-assistant .` |
| **Docker Compose Up** | `docker compose up -d` |
| **Docker Logs** | `docker compose logs -f` |
