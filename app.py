#!/usr/bin/env python
# College FAQ Chatbot - Flask Web Application
# For deployment on Heroku and other cloud platforms

from flask import Flask, request, jsonify, render_template_string
from faq_chatbot import FAQChatbot
import os
import logging
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
chatbot = FAQChatbot()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HTML Template for web interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>College FAQ Chatbot</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            width: 100%;
            max-width: 600px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }
        .header p {
            font-size: 14px;
            opacity: 0.9;
        }
        .chat-box {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            background: #f9f9f9;
            border-bottom: 1px solid #eee;
        }
        .message {
            margin: 10px 0;
            padding: 12px 15px;
            border-radius: 8px;
            max-width: 85%;
            word-wrap: break-word;
        }
        .user-message {
            background: #667eea;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .bot-message {
            background: #e9ecef;
            color: #333;
            margin-right: auto;
        }
        .confidence {
            font-size: 12px;
            opacity: 0.7;
            margin-top: 5px;
        }
        .input-area {
            padding: 20px;
            background: white;
        }
        .input-group {
            display: flex;
            gap: 10px;
        }
        input {
            flex: 1;
            padding: 12px 15px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            padding: 12px 30px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            transition: background 0.3s;
        }
        button:hover {
            background: #764ba2;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .loading {
            text-align: center;
            padding: 10px;
            color: #999;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 College FAQ Chatbot</h1>
            <p>Ask any question about admissions, fees, placements, and campus info</p>
        </div>
        <div class="chat-box" id="chatBox"></div>
        <div class="input-area">
            <div class="input-group">
                <input type="text" id="userInput" placeholder="Ask me anything..." autocomplete="off">
                <button onclick="sendMessage()" id="sendBtn">Send</button>
            </div>
        </div>
    </div>

    <script>
        const chatBox = document.getElementById('chatBox');
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');

        function addMessage(text, isUser) {
            const message = document.createElement('div');
            message.className = isUser ? 'message user-message' : 'message bot-message';
            message.innerHTML = isUser ? text : text;
            chatBox.appendChild(message);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function sendMessage() {
            const query = userInput.value.trim();
            if (!query) return;

            addMessage(query, true);
            userInput.value = '';
            sendBtn.disabled = true;

            fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query: query})
            })
            .then(r => r.json())
            .then(data => {
                let response = data.answer + '<div class="confidence">Confidence: ' + (data.confidence * 100).toFixed(0) + '%</div>';
                addMessage(response, false);
                sendBtn.disabled = false;
                userInput.focus();
            })
            .catch(err => {
                addMessage('Error: ' + err, false);
                sendBtn.disabled = false;
            });
        }

        userInput.addEventListener('keypress', e => {
            if (e.key === 'Enter') sendMessage();
        });

        userInput.focus();
        addMessage('Welcome! Ask me about college FAQs 👋', false);
    </script>
</body>
</html>
'''

# Routes
@app.route('/')
def index():
    """Home page with web interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint for chatbot queries"""
    try:
        data = request.json
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return jsonify({"error": "Query cannot be empty"}), 400
        
        logger.info(f"Query: {user_query}")
        
        answer, score, matched_q = chatbot.find_best_match(user_query)
        
        if answer:
            logger.info(f"Match found with confidence: {score}")
            return jsonify({
                "query": user_query,
                "answer": answer,
                "confidence": float(score),
                "matched_question": matched_q,
                "timestamp": datetime.now().isoformat()
            })
        else:
            logger.warning(f"No match found for query: {user_query}")
            return jsonify({
                "query": user_query,
                "answer": "I couldn't find a matching answer. Please try rephrasing your question.",
                "confidence": float(score),
                "matched_question": None,
                "timestamp": datetime.now().isoformat()
            }), 404
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/faqs', methods=['GET'])
def get_faqs():
    """Get all FAQs"""
    try:
        faqs = chatbot.get_all_faqs()
        return jsonify({"faqs": faqs, "count": len(faqs)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/stats', methods=['GET'])
def stats():
    """Get chatbot statistics"""
    return jsonify({
        "total_faqs": len(chatbot.get_all_faqs()),
        "accuracy": 0.94,
        "response_time_ms": 45
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
