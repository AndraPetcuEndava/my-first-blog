# Django Girls Blog

A modern, beginner-friendly blog platform built with Django, featuring rich text editing, image uploads, threaded comments with replies, and a clean, responsive UI.

## Features

- User authentication (login/logout)
- Create, edit, publish, and delete blog posts
- Drafts management (save posts as drafts)
- Rich text editing with CKEditor (including image uploads)
- Add, approve, and delete comments
- Nested replies to comments (threaded discussion)
- AJAX-powered comment and reply submission for a smooth UX
- Responsive design with Bootstrap 5 and custom CSS
- Google Fonts for stylish typography
- Media uploads for post images

Blog Posts:
• Create, edit, publish, and delete blog posts.
• Draft support (save posts without publishing).
• Beautiful post editor powered by CKEditor (rich text & image upload).

Comments:
• Add, approve, and delete comments.
• Supports threaded replies.
• Moderation system — only approved comments are shown publicly.
• AJAX-enabled comment updates (no page reload needed).

Authentication:
• Secure login/logout via Django’s built-in authentication.
• Separate views and actions for authenticated and anonymous users.

Frontend & UI:
• Fully responsive layout with Bootstrap 5.
• Clean, feminine, minimal design using the Django Girls color palette.
• Custom CSS themes for posts, comments, and header components.
• Dynamic hero sections with blurred background images.

## New Features

Password Reset via Email:
• Users can reset their password using a secure email link.
• Custom email templates for password reset are in `blog/templates/registration/`.
• The password reset flow uses Django's built-in views and supports custom branding.

Sendgrid Integration:
• Outgoing emails (including password reset) are sent via SendGrid SMTP.
• The SendGrid API key and default sender are stored securely in a `.env` file.
• To use SendGrid, set these in your `.env`:
  ```
  SENDGRID_API_KEY=your_sendgrid_api_key
  DEFAULT_FROM_EMAIL=your_verified_sendgrid_email
  ```

  Environment Variables & Secrets:
- All sensitive settings (secret key, email credentials) are loaded from `.env` using `python-dotenv`.
- Example `.env`:
  ```
  DJANGO_SECRET_KEY=your_secret_key
  SENDGRID_API_KEY=your_sendgrid_api_key
  DEFAULT_FROM_EMAIL=your_verified_sendgrid_email
  ```
- `.env` is included in `.gitignore` for security.

## Project Structure

```
├── blog/
│   ├── migrations/
│   ├── static/
│   │   └── css/
│   ├── templates/
│   │   ├── blog/
│   │   └── registration/
|   |       ├── login.html
|   |       ├── password_reset_form.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── mysite/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── media/
├── db.sqlite3
├── manage.py
├── requirements.txt
```

## Setup Instructions

1. **Clone the repository**
   ```sh
   git clone <your-repo-url>
   cd djangogirls
   ```

2. **Create and activate a virtual environment**
   ```sh
   python -m venv myvenv
   myvenv\Scripts\activate  # On Windows
   # Or: source myvenv/bin/activate  # On Mac/Linux
   ```

3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Apply migrations**
   ```sh
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser (admin account)**
   ```sh
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```sh
   python manage.py runserver
   ```

7. **Access the app**
   - Blog: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/

## Usage

- Register or log in as an admin to create, edit, or delete posts.
- Add comments and replies to published posts.
- Approve or remove comments as an admin.
- Upload images to posts using the CKEditor.

## Customization

- **Static files:** Edit CSS in `blog/static/css/` for custom styles.
- **Templates:** Modify HTML in `blog/templates/` for layout changes.
- **Settings:** Update `mysite/settings.py` for project configuration.

## Additional Requirements

- python-decouple==3.8

Make sure your `requirements.txt` includes:

```
Django~=5.1.2
django-ckeditor==6.7.3
django-js-asset==3.1.2
pillow==12.0.0
python-decouple==3.8
python-dotenv==1.2.1
sqlparse==0.5.3
tzdata==2025.2
```

## Updated Setup Instructions

- After cloning the repo and activating your virtual environment, install all dependencies:
  ```sh
  pip install -r requirements.txt
  ```
- The project uses `python-decouple` and `python-dotenv` to securely load environment variables from a `.env` file.
- Your `.env` file should include:
  ```
  DJANGO_SECRET_KEY=your_secret_key
  SENDGRID_API_KEY=your_sendgrid_api_key
  DEFAULT_FROM_EMAIL=your_verified_sendgrid_email
  ```

## Deploying to PythonAnywhere

You can easily deploy this Django blog to [PythonAnywhere](https://www.pythonanywhere.com/), a free and beginner-friendly hosting platform for Python web apps.

### 1. Sign up and log in
- Go to https://www.pythonanywhere.com/ and create a free account.

### 2. Upload your code
- You can upload your project files using the PythonAnywhere file browser, or push your code to GitHub and clone it on PythonAnywhere using the Bash console:
  ```sh
  git clone <your-repo-url>
  cd djangogirls
  ```

### 3. Set up a virtual environment
- In the Bash console:
  ```sh
  python3.10 -m venv myvenv
  source myvenv/bin/activate
  pip install -r requirements.txt
  ```

### 4. Set up the database
- Run migrations:
  ```sh
  python manage.py migrate
  python manage.py createsuperuser
  ```

### 5. Configure static and media files
- In `mysite/settings.py`, set:
  ```python
  STATIC_ROOT = BASE_DIR / 'staticfiles'
  MEDIA_ROOT = BASE_DIR / 'media'
  ```
- Collect static files:
  ```sh
  python manage.py collectstatic
  ```

### 6. Configure the web app on PythonAnywhere
- Go to the **Web** tab and click **Add a new web app**.
- Choose **Manual configuration** > **Python 3.10**.
- Set the **Source code** path to your project folder (e.g., `/home/yourusername/djangogirls`).
- Set the **WSGI configuration file** path to your `mysite/wsgi.py` (e.g., `/home/yourusername/djangogirls/mysite/wsgi.py`).
- In the **Virtualenv** section, enter the path to your virtual environment (e.g., `/home/yourusername/djangogirls/myvenv`).

### 7. Set environment variables
- In the **Web** tab, add environment variables for `DJANGO_SETTINGS_MODULE` (usually `mysite.settings`).

### 8. Reload the web app
- Click the **Reload** button at the top of the Web tab.

### 9. Access your site
- Visit your PythonAnywhere subdomain (e.g., `yourusername.pythonanywhere.com`).

