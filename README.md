# AURA-1: Invoicing Automation System for Client1

AURA-1 is a comprehensive automation solution for Client1's invoicing process, designed to streamline the workflow from data collection to document generation and delivery.

## Overview

This application automates the invoicing process for Client1 by:

1. Processing payroll details and daily feedback sheets using OCR technology
2. Validating data according to business rules
3. Generating required documents (Attendance Records, Progress Reports, Invoices, Service Logs)
4. Converting documents to PDF format
5. Providing a user-friendly interface with data visualization for the entire workflow
6. Offering robust testing frameworks for both frontend and backend components

## System Architecture

The application follows a modern client-server architecture:

### Frontend Architecture

The frontend is built with React.js and follows a component-based architecture:

- **React.js**: Frontend library for building user interfaces
- **React Router**: For navigation and routing
- **Material-UI**: Component library for consistent design
- **Axios**: HTTP client for API requests
- **Formik & Yup**: Form handling and validation
- **JWT**: Authentication handling
- **Recharts**: Data visualization library for processing statistics

#### Frontend Structure

```
frontend/
├── public/                  # Public assets
├── src/                     # Source code
│   ├── components/          # Reusable UI components
│   │   ├── Layout/          # Layout components
│   │   └── Dashboard/       # Dashboard components including ProcessingStats
│   ├── context/             # React context providers
│   ├── pages/               # Page components
│   │   ├── Auth/            # Authentication pages
│   │   ├── Dashboard/       # Dashboard page
│   │   ├── Documents/       # Document management
│   │   ├── FileUpload/      # File upload page
│   │   ├── NotFound/        # 404 page
│   │   ├── Templates/       # Template management
│   │   └── Validation/      # Validation page
│   ├── services/            # API services
│   ├── utils/               # Utility functions
│   ├── App.js               # Main App component
│   ├── index.js             # Entry point
│   ├── index.css            # Global styles
│   └── theme.js             # Material-UI theme
└── package.json             # Dependencies and scripts
```

#### Authentication Flow

1. User logs in with username and password
2. Backend validates credentials and returns a JWT token
3. Token is stored in localStorage
4. Token is included in subsequent API requests
5. Protected routes check for valid token

### Backend Architecture

The backend is built with Python FastAPI and follows a modular architecture:

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: ORM for database interactions
- **Pydantic**: Data validation and settings management
- **JWT**: Authentication and authorization
- **Pytest**: Testing framework

#### Backend Structure

```
backend/
├── main.py                  # Entry point
├── auth/                    # Authentication
│   ├── __init__.py
│   └── security.py          # JWT and password security
├── database/                # Database models and connections
│   ├── __init__.py
│   ├── models.py            # SQLAlchemy models
│   ├── database.py          # DB connection
│   └── crud.py              # Database operations
├── routers/                 # API routes
│   ├── __init__.py
│   ├── auth.py              # Authentication endpoints
│   ├── files.py             # File upload/download endpoints
│   ├── validation.py        # Validation endpoints
│   ├── templates.py         # Template management endpoints
│   ├── processing.py        # Document generation endpoints
│   └── ocr.py               # OCR processing endpoints
├── schemas/                 # Pydantic models
│   ├── __init__.py
│   ├── file.py              # File schema
│   ├── job.py               # Processing job schema
│   ├── template.py          # Template schema
│   ├── user.py              # User schema
│   └── validation.py        # Validation schema
├── services/                # Business logic
│   ├── file_processor.py    # Extract data from files
│   ├── validator.py         # Validation rules
│   ├── ar_generator.py      # Attendance record generator
│   ├── pr_generator.py      # Progress report generator
│   ├── invoice_generator.py # Invoice generator
│   ├── service_log.py       # Agency service log generator
│   ├── document_generator.py # Document generation orchestrator
│   └── ocr_service.py       # OCR text and data extraction
└── tests/                   # Testing framework
    ├── conftest.py          # Test configuration and fixtures
    ├── test_auth.py         # Authentication tests
    ├── test_files.py        # File upload/processing tests
    └── test_ocr_service.py  # OCR service tests
```

## Features

### File Management
- Upload and process Payroll Detail Sheets (PDF) and Daily Feedback Sheets (Excel)
- Extract and parse data from uploaded files using OCR technology
- Store processed data for further validation and document generation

### OCR Processing
- Extract text from PDF documents
- Parse structured data from payroll information
- Extract tabular data from documents
- Process multiple document types with high accuracy

