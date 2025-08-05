# Trade Journal Web Application

A comprehensive Django-based trading journal application that helps traders log, analyze, and improve their trading performance.

## Features

### 🔐 Authentication & User Management
- User registration and login
- Password reset via email
- User profile management with avatar upload
- Secure authentication system

### 📊 Trade Logging
- Comprehensive trade entry with all essential fields:
  - Date/Time, Asset, Trade Type (Buy/Sell)
  - Entry/Exit prices, Position size
  - Stop Loss, Take Profit levels
  - Tags for categorization
  - Screenshot uploads
  - Trading notes and emotions
- Automatic P&L calculation
- Risk:Reward ratio calculation

### 📈 Dashboard & Analytics
- Real-time trading statistics
- Win rate calculation
- Total profit/loss tracking
- Best and worst trade identification
- Monthly trading activity charts
- Interactive Chart.js visualizations

### 🔍 Trade Management
- Filterable and searchable trade history
- Pagination for large datasets
- Detailed trade view pages
- Edit and delete functionality
- Bulk operations support

### 📤 Export & Reporting
- CSV export with filtering options
- PDF export capability (planned)
- Customizable date ranges
- Tag-based filtering

## Tech Stack

- **Backend**: Django 4.2+, Python 3.x
- **Frontend**: Django Templates, Bootstrap 5
- **Database**: SQLite (development), PostgreSQL ready
- **Charts**: Chart.js
- **Forms**: django-crispy-forms
- **File Handling**: Pillow for image processing

## Installation & Setup

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd trade-journal
   pip install -r requirements.txt
   ```

2. **Environment Setup**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Database Setup**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Run Development Server**:
   ```bash
   python manage.py runserver
   ```

5. **Access the Application**:
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Project Structure

```
trade_journal/
├── trade_journal/          # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/                  # User management app
│   ├── models.py          # Custom user and profile models
│   ├── views.py           # Authentication views
│   ├── forms.py           # User forms
│   └── urls.py
├── trades/                 # Trade management app
│   ├── models.py          # Trade model
│   ├── views.py           # Trade CRUD and dashboard
│   ├── forms.py           # Trade forms
│   └── urls.py
├── templates/              # HTML templates
│   ├── base.html          # Base template
│   ├── index.html         # Home page
│   ├── users/             # User templates
│   └── trades/            # Trade templates
├── static/                 # Static files (CSS, JS, images)
├── media/                  # User uploads
└── requirements.txt
```

## Key Features Explained

### Trade Model
The Trade model captures comprehensive trading data:
- Financial data (prices, sizes, P&L)
- Risk management (stop loss, take profit)
- Metadata (tags, emotions, notes)
- File uploads (screenshots)
- Automatic calculations (profit/loss, risk:reward)

### Dashboard Analytics
- Real-time statistics calculation
- Chart.js integration for visualizations
- Monthly trade activity tracking
- Performance metrics (win rate, average R:R)

### Security Features
- Django's built-in authentication
- CSRF protection
- Secure file uploads
- User data isolation

## Customization

### Adding New Fields
1. Update the Trade model in `trades/models.py`
2. Create and run migrations
3. Update forms in `trades/forms.py`
4. Modify templates as needed

### Email Configuration
Configure email settings in `.env`:
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
```

### Database Configuration
For PostgreSQL production setup:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'trade_journal',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## API Endpoints

- `/` - Home page
- `/users/login/` - User login
- `/users/signup/` - User registration
- `/dashboard/` - Trading dashboard
- `/trades/list/` - Trade list with filters
- `/trades/add/` - Add new trade
- `/trades/<id>/` - Trade detail view
- `/trades/export/csv/` - CSV export

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please use the GitHub issue tracker or contact the development team.