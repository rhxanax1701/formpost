# FormPost

A self-hosted form backend service — like Formspree or Basin, but open source and yours to host.

Point any HTML form at your FormPost endpoint and instantly get:
- Submissions stored and viewable in a dashboard
- Email notifications on every submission
- CSV export for spreadsheets
- Spam protection out of the box
- One-command Docker deploy

---

## Why FormPost?

Most form services charge monthly fees, limit submissions, or sell your data.
FormPost runs on your own server. You own everything.

---

## Features

- **Unique endpoint per form** — each form gets its own `/f/abc123` URL
- **Submission dashboard** — view, manage and search all submissions
- **Email notifications** — get alerted instantly via SMTP (Gmail, SendGrid, etc.)
- **CSV export** — download all submissions as a spreadsheet
- **Spam protection** — honeypot field + hCaptcha integration
- **Rate limiting** — blocks flood attacks (10 requests/min per IP)
- **Docker Compose** — deploy in one command
- **No third-party dependencies** — runs fully self-contained

---

## Quick Start (Docker)

**1. Clone the repo**
```bash
git clone https://github.com/rhxanax1701/formpost.git
cd formpost
```

**2. Configure environment**
```bash
cp formpost/.env.example formpost/.env
nano formpost/.env
```

**3. Deploy**
```bash
docker compose up --build -d
```

**4. Open in browser**
http://localhost:5000/register

Create your account — registration closes after the first user is created.

---

## Local Development

```bash
cd formpost
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
python app.py
```

Visit `http://localhost:5000`

---

## Configuration

Copy `.env.example` to `.env` and fill in your values:

| Variable | Description | Example |
|---|---|---|
| `SECRET_KEY` | Random secret string | `openssl rand -hex 32` |
| `DATABASE_URL` | Database connection | `sqlite:///formpost.db` |
| `MAIL_SERVER` | SMTP server | `smtp.gmail.com` |
| `MAIL_PORT` | SMTP port | `587` |
| `MAIL_USE_TLS` | Use TLS | `true` |
| `MAIL_USERNAME` | Your email address | `you@gmail.com` |
| `MAIL_PASSWORD` | App password | see below |
| `MAIL_DEFAULT_SENDER` | Sender address | `you@gmail.com` |
| `HCAPTCHA_SITEKEY` | hCaptcha site key | from hcaptcha.com |
| `HCAPTCHA_SECRET` | hCaptcha secret key | from hcaptcha.com |

### Gmail Setup

1. Enable 2-Factor Authentication on your Google account
2. Go to **Google Account → Security → App Passwords**
3. Generate a password for "FormPost"
4. Use that 16-character password as `MAIL_PASSWORD`

### Generate a Secret Key

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## Usage

**1. Create a form** in the dashboard → copy your endpoint URL

**2. Add to any HTML page:**

```html
<form action="https://yourserver.com/f/YOUR_TOKEN" method="POST">

  <!-- Honeypot spam trap — leave this hidden -->
  <input name="_honey" style="display:none" tabindex="-1" autocomplete="off">

  <!-- Your fields — use any field names you want -->
  <input name="name" placeholder="Your name" required>
  <input name="email" type="email" placeholder="Your email" required>
  <textarea name="message" placeholder="Message" required></textarea>

  <!-- Optional hCaptcha — enable in dashboard per form -->
  <div class="h-captcha" data-sitekey="YOUR_HCAPTCHA_SITE_KEY"></div>
  <script src="https://js.hcaptcha.com/1/api.js" async defer></script>

  <button type="submit">Send</button>
</form>
```

**3. View submissions** in the dashboard at `/dashboard`

**4. Export to CSV** from the form detail page

---

## API

FormPost accepts standard HTML form POST requests. It also works with JavaScript:

```javascript
const response = await fetch('https://yourserver.com/f/YOUR_TOKEN', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    name: 'John',
    email: 'john@example.com',
    message: 'Hello!'
  })
});

const data = await response.json();
// { "status": "ok", "id": 1 }
```

### Response codes

| Status | Meaning |
|---|---|
| `200 ok` | Submission accepted |
| `200 spam` | Flagged as spam (honeypot or captcha failed) |
| `404` | Form not found or disabled |
| `429` | Rate limit exceeded (10/min per IP) |

---

## Project Structure
formpost/

├── app.py              # App factory, extensions

├── config.py           # Configuration from .env

├── models.py           # Database models

├── mail.py             # Email sending

├── limiter.py          # Rate limiting

├── routes/

│   ├── auth.py         # Login, register, logout

│   ├── forms.py        # Dashboard, create, delete, export

│   ├── submit.py       # Public form submission endpoint

│   └── demo.py         # Demo form page

├── templates/          # Jinja2 HTML templates

├── static/             # CSS

├── requirements.txt

├── Dockerfile

└── docker-compose.yml

---

## Tech Stack

- **Python 3.12** / **Flask** — web framework
- **SQLAlchemy** — database ORM
- **SQLite** — default database (swappable to Postgres)
- **Flask-Mail** — SMTP email
- **Flask-Limiter** — rate limiting
- **hCaptcha** — spam protection
- **Docker Compose** — containerized deploy
- **Gunicorn** — production WSGI server

---

## Roadmap

- [ ] Webhook forwarding
- [ ] Discord / Slack notifications
- [ ] File upload support
- [ ] Auto-responder emails
- [ ] Postgres support
- [ ] HTTPS / Nginx setup guide


---

## Production Deployment (Nginx + HTTPS)

### 1. Install Nginx and Certbot

```bash
sudo apt install nginx certbot python3-certbot-nginx -y
```

### 2. Create Nginx config

```bash
sudo nano /etc/nginx/sites-available/formpost
```

Paste this (replace `yourdomain.com`):

```nginx
server {
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Enable the site

```bash
sudo ln -s /etc/nginx/sites-available/formpost /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Get free HTTPS certificate

```bash
sudo certbot --nginx -d yourdomain.com
```

Certbot auto-renews. Your site is now on HTTPS.

### 5. Switch to Postgres (recommended for production)

```bash
pip install psycopg2-binary
```

Update `.env`:
DATABASE_URL=postgresql://user:password@localhost/formpost

### 6. Set a strong secret key

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Paste the output as `SECRET_KEY` in your `.env`.

---

## License

MIT — free to use, modify and self-host.