### Data Validation
- Validate contract periods for students and tutors
- Verify working hours (10am to 7pm)
- Cross-check hours between payroll and feedback sheets
- Track and validate no-shows (max 2 per student per month)
- Enforce maximum 4 tutoring hours per week per student
- Round time entries to nearest 0.25 hour

### Document Generation
- Generate Attendance Records (ARs) for each student monthly
- Create Progress Reports (PRs) for each student monthly
- Produce invoices in the required format
- Prepare Agency Service Logs
- Convert documents to PDF format

### Data Visualization
- Real-time processing statistics dashboard
- Visual representation of job status and progress
- Interactive charts for monitoring system performance
- Metrics for active jobs, completed jobs, and processing stages

### Template Management
- Create and edit document templates
- Preview templates with sample data
- Manage different document types and formats

### User Management
- User registration and authentication
- Role-based access control
- Secure password handling

## Project Structure

```
AURA-1/
│
├── backend/                     # FastAPI backend
│   ├── main.py                  # Entry point
│   ├── auth/                    # Authentication
│   │   ├── __init__.py
│   │   └── security.py          # JWT and password security
│   ├── database/                # Database models and connections
│   │   ├── __init__.py
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── database.py          # DB connection
│   │   └── crud.py              # Database operations
│   ├── routers/                 # API routes
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── files.py             # File upload/download endpoints
│   │   ├── validation.py        # Validation endpoints
│   │   ├── templates.py         # Template management endpoints
│   │   ├── processing.py        # Document generation endpoints
│   │   └── ocr.py               # OCR processing endpoints
│   ├── schemas/                 # Pydantic models
│   │   ├── __init__.py
│   │   ├── file.py              # File schema
│   │   ├── job.py               # Processing job schema
│   │   ├── template.py          # Template schema
│   │   ├── user.py              # User schema
│   │   └── validation.py        # Validation schema
│   ├── services/                # Business logic
│   │   ├── file_processor.py    # Extract data from files
│   │   ├── validator.py         # Validation rules
│   │   ├── ar_generator.py      # Attendance record generator
│   │   ├── pr_generator.py      # Progress report generator
│   │   ├── invoice_generator.py # Invoice generator
│   │   ├── service_log.py       # Agency service log generator
│   │   ├── document_generator.py # Document generation orchestrator
│   │   └── ocr_service.py       # OCR text and data extraction
│   └── tests/                   # Testing framework
│       ├── conftest.py          # Test configuration and fixtures
│       ├── test_auth.py         # Authentication tests
│       ├── test_files.py        # File upload/processing tests
│       └── test_ocr_service.py  # OCR service tests
│
└── frontend/                    # React frontend
    ├── public/                  # Static files
    │   ├── index.html           # HTML entry point
    │   └── manifest.json        # Web app manifest
    ├── src/                     # Source code
    │   ├── components/          # Reusable UI components
    │   │   ├── Layout/          # Layout components
    │   │   │   └── Layout.js    # Main layout component
    │   │   └── Dashboard/       # Dashboard components
    │   │       └── ProcessingStats.js # Processing statistics visualization
    │   ├── context/             # React context providers
    │   │   └── AuthContext.js   # Authentication context
    │   ├── pages/               # Page components
    │   │   ├── Auth/            # Authentication pages
    │   │   │   ├── Login.js     # Login page
    │   │   │   └── Register.js  # Registration page
    │   │   ├── Dashboard/       # Dashboard
    │   │   │   └── Dashboard.js # Main dashboard
    │   │   ├── Documents/       # Document management
    │   │   │   └── Documents.js # Documents page
    │   │   ├── FileUpload/      # File upload
    │   │   │   └── FileUpload.js # File upload page
    │   │   ├── NotFound/        # 404 page
    │   │   │   └── NotFound.js  # Not found page
    │   │   ├── Templates/       # Template management
    │   │   │   ├── Templates.js # Templates list
    │   │   │   └── TemplateEditor.js # Template editor
    │   │   └── Validation/      # Validation
    │   │       └── Validation.js # Validation page
    │   ├── services/            # API services
    │   │   └── api.js           # API client
    │   ├── utils/               # Utility functions
    │   │   ├── formatters.js    # Data formatting utilities
    │   │   └── validators.js    # Form validation utilities
    │   ├── App.js               # Main App component
    │   ├── index.js             # Entry point
    │   ├── index.css            # Global styles
    │   └── theme.js             # Material-UI theme
    ├── package.json             # Dependencies and scripts
    └── README.md                # Frontend documentation
```

## Getting Started

### Prerequisites

