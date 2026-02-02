# TIPU - University Contract Management System

A comprehensive dashboard system for managing student contracts, installment payments, and enrollment processes at private universities.

## 📋 Overview

TIPU is an all-in-one university management platform that automates contract generation, payment scheduling, and student profile management, making administrative tasks more efficient and transparent.

## ✨ Features

- **Automated Contract Generation**: Generate enrollment contracts with customizable terms
- **Flexible Installment Plans**: Create and modify payment schedules based on student needs
- **SMS Notifications**: Automated payment reminders sent via SMS
- **Student Portal**: Secure access for students to view contracts and payment history
- **Payment Tracking**: Monitor all transactions and outstanding balances
- **Excel Integration**: Import/export student and payment data
- **Admin Dashboard**: Comprehensive control panel for university administrators
- **Profile Management**: Students can manage their personal information

## 🛠️ Tech Stack

- **Backend**: Python 3.x, Django, Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **SMS Service**: Integrated SMS gateway for notifications
- **Containerization**: Docker, Docker Compose
- **File Processing**: Excel file handling for bulk operations

## 📦 Installation

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- PostgreSQL
- SMS service provider credentials

### Setup

1. Clone the repository
```bash
git clone https://github.com/TulqinUrinov/TIPU.git
cd TIPU
```

2. Create environment file
```bash
cp env_example .env
```

3. Configure your environment variables in `.env`:
```
SECRET_KEY=your_secret_key
DEBUG=False
DATABASE_URL=postgresql://user:password@db:5432/tipu
SMS_API_KEY=your_sms_api_key
SMS_API_URL=your_sms_provider_url
```

4. Build and run with Docker
```bash
docker-compose up --build
```

5. Run migrations
```bash
docker-compose exec web python manage.py migrate
```

6. Create superuser
```bash
docker-compose exec web python manage.py createsuperuser
```

7. Load initial data (optional)
```bash
docker-compose exec web python manage.py loaddata initial_data
```

## 🚀 Usage

Access the application:
- **API**: http://localhost:8000/
- **Admin Dashboard**: http://localhost:8000/admin/
- **Student Portal**: http://localhost:8000/student/

## 📁 Project Structure

```
TIPU/
├── config/          # Django settings and configuration
├── data/            # Models and database schemas
├── sms/             # SMS notification service
├── tg_bot/          # Telegram bot integration (optional)
├── manage.py        # Django management script
├── r.txt            # Requirements file
└── docker-compose.yml
```
## 📊 Features in Detail

### Contract Generation
- Customizable contract templates
- Automatic field population from student data
- Digital signature support
- PDF export functionality

### Payment Management
- Flexible installment creation (monthly, quarterly, custom)
- Payment deadline tracking
- Payment history and receipts

### SMS Notifications
- Automated reminders 3 days before payment deadline
- Payment confirmation messages
- Custom notification templates
- 
## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Tulqin Urinov**
- GitHub: [@TulqinUrinov](https://github.com/TulqinUrinov)

