# Local Development Setup Guide

This guide will help you set up the Vet Insight project for local development.

## 🔧 Required Modifications for Local Development

Since this project was built for production deployment, you'll need to make several changes to run it locally.

### 1. Database Configuration

**In your main app file (server.py):**

```python
# REMOVE this line:
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SUPABASE_CONNECTION_STRING')

# REPLACE with:
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
```

### 2. Error Handlers

Comment out any production error handlers that might interfere with development debugging.

### 3. Email Templates Fix (Windows Users)

**In `email_templates.py`:**

Comment out any `zoneinfo` imports and calls:

```python
# created_at_local = booking.created_at.astimezone(ZoneInfo("Asia/Karachi"))
# formatted_created_date = created_at_local.strftime("%B %d, %Y at %I:%M %p")
```

### 4. Sitemap Blueprint

**In your main app file:**

Comment out the sitemap blueprint registration since it has hardcoded domain references:

```python
# app.register_blueprint(sitemap_bp)  # Comment this out for local dev
```

## 🗄️ Database Initialization

Create a `db_init.py` file to set up your local admin user:

```python
from flask import Flask

from db_models import (

    db,

    Admins,

)
from utils import set_password
import os

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(

    "DATABASE_URL", "sqlite:///example.db"

)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():  
    db.create_all()
    if not Admins.query.filter_by(username="your username").first():

        hashed_password = set_password("Your password")

        admin_user = Admins(

            username="your username",

            password=hashed_password,

            email="your email",

            is_superadmin=True,
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created: your username")
    else:
        print("Admin user already exists.")
```

## 🚀 Running the Development Server

### Terminal 1: Flask Application

```bash
export FLASK_ENV=development
export FLASK_APP=server.py
python db_init.py  # Run once to create admin user
flask run --debug
```

### Terminal 2: Tailwind CSS

```bash
npm run dev
```

## 🌐 Accessing the Application

- **Main Site**: http://localhost:5000
- **Admin Panel**: http://localhost:5000/admin
- **Login**: Use the credentials you set in `db_init.py`

## 📝 Local Development Notes

### Environment Variables (Optional for Local)

You can create a `.env` file for local development, but most features will work without external services:

```bash
GMAIL_APP_PASSWORD=your_test_password
GMAIL_ADDRESS=your_test_email
CLOUD_NAME=your_cloudinary_name
CLOUDINARY_API_KEY=your_key
CLOUDINARY_API_SECRET=your_secret
SECRET_KEY=your_local_secret_key
```

### Features Available Locally

- ✅ Admin panel and authentication
- ✅ Blog article management 
- ✅ Product management 
- ✅ Order management
- ✅ Shopping cart functionality
- ✅ Email notifications 
- ✅ Image uploads to Cloudinary 

### Database File Location

Your SQLite database will be created as `example.db` in your project root. This file contains all your local data and should not be committed to version control.

## 🐛 Common Issues

### Windows-Specific Issues

- **Zoneinfo errors**: Make sure you've commented out zoneinfo imports
- **Path issues**: Use forward slashes in paths or Python's `os.path.join()`

### Database Issues

- **Table errors**: Run `db_init.py` to create tables
- **Permission errors**: Make sure the project directory is writable

### CSS Not Loading

- Make sure Tailwind is running: `npm run dev`
- Check that `static/css/main.css` is being generated

## 🔄 Switching Back to Production

When you're ready to deploy changes:

1. Uncomment the Supabase database URI
2. Uncomment error handlers
3. Uncomment zoneinfo imports
4. Re-enable sitemap blueprint
5. Make sure all environment variables are set on Render

## 📊 Testing Your Changes

Since there are no automated tests:

1. **Test Admin Panel**: Login, create/edit articles and products
2. **Test Store**: Add products to cart, go through checkout flow
3. **Test Mobile**: Check responsive design on different screen sizes
4. **Test Forms**: Verify CSRF protection is working

Remember: This is a hand-tested project, so be thorough with manual testing before deploying to production!