from flask import Flask, render_template, request, jsonify, Response, send_from_directory
import subprocess
import os
import signal
import time
import sqlite3
from database import init_db, log_build, get_build_stats

app = Flask(__name__, static_folder='src')
running_processes = {}
status_updates = {
    'status': 'idle',
    'version': '',
    'customer': '',
    'terminal': ''
}

init_db()

@app.route('/build_stats')
def build_stats():
    try:
        conn = sqlite3.connect('build_buddy.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT build_type, 
                   COUNT(*) as total,
                   SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
                   SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
            FROM builds
            GROUP BY build_type
        ''')
        results = cursor.fetchall()
        
        stats = {
            'kompass': {'total': 0, 'successful': 0, 'failed': 0},
            'nagare': {'total': 0, 'successful': 0, 'failed': 0}
        }
        
        for row in results:
            build_type, total, successful, failed = row
            stats[build_type.lower()] = {
                'total': total,
                'successful': successful,
                'failed': failed
            }
        return jsonify(stats)
    except Exception as e:
        app.logger.error(f"Database error: {str(e)}")
        return jsonify({
            'kompass': {'total': 0, 'successful': 0, 'failed': 0},
            'nagare': {'total': 0, 'successful': 0, 'failed': 0}
        })
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/kompass')
def kompass():
    return render_template('kompass.html')

@app.route('/nagare')
def nagare():
    return render_template('nagare.html')

@app.route('/Home')
def home():
    return render_template('dashboard.html')

@app.route('/start_kompass', methods=['POST'])
def start_kompass():
    status_updates['terminal'] = ''
    data = request.json
    
    if not request.is_json:
        return "<script>showPopup('Invalid input, expected JSON');</script>", 400

    field1 = data.get('field1')
    field2 = data.get('field2')
    field3 = data.get('field3')
    field4 = data.get('field4')

    if not field1 or not field2:
        return "<script>showPopup('Version and Customer are required fields.');</script>", 400

    status_updates['version'] = field1
    status_updates['customer'] = field2

    def generate_output():
        try:
            process = subprocess.Popen(
                ['bash', 'script.sh', field1, field2, field3, field4],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, 
                preexec_fn=os.setpgrp, bufsize=1
            )
            running_processes['build'] = process
            status_updates['status'] = 'running'

            for line in iter(process.stdout.readline, ''):
                if 'Exiting' in line:
                    log_build('kompass', field1, field2, 'failed')
                    yield "<script>showPopup('Build failed: Script exited unexpectedly');</script>"
                    break
                if 'PROGRESS:' in line:
                    try:
                        progress = int(line.split('PROGRESS:')[1].strip())
                        status_updates['progress'] = progress
                        if progress == 100:
                            log_build('kompass', field1, field2, 'success')
                            yield "<script>showPopup('Build completed successfully');</script>"
                    except ValueError:
                        pass
                    continue
                status_updates['terminal'] += f"{line}<br/>"
                yield f"{line}<br/>"
        except Exception as e:
            log_build('kompass', field1, field2, 'failed')
            yield f"<script>showPopup('Build failed: {str(e)}');</script>"
        finally:
            running_processes.pop('build', None)
            status_updates['status'] = 'idle'
            status_updates['progress'] = 0

    return Response(generate_output(), mimetype='text/html')

@app.route('/stop_kompass', methods=['POST'])
def stop_kompass():
    process = running_processes.pop('build', None)
    if process:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        status_updates['status'] = 'idle'
        return jsonify({'message': 'Build process stopped.', 'type': 'success'}), 200
    else:
        return jsonify({'message': 'No build process is currently running.', 'type': 'error'}), 400

@app.route('/start_nagare', methods=['POST'])
def start_nagare():
    status_updates['terminal'] = ''
    data = request.json
    
    if not request.is_json:
        return jsonify({'message': 'Invalid input, expected JSON', 'type': 'error'}), 400

    field1 = data.get('field1')
    field2 = data.get('field2')
    field3 = data.get('field3')

    if not field1 or not field2:
        return jsonify({'message': 'Version and Customer are required fields.', 'type': 'error'}), 400

    status_updates['version'] = field1
    status_updates['customer'] = field2

    def generate_output():
        try:
            process = subprocess.Popen(
                ['bash', 'nagare_script.sh', field1, field2, field3],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, 
                preexec_fn=os.setpgrp, bufsize=1
            )
            running_processes['build'] = process
            status_updates['status'] = 'running'

            for line in iter(process.stdout.readline, ''):
                if 'Exiting' in line:
                    log_build('nagare', field1, field2, 'failed')
                    yield "<script>showPopup('Build failed: Script exited unexpectedly');</script>"
                    break
                if 'PROGRESS:' in line:
                    try:
                        progress = int(line.split('PROGRESS:')[1].strip())
                        status_updates['progress'] = progress
                        if progress == 100:
                            log_build('nagare', field1, field2, 'success')
                            yield "<script>showPopup('Build completed successfully');</script>"
                    except ValueError:
                        pass
                    continue
                status_updates['terminal'] += f"{line}<br/>"
                yield f"{line}<br/>"
        except Exception as e:
            log_build('nagare', field1, field2, 'failed')
            yield f"<script>showPopup('Build failed: {str(e)}');</script>"
        finally:
            running_processes.pop('build', None)
            status_updates['status'] = 'idle'
            status_updates['progress'] = 0

    return Response(generate_output(), mimetype='text/html')

@app.route('/stop_nagare', methods=['POST'])
def stop_nagare():
    process = running_processes.pop('build', None)
    if process:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        status_updates['status'] = 'idle'
        return jsonify({'message': 'Build process stopped.', 'type': 'success'}), 200
    else:
        return jsonify({'message': 'No build process is currently running.', 'type': 'error'}), 400

@app.route('/status')
def status():
    return jsonify({
        'status': status_updates.get('status', 'idle'),
        'version': status_updates.get('version', ''),
        'customer': status_updates.get('customer', ''),
        'terminal': status_updates.get('terminal', ''),
        'progress': status_updates.get('progress', 0),
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
