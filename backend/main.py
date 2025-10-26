from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import google.generativeai as genai
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure API keys
GEMINI_API_KEY_1 = os.getenv("GEMINI_API_KEY_1")
GEMINI_API_KEY_2 = os.getenv("GEMINI_API_KEY_2")
GMAIL_EMAIL = os.getenv("GMAIL_EMAIL")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# Initialize Flask with production configuration
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True

# Configure CORS for security
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5000", "https://your-production-domain.com"],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Initialize Gemini clients with error handling
gemini_clients = []
current_key = 0
last_switch_time = time.time()

def setup_gemini_clients():
    global gemini_clients
    for api_key in [GEMINI_API_KEY_1, GEMINI_API_KEY_2]:
        if api_key:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-pro')
                # Test the model with a simple prompt
                model.generate_content("Test")
                gemini_clients.append(model)
                logger.info(f"Successfully initialized Gemini client")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {str(e)}")

try:
    setup_gemini_clients()
    if not gemini_clients:
        logger.error("No Gemini clients were initialized successfully")
except Exception as e:
    logger.error(f"Failed to setup Gemini clients: {str(e)}")

def switch_api_key():
    global current_key, last_switch_time
    current_time = time.time()
    
    # Only switch if at least 5 minutes have passed since last switch
    if current_time - last_switch_time >= 300 and len(gemini_clients) > 1:
        current_key = (current_key + 1) % len(gemini_clients)
        last_switch_time = current_time
        logger.info(f"Switched to API key {current_key + 1}")

def validate_email_data(data):
    required_fields = ['name', 'email', 'subject', 'message']
    if not all(field in data for field in required_fields):
        return False, "Missing required fields"
    if not all(data[field].strip() for field in required_fields):
        return False, "All fields must be non-empty"
    return True, None

def send_email(contact_data):
    if not all([GMAIL_EMAIL, GMAIL_APP_PASSWORD]):
        logger.error("Email configuration missing")
        return jsonify({"error": "Email service not configured"}), 503
    
    # Validate email data
    is_valid, error_message = validate_email_data(contact_data)
    if not is_valid:
        return jsonify({"error": error_message}), 400
    
    msg = MIMEMultipart()
    msg['From'] = GMAIL_EMAIL
    msg['To'] = GMAIL_EMAIL
    msg['Subject'] = f"Portfolio Contact: {contact_data['subject']}"
    
    body = f"""
    New contact from portfolio website:
    
    Name: {contact_data['name']}
    Email: {contact_data['email']}
    Subject: {contact_data['subject']}
    
    Message:
    {contact_data['message']}
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        logger.info(f"Email sent successfully from {contact_data['email']}")
        return None
    except Exception as e:
        logger.error(f"Email sending failed: {str(e)}")
        return jsonify({"error": "Failed to send email"}), 503

@app.route("/api/chat", methods=["POST"])
def chat_endpoint():
    if not gemini_clients:
        logger.error("No Gemini clients available")
        return jsonify({"error": "Service not configured"}), 503
    
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
            
        message = data.get("message").strip()
        if not message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        # Rate limiting check (implement proper rate limiting in production)
        current_time = time.time()
        if hasattr(chat_endpoint, 'last_request_time'):
            if current_time - chat_endpoint.last_request_time < 1:  # 1 second delay
                return jsonify({"error": "Please wait before sending another message"}), 429
        chat_endpoint.last_request_time = current_time
        
        # Get current client
        client = gemini_clients[current_key]
        
        # Prepare context and prompt
        context = """You are an AI assistant for Mujahid Islam's portfolio website. 
        You help visitors learn about his services in AI automation, Make.com/n8n workflows, 
        Python scripting, and Selenium automation. You can also take orders for automation projects.
        Keep responses professional, concise, and focused on his services."""
        
        try:
            # Generate response with timeout
            prompt = f"{context}\n\nUser: {message}\nAssistant:"
            response = client.generate_content(prompt)
            
            if not response or not response.text:
                raise Exception("No response generated")
                
            # Check if we need to switch API keys
            switch_api_key()
            
            logger.info("Successfully generated chat response")
            return jsonify({
                "reply": response.text,
                "key_in_use": f"API Key {current_key + 1}",
                "status": "success"
            })
            
        except Exception as e:
            logger.error(f"Gemini API Error: {str(e)}")
            switch_api_key()
            return jsonify({"error": "AI service temporarily unavailable"}), 503
            
    except Exception as e:
        logger.error(f"Server Error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/contact", methods=["POST"])
def contact_endpoint():
    try:
        contact_data = request.get_json()
        error_response = send_email(contact_data)
        if error_response:
            return error_response
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"Contact form error: {str(e)}")
        return jsonify({"error": "Failed to process contact form"}), 500

if __name__ == "__main__":
    # In production, use a proper WSGI server like Gunicorn
    # For development:
    app.run(host="0.0.0.0", port=8000, debug=False)