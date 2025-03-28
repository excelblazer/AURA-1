# AURA-1 Deployment Guide

This guide provides instructions for deploying the AURA-1 Invoicing Automation System in various environments.

## Prerequisites

- Docker and Docker Compose
- Git
- Basic knowledge of terminal/command line
- Access to the server/environment where you want to deploy

## Local Development Setup

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up environment variables by creating a `.env` file (see ENV_SETUP.md for details)

6. Run the development server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables by creating a `.env` file (see ENV_SETUP.md for details)

4. Run the development server:
   ```bash
   npm start
   ```

## Docker Deployment

The easiest way to deploy AURA-1 is using Docker Compose, which will set up all the required services:

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd AURA-1
   ```

2. Create a `.env` file in the project root with the necessary environment variables:
   ```
   # Database
   DB_USER=postgres
   DB_PASSWORD=your_secure_password
   DB_NAME=locoe_gain
   
   # Security
   SECRET_KEY=your_secure_secret_key
   
   # Frontend
   REACT_APP_API_URL=http://localhost:8000/api
   ```

3. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

4. The application will be available at:
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

5. To stop the application:
   ```bash
   docker-compose down
   ```

## Production Deployment

For production environments, additional steps are recommended:

### Security Enhancements

1. Use strong, unique passwords and secret keys
2. Set up HTTPS with Let's Encrypt or another SSL provider
3. Configure proper firewall rules
4. Use a reverse proxy like Nginx or Traefik

### Example Nginx Configuration for HTTPS

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;
    
    # SSL configurations
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Cloud Deployment Options

#### AWS Deployment

1. Set up an EC2 instance or ECS cluster
2. Use RDS for the PostgreSQL database
3. Configure an Application Load Balancer
4. Set up CloudWatch for monitoring

#### Azure Deployment

1. Use Azure App Service for the application
2. Set up Azure Database for PostgreSQL
3. Configure Azure Application Gateway
4. Set up Azure Monitor for monitoring

#### Google Cloud Platform

1. Use Google Compute Engine or Google Kubernetes Engine
2. Set up Cloud SQL for PostgreSQL
3. Configure Cloud Load Balancing
4. Set up Cloud Monitoring

## Database Migrations

The application uses SQLAlchemy for database models. If you need to make changes to the database schema:

1. Create a migration script using Alembic:
   ```bash
   cd backend
   alembic revision --autogenerate -m "Description of changes"
   ```

2. Apply the migration:
   ```bash
   alembic upgrade head
   ```

## Backup and Restore

### Database Backup

```bash
docker exec -t aura1-db pg_dump -U postgres locoe_gain > backup_$(date +%Y-%m-%d_%H-%M-%S).sql
```

### Database Restore

```bash
cat backup_file.sql | docker exec -i aura1-db psql -U postgres -d locoe_gain
```

### File Backup

```bash
# Backup uploads and output directories
docker cp aura1-backend:/app/uploads ./backup/uploads
docker cp aura1-backend:/app/output ./backup/output
```

## Monitoring and Maintenance

- Set up health checks to monitor the application
- Regularly update dependencies
- Monitor disk space, especially for upload and output directories
- Set up log rotation
- Schedule regular backups

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Check if the database container is running
   - Verify database credentials in the `.env` file
   - Check network connectivity between services

2. **File Upload Issues**
   - Ensure the upload directory has proper permissions
   - Check disk space
   - Verify file size limits in the configuration

3. **OCR Processing Issues**
   - Ensure Tesseract is properly installed
   - Check if the uploaded PDFs are readable
   - Verify that the necessary language packs are installed

4. **Frontend Connection Issues**
   - Check if the backend API URL is correctly set
   - Verify CORS settings
   - Check browser console for errors

For additional help, please refer to the project documentation or contact the development team.
