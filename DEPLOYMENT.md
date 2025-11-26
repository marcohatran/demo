# 🚀 Production Deployment Guide

Hướng dẫn deploy hệ thống Media Monitoring lên server production.

## Yêu cầu Server

### Hardware Minimum:
- **CPU**: 4 cores
- **RAM**: 8GB (16GB recommended)
- **Storage**: 50GB SSD
- **Network**: 100Mbps+

### Software:
- Ubuntu 22.04 LTS (hoặc CentOS 8+)
- Docker 24+
- Docker Compose 2.20+
- Nginx (reverse proxy)

## Các bước Deploy

### 1. Chuẩn bị Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
```

### 2. Clone Code

```bash
git clone <your-repo-url>
cd demo-app

# Tạo .env file
cp backend/.env.example backend/.env
nano backend/.env  # Điền GEMINI_API_KEY
```

### 3. Production Docker Compose

Tạo file `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    restart: always
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=CHANGE_THIS_PASSWORD
      - POSTGRES_DB=mediamonitor
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

  backend:
    build: ./backend
    restart: always
    env_file:
      - ./backend/.env
    environment:
      - DATABASE_URL=postgresql://user:CHANGE_THIS_PASSWORD@db:5432/mediamonitor
    depends_on:
      - db
    networks:
      - app-network

  frontend:
    build: ./frontend
    restart: always
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
```

### 4. Nginx Configuration

Tạo `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:5173;
    }

    server {
        listen 80;
        server_name your-domain.com;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }

        # Backend API
        location /api/ {
            proxy_pass http://backend/;
            proxy_http_version 1.1;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket
        location /ws/ {
            proxy_pass http://backend/ws/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
        }
    }
}
```

### 5. Start Production

```bash
# Build và start
docker-compose -f docker-compose.prod.yml up --build -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Check status
docker-compose -f docker-compose.prod.yml ps
```

### 6. SSL Certificate (Optional)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com
```

### 7. Monitoring & Maintenance

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f backend

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Update code
git pull
docker-compose -f docker-compose.prod.yml up --build -d

# Backup database
docker exec demo-app-db-1 pg_dump -U user mediamonitor > backup.sql
```

## Security Best Practices

1. **Change Default Passwords** trong docker-compose.prod.yml
2. **Firewall**: Chỉ mở port 80, 443
3. **Environment Variables**: Không commit .env vào git
4. **SSL**: Bắt buộc HTTPS cho production
5. **Database**: Backup hàng ngày

## Performance Tuning

### PostgreSQL:
```sql
-- Tăng connection pool
max_connections = 200
shared_buffers = 2GB
```

### Backend:
```python
# main.py - Tăng số workers
uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=4)
```

## Monitoring

Dùng Prometheus + Grafana:

```yaml
# docker-compose.prod.yml - thêm
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

## Troubleshooting

### Backend không start:
```bash
docker logs demo-app-backend-1
# Check GEMINI_API_KEY
```

### Database connection failed:
```bash
docker exec demo-app-db-1 psql -U user -d mediamonitor
```

### High CPU usage:
- Giảm frame rate trong stream_processor.py
- Tăng interval phân tích (từ 15s lên 30s)

---

**Contact**: Nếu cần hỗ trợ deploy, hãy cung cấp:
- OS và specs server
- Domain name
- Yêu cầu đặc biệt (VPN, firewall, etc.)