- Python 3.8+ for the backend
- Node.js (v14 or higher) for the frontend
- PostgreSQL database
- npm or yarn for frontend package management

### Installation

#### Backend Setup

1. Clone the repository
2. Navigate to the backend directory:
   ```
   cd AURA-1/backend
   ```
3. Create a virtual environment:
   ```
   python -m venv venv
   ```
4. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
5. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
6. Set up environment variables:
   ```
   # Create a .env file with the following variables
   DATABASE_URL=postgresql://user:password@localhost/aura1
   SECRET_KEY=your_secret_key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

#### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd AURA-1/frontend
   ```
2. Install dependencies:
   ```
   npm install
   ```
   or
   ```
   yarn install
   ```

### Running the Application

#### Start the Backend

```
cd AURA-1/backend
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

#### Start the Frontend

```
cd AURA-1/frontend
npm start
```

The application will be available at `http://localhost:3000` and will proxy API requests to the backend.

### Building for Production

#### Backend

The backend can be deployed using any ASGI server like Uvicorn or Gunicorn:

```
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

#### Frontend

Build the frontend application:

```
cd AURA-1/frontend
npm run build
```

This will create a `build` directory with optimized production files that can be served by any static file server.

## Setup Instructions

### Prerequisites
- Python 3.8+ for backend
- Node.js 14+ for frontend
- PostgreSQL database

### Backend Setup
1. Navigate to the backend directory:
   ```
   cd AURA-1/backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Set up environment variables:
   - Create a `.env` file with the following variables:
     ```
     DATABASE_URL=postgresql://user:password@localhost/aura1
     SECRET_KEY=your_secret_key
     ALGORITHM=HS256
     ACCESS_TOKEN_EXPIRE_MINUTES=30
     ```

6. Run database migrations:
   ```
   alembic upgrade head
   ```

7. Start the backend server:
   ```
   uvicorn main:app --reload
   ```

8. Run tests:
   ```
   pytest
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```
   cd AURA-1/frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

4. Run tests:
   ```
   npm run test
   ```

5. Generate test coverage report:
   ```
   npm run test:coverage
   ```

## Workflow

1. **File Upload**:
   - Upload Payroll Detail Sheet (PDF) and Daily Feedback Sheet (Excel)
   - System extracts and processes data using OCR technology

2. **Data Validation**:
   - System validates extracted data against business rules
   - Validation issues are highlighted for user review
   - Users can resolve validation issues manually

3. **Document Generation**:
   - System generates required documents based on validated data
   - Documents are converted to PDF format
   - Users can preview generated documents

4. **Document Delivery**:
   - Generated documents can be downloaded or sent via email
   - System maintains a record of all generated documents

## Cloud Deployment Instructions

### AWS Deployment

#### Prerequisites
- AWS account with appropriate permissions
- AWS CLI installed and configured
- Docker installed (optional for containerized deployment)

#### EC2 Deployment
1. Launch an EC2 instance:
   - Choose Amazon Linux 2 or Ubuntu Server
   - Select an instance type (t2.medium or higher recommended)
   - Configure security groups to allow HTTP (80), HTTPS (443), and SSH (22)
   - Create and download key pair for SSH access

2. Connect to your instance:
   ```
   ssh -i your-key.pem ec2-user@your-instance-public-dns
   ```

3. Update system packages:
   ```
   sudo yum update -y   # Amazon Linux
   # OR
   sudo apt update && sudo apt upgrade -y   # Ubuntu
   ```

4. Install required dependencies:
   ```
   # Amazon Linux
   sudo amazon-linux-extras install python3 postgresql nginx
   sudo yum install git -y
   
   # Ubuntu
   sudo apt install python3 python3-pip python3-venv postgresql nginx git -y
   ```

5. Clone the repository:
   ```
   git clone https://your-repository-url/AURA-1.git
   cd AURA-1
   ```

6. Set up and configure the application following the setup instructions above.

