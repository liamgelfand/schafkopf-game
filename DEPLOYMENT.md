# Deployment Guide

## Quick Start with Docker Compose

1. **Copy environment file:**
```bash
cp .env.example .env
```

2. **Edit `.env` file** with your production settings:
   - Change `SECRET_KEY` to a strong random key
   - Update `POSTGRES_PASSWORD` to a secure password
   - Set `CORS_ORIGINS` to your frontend domain

3. **Start all services:**
```bash
docker-compose up -d
```

4. **Check logs:**
```bash
docker-compose logs -f
```

## Services

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Database**: PostgreSQL on port 5432

## Production Deployment

### Environment Variables

Set these in your production environment:

```bash
# Required
SECRET_KEY=<strong-random-key>
POSTGRES_PASSWORD=<secure-password>
CORS_ORIGINS=https://yourdomain.com

# Optional
POSTGRES_USER=schafkopf
POSTGRES_DB=schafkopf
BACKEND_PORT=8000
FRONTEND_PORT=3000
```

### Database Migrations

For production, use Alembic for migrations:

```bash
cd backend
alembic upgrade head
```

### Building for Production

```bash
# Build images
docker-compose build

# Run in production mode (no hot reload)
docker-compose -f docker-compose.prod.yml up -d
```

## Development

For development with hot reload:

```bash
docker-compose up
```

The backend will reload on code changes, and frontend can be run separately with `npm run dev` for faster iteration.

## Database Backup

```bash
# Backup
docker-compose exec db pg_dump -U schafkopf schafkopf > backup.sql

# Restore
docker-compose exec -T db psql -U schafkopf schafkopf < backup.sql
```

## Troubleshooting

1. **Database connection issues**: Ensure the database container is healthy before starting backend
2. **CORS errors**: Check `CORS_ORIGINS` environment variable
3. **Port conflicts**: Change ports in `.env` file


