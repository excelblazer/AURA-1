# AURA-1 Environment Configuration Guide

This document provides instructions for setting up environment variables for the AURA-1 Invoicing Automation System. Proper configuration of these variables is essential for the application to function correctly in different deployment environments.

## Backend Environment Variables

The backend requires several environment variables for database connection, security, server configuration, and more. These variables should be defined in a `.env` file located in the root of the backend directory.

### Required Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost/locoe_gain` | `postgresql://user:password@host:port/dbname` |
| `SECRET_KEY` | Key used for JWT token encryption | - | `your_secret_key_here` |
| `PORT` | Server port number | `8000` | `8000` |

### Optional Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `DB_HOST` | Database host (alternative to DATABASE_URL) | `localhost` | `db.example.com` |
| `DB_PORT` | Database port (alternative to DATABASE_URL) | `5432` | `5432` |
| `DB_USER` | Database username (alternative to DATABASE_URL) | `postgres` | `dbuser` |
| `DB_PASSWORD` | Database password (alternative to DATABASE_URL) | `postgres` | `password123` |
| `DB_NAME` | Database name (alternative to DATABASE_URL) | `locoe_gain` | `aura1_db` |
| `ALGORITHM` | JWT algorithm | `HS256` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration time in minutes | `30` | `60` |
| `HOST` | Server host | `0.0.0.0` | `0.0.0.0` |
| `DEBUG` | Debug mode flag | `False` | `True` |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | `http://localhost:3000` | `http://localhost:3000,https://yourdomain.com` |
| `UPLOAD_DIR` | Directory for uploaded files | `uploads` | `data/uploads` |
| `OUTPUT_DIR` | Directory for generated documents | `output` | `data/output` |
| `LOG_LEVEL` | Logging level | `INFO` | `DEBUG` |
| `LOG_FILE` | Log file path | `app.log` | `logs/app.log` |
| `OCR_ENGINE` | OCR engine to use | `tesseract` | `tesseract` |

## Frontend Environment Variables

The frontend requires environment variables for API configuration, authentication, and UI customization. These variables should be defined in a `.env` file located in the root of the frontend directory.

### Required Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `REACT_APP_API_URL` | Backend API URL | `http://localhost:8000/api` | `https://api.example.com/api` |

### Optional Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `REACT_APP_TOKEN_STORAGE_KEY` | Local storage key for JWT token | `token` | `auth_token` |
| `REACT_APP_TITLE` | Application title | `AURA-1 Invoicing Automation` | `Client1 Invoice System` |
| `REACT_APP_VERSION` | Application version | `1.0.0` | `1.2.3` |
| `REACT_APP_ENABLE_TEMPLATE_CUSTOMIZATION` | Enable template customization feature | `true` | `false` |
| `REACT_APP_ENABLE_DATA_VISUALIZATION` | Enable data visualization feature | `true` | `false` |
| `REACT_APP_MAX_FILE_SIZE` | Maximum file size in bytes | `10485760` (10MB) | `20971520` (20MB) |
| `REACT_APP_ALLOWED_FILE_TYPES` | Allowed file types (comma-separated) | `application/pdf,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | `application/pdf` |
| `REACT_APP_THEME_PRIMARY_COLOR` | Primary theme color | `#1976d2` | `#00796b` |
| `REACT_APP_THEME_SECONDARY_COLOR` | Secondary theme color | `#dc004e` | `#ff9800` |

## Setup Instructions

### Development Environment

1. Create a `.env` file in the backend directory:
   ```bash
   cp backend/.env.example backend/.env
   ```

2. Create a `.env` file in the frontend directory:
   ```bash
   cp frontend/.env.example frontend/.env
   ```

3. Edit both files to set the appropriate values for your development environment.

### Production Environment

For production deployment, you should set these environment variables securely according to your hosting platform's recommendations:

#### Docker Deployment

If using Docker, you can pass environment variables in your `docker-compose.yml` file:

```yaml
version: '3'
services:
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/aura1
      - SECRET_KEY=your_production_secret_key
      - PORT=8000
      # Add other variables as needed
    ports:
      - "8000:8000"
    depends_on:
      - db

  frontend:
    build: ./frontend
    environment:
      - REACT_APP_API_URL=https://api.yourdomain.com/api
      # Add other variables as needed
    ports:
      - "80:80"
    depends_on:
      - backend

  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=aura1
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### Cloud Deployment

For cloud platforms (AWS, Azure, GCP, etc.), use their respective secret management services:

- AWS: AWS Secrets Manager or Parameter Store
- Azure: Azure Key Vault
- GCP: Secret Manager

## Troubleshooting

If you encounter issues related to environment variables:

1. Verify that all required variables are set correctly
2. Check for typos in variable names
3. Ensure that the `.env` files are in the correct locations
4. For the frontend, remember that all environment variables must start with `REACT_APP_`
5. After changing environment variables in the frontend, you need to restart the development server

## Security Considerations

- Never commit `.env` files to version control
- Use strong, unique values for `SECRET_KEY`
- In production, use a secure method to manage secrets
- Regularly rotate sensitive credentials
- Limit access to environment variables to authorized personnel only
