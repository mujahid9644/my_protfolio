# Professional Portfolio Website

Modern portfolio website showcasing AI automation and data analysis skills, featuring an AI-powered chatbot.

## Features

- Responsive design with modern UI/UX
- AI chatbot powered by Google's Gemini API
- Secure contact form with Gmail integration
- API key rotation system
- Production-ready setup

## Project Structure

```
├── index.html              # Frontend UI
├── protfolio.jpg          # Profile image
└── backend/
    ├── main.py            # Flask backend server
    ├── requirements.txt    # Python dependencies
    ├── .env.example       # Environment template
    └── .env               # Configuration (not in version control)
```

## Quick Start

### Local Development

1. Setup Backend:
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin activate # Unix
pip install -r requirements.txt
```

2. Configure Environment:
- Copy `.env.example` to `.env`
- Add your Gemini API keys
- Set Gmail credentials

3. Start Server:
```bash
python main.py
```

4. Open `index.html` in your browser

### Production Deployment

1. Frontend Deployment:
- Host static files on Netlify, Vercel, or similar
- Update API endpoint in `index.html`:
  ```javascript
  const API_URL = 'https://your-backend-domain.com';
  ```

2. Backend Deployment (e.g., on DigitalOcean):
```bash
# Install dependencies
pip install -r requirements.txt

# Start with Gunicorn
gunicorn main:app --bind 0.0.0.0:8000 --workers 4
```

3. Set up Nginx reverse proxy:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

4. SSL Configuration:
```bash
# Install Certbot
sudo certbot --nginx -d your-domain.com
```

### Security Checklist

✅ Environment variables for sensitive data
✅ CORS protection
✅ Rate limiting implementation
✅ Secure email handling
✅ API key rotation
✅ Error logging
✅ Input validation

## Maintenance

- Monitor API usage
- Rotate API keys regularly
- Check error logs
- Update dependencies
- Backup configuration

## Support

For issues or questions, contact Mujahid Islam:
- Email: mujahidislam2540@gmail.com
- LinkedIn: [Mujahid Islam](https://www.linkedin.com/in/mujahid-islam-648532308/)
- GitHub: [mujahid9644](https://github.com/mujahid9644)