7. Configure Nginx as a reverse proxy:
   ```
   sudo nano /etc/nginx/sites-available/aura1
   ```
   
   Add the following configuration:
   ```
   server {
       listen 80;
       server_name your-domain.com;
       
       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location / {
           proxy_pass http://localhost:3000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

8. Enable the site and restart Nginx:
   ```
   sudo ln -s /etc/nginx/sites-available/aura1 /etc/nginx/sites-enabled/
   sudo systemctl restart nginx
   ```

9. Set up SSL with Let's Encrypt (optional but recommended):
   ```
   sudo apt install certbot python3-certbot-nginx -y
   sudo certbot --nginx -d your-domain.com
   ```

#### Using AWS RDS for Database
1. Create a PostgreSQL RDS instance in the AWS console
2. Configure security groups to allow connections from your EC2 instance
3. Update your application's `.env` file with the RDS connection string

#### Using AWS S3 for File Storage
1. Create an S3 bucket for file storage
2. Configure IAM roles and permissions
3. Update your application to use S3 for file storage instead of local storage

### GCP Deployment

#### Prerequisites
- Google Cloud Platform account
- gcloud CLI installed and configured

#### Compute Engine Deployment
1. Create a Compute Engine VM instance:
   ```
   gcloud compute instances create aura1-instance \
     --machine-type=e2-medium \
     --image-family=ubuntu-2004-lts \
     --image-project=ubuntu-os-cloud \
     --boot-disk-size=20GB \
     --tags=http-server,https-server
   ```

2. Connect to your instance:
   ```
   gcloud compute ssh aura1-instance
   ```

3. Update system packages:
   ```
   sudo apt update && sudo apt upgrade -y
   ```

4. Install required dependencies:
   ```
   sudo apt install python3 python3-pip python3-venv postgresql nginx git -y
   ```

5. Clone the repository:
   ```
   git clone https://your-repository-url/AURA-1.git
   cd AURA-1
   ```

6. Set up and configure the application following the setup instructions above.

7. Configure Nginx as a reverse proxy (similar to AWS instructions)

8. Set up SSL with Let's Encrypt (optional but recommended)

#### Using Cloud SQL for Database
1. Create a PostgreSQL Cloud SQL instance:
   ```
   gcloud sql instances create aura1-db \
     --database-version=POSTGRES_13 \
     --tier=db-g1-small \
     --region=us-central1
   ```

2. Create a database and user:
   ```
   gcloud sql databases create aura1 --instance=aura1-db
   gcloud sql users create aura1-user --instance=aura1-db --password=your-password
   ```

3. Update your application's `.env` file with the Cloud SQL connection string

#### Using Cloud Storage for File Storage
1. Create a Cloud Storage bucket:
   ```
   gsutil mb gs://aura1-storage
   ```

2. Configure IAM permissions
3. Update your application to use Cloud Storage for file storage

## Docker Deployment (Optional)

For containerized deployment, you can use Docker and Docker Compose:

1. Create a `Dockerfile` for the backend:
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY backend/requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY backend/ .
   
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. Create a `Dockerfile` for the frontend:
   ```dockerfile
   FROM node:14-alpine as build
   
   WORKDIR /app
   
   COPY frontend/package*.json ./
   RUN npm install
   
   COPY frontend/ .
   RUN npm run build
   
   FROM nginx:alpine
   COPY --from=build /app/build /usr/share/nginx/html
   COPY nginx.conf /etc/nginx/conf.d/default.conf
   
   EXPOSE 80
   
   CMD ["nginx", "-g", "daemon off;"]
   ```

3. Create a `docker-compose.yml` file:
   ```yaml
   version: '3'
   
   services:
     backend:
       build:
         context: .
         dockerfile: backend.Dockerfile
       ports:
         - "8000:8000"
       environment:
         - DATABASE_URL=postgresql://postgres:postgres@db:5432/aura1
         - SECRET_KEY=your_secret_key
         - ALGORITHM=HS256
         - ACCESS_TOKEN_EXPIRE_MINUTES=30
       depends_on:
         - db
   
     frontend:
       build:
         context: .
         dockerfile: frontend.Dockerfile
       ports:
         - "80:80"
       depends_on:
         - backend
   
     db:
       image: postgres:13
       environment:
         - POSTGRES_USER=postgres
         - POSTGRES_PASSWORD=postgres
         - POSTGRES_DB=aura1
       volumes:
         - postgres_data:/var/lib/postgresql/data
   
   volumes:
     postgres_data:
   ```

4. Build and run the containers:
   ```
   docker-compose up -d
   ```

## Maintenance and Monitoring

### Logging
- Application logs are stored in the `logs` directory
- Use a centralized logging service like AWS CloudWatch or GCP Cloud Logging for production

### Monitoring
- Set up health check endpoints to monitor application status
- Use AWS CloudWatch or GCP Cloud Monitoring for production monitoring
- Configure alerts for critical errors and performance issues

### Backup
- Regular database backups are essential
- For AWS, use RDS automated backups
- For GCP, use Cloud SQL automated backups
- Store file backups in a separate storage location

## License

This project is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.
