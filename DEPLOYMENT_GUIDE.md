# College FAQ Chatbot - Deployment Guide

## Overview
This guide provides comprehensive instructions for deploying the College FAQ Chatbot in various environments.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Deployment](#local-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment (Heroku)](#cloud-deployment-heroku)
5. [Flask Web Interface](#flask-web-interface)
6. [Advanced Deployment](#advanced-deployment)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- Python 3.8 or higher
- pip (Python package manager)
- git
- 100MB free disk space
- 512MB RAM (minimum)

### Verify Installation
```bash
python --version
pip --version
git --version
```

---

## Local Deployment

### Step 1: Clone the Repository
```bash
git clone https://github.com/Priyanka-N2781/College-FAQ-Chatbot.git
cd College-FAQ-Chatbot
```

### Step 2: Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the CLI Chatbot
```bash
python faq_chatbot.py
```

### Step 5: Test the Installation
```bash
# Run unit tests
python -m unittest test_chatbot.py

# Expected Output: All tests pass with OK
```

---

## Docker Deployment

### Create Dockerfile
Create a `Dockerfile` in the project root:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY faq_chatbot.py .
COPY test_chatbot.py .

CMD ["python", "faq_chatbot.py"]
```

### Build Docker Image
```bash
docker build -t college-faq-chatbot .
```

### Run Docker Container
```bash
docker run -it college-faq-chatbot
```

### Push to Docker Hub
```bash
# Tag image
docker tag college-faq-chatbot:latest username/college-faq-chatbot:latest

# Push to Docker Hub
docker push username/college-faq-chatbot:latest
```

---

## Flask Web Interface Deployment

### Step 1: Create Flask Application
Create `app.py`:

```python
from flask import Flask, request, jsonify
from faq_chatbot import FAQChatbot

app = Flask(__name__)
chatbot = FAQChatbot()

@app.route('/')
def home():
    return jsonify({"message": "College FAQ Chatbot API"})

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_query = data.get('query', '')
        
        if not user_query:
            return jsonify({"error": "Query cannot be empty"}), 400
        
        answer, score, matched_q = chatbot.find_best_match(user_query)
        
        if answer:
            return jsonify({
                "query": user_query,
                "answer": answer,
                "confidence": float(score),
                "matched_question": matched_q
            })
        else:
            return jsonify({
                "query": user_query,
                "answer": "I couldn't find a matching answer. Please rephrase your question.",
                "confidence": float(score),
                "matched_question": None
            }), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### Step 2: Install Flask
```bash
pip install flask
```

### Step 3: Run Flask Application
```bash
python app.py
```

### Step 4: Test API
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the class timings?"}'
```

### Expected Response
```json
{
  "query": "What are the class timings?",
  "answer": "Class timings are 9:00 AM to 4:30 PM...",
  "confidence": 0.89,
  "matched_question": "What are the class timings?"
}
```

---

## Cloud Deployment (Heroku)

### Step 1: Install Heroku CLI
```bash
# Download from https://devcenter.heroku.com/articles/heroku-cli
```

### Step 2: Login to Heroku
```bash
heroku login
```

### Step 3: Create Procfile
Create `Procfile` in project root:
```
web: gunicorn app:app
```

### Step 4: Install Gunicorn
```bash
pip install gunicorn
pip freeze > requirements.txt
```

### Step 5: Create Heroku App
```bash
heroku create college-faq-chatbot
```

### Step 6: Deploy to Heroku
```bash
git push heroku main
```

### Step 7: Check Logs
```bash
heroku logs --tail
```

### Step 8: Access Application
```
https://college-faq-chatbot.herokuapp.com
```

---

## AWS Lambda Deployment

### Step 1: Create Lambda Function
1. Go to AWS Console > Lambda
2. Click "Create Function"
3. Runtime: Python 3.9
4. Handler: lambda_handler

### Step 2: Create lambda_handler.py
```python
import json
from faq_chatbot import FAQChatbot

chatbot = FAQChatbot()

def lambda_handler(event, context):
    try:
        query = event.get('query', '')
        answer, score, matched_q = chatbot.find_best_match(query)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'query': query,
                'answer': answer,
                'confidence': float(score)
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

### Step 3: Create API Gateway
1. Go to API Gateway
2. Create REST API
3. Create POST method
4. Link to Lambda function
5. Deploy API

---

## Advanced Deployment

### Multi-Container Setup with Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3'
services:
  chatbot:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
  
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - chatbot
```

### Run with Docker Compose
```bash
docker-compose up
```

### Kubernetes Deployment

Create `deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: college-faq-chatbot
spec:
  replicas: 3
  selector:
    matchLabels:
      app: chatbot
  template:
    metadata:
      labels:
        app: chatbot
    spec:
      containers:
      - name: chatbot
        image: college-faq-chatbot:latest
        ports:
        - containerPort: 5000
        resources:
          limits:
            memory: "256Mi"
            cpu: "500m"
          requests:
            memory: "128Mi"
            cpu: "250m"
```

### Deploy to Kubernetes
```bash
kubectl apply -f deployment.yaml
kubectl expose deployment college-faq-chatbot --type=LoadBalancer --port=80 --target-port=5000
```

---

## Performance Optimization

### Caching
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_find_best_match(query):
    return chatbot.find_best_match(query)
```

### Load Balancing
- Use Nginx for reverse proxy
- Deploy multiple instances
- Use sticky sessions if needed

### Monitoring
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Query: {user_query}")
logger.info(f"Response Time: {response_time}ms")
logger.info(f"Confidence: {confidence}")
```

---

## Troubleshooting

### Issue 1: ModuleNotFoundError
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

### Issue 2: Port Already in Use
```bash
# Solution: Use different port
python app.py --port 5001

# Or kill process on port 5000
# Windows: netstat -ano | findstr :5000
# Linux/Mac: lsof -i :5000
```

### Issue 3: NLTK Data Missing
```python
import nltk
nltk.download('stopwords')
```

### Issue 4: Slow Response Time
- Check system resources
- Optimize TF-IDF vectorization
- Use caching
- Consider GPU acceleration

### Issue 5: API Connection Timeout
- Increase timeout in client
- Optimize query processing
- Add connection pooling

---

## Security Considerations

### 1. API Authentication
```python
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

@app.route('/api/chat', methods=['POST'])
@auth.login_required
def chat():
    # Protected endpoint
    pass
```

### 2. Rate Limiting
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/chat', methods=['POST'])
@limiter.limit("100 per day")
def chat():
    pass
```

### 3. Input Validation
```python
from werkzeug.utils import secure_filename

query = secure_filename(request.json.get('query', ''))
```

### 4. HTTPS Configuration
```python
from flask_talisman import Talisman

Talisman(app)
```

---

## Monitoring & Analytics

### Log Analysis
```bash
# View logs
heroku logs --tail

# Specific app logs
docker logs --follow container_name
```

### Performance Metrics
- Response time
- Query volume
- Accuracy rate
- User satisfaction

### Set Up Monitoring
- New Relic
- DataDog
- Prometheus + Grafana
- CloudWatch (AWS)

---

## Maintenance & Updates

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Backup Data
```bash
git commit -m "Backup FAQ database"
git push
```

### Version Control
```bash
git tag v1.0.0
git push --tags
```

---

## Support & Feedback

- **GitHub Issues**: https://github.com/Priyanka-N2781/College-FAQ-Chatbot/issues
- **Email**: support@example.com
- **Documentation**: https://github.com/Priyanka-N2781/College-FAQ-Chatbot

---

## License

MIT License - See LICENSE file for details

---

**Last Updated**: December 2025
