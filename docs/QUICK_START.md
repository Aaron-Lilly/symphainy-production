# Quick Start Guide

## Start the Platform

```bash
cd /home/founders/demoversion/symphainy_source
docker-compose up -d
```

## Verify It's Running

```bash
# Check status
docker-compose ps

# Test health endpoint
curl http://localhost/api/health
```

## Access the Platform

- **Frontend**: http://localhost
- **API Docs**: http://localhost/api/docs
- **Traefik Dashboard**: http://localhost:8080
- **Consul UI**: http://localhost:8500
- **Grafana**: http://localhost:3100

## Stop the Platform

```bash
docker-compose down
```

## View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

## Common Issues

**Port conflicts?** Check what's using ports:
```bash
lsof -i :80
lsof -i :8500
```

**Backend not starting?** Check logs:
```bash
docker logs symphainy-backend-prod
```

**Need more help?** See [PLATFORM_STARTUP_GUIDE.md](./PLATFORM_STARTUP_GUIDE.md) for detailed documentation.








