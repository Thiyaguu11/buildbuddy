from flask import Flask, render_template, request, jsonify, Response, send_from_directory
import subprocess
import os
import signal
import time

app = Flask(__name__, static_folder='src')
running_processes = {}

status_updates = {
    'status': 'idle',
    'version': '',
    'customer': '',
    'terminal': ''
}

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
    status_updates['version'] = data.get('field1')
    status_updates['customer'] = data.get('field2')


    if not request.is_json:
        return jsonify({'error': 'Invalid input, expected JSON'}), 400

    field1 = data.get('field1')
    field2 = data.get('field2')
    field3 = data.get('field3')
    field4 = data.get('field4')

    if not field1 or not field2:
        return jsonify({'error': 'Version and Customer are required fields.'}), 400

    def generate_output():
        try:
            process = subprocess.Popen(
                ['bash', 'script.sh', field1, field2, field3, field4],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, preexec_fn=os.setpgrp, bufsize=1
            )

            running_processes['build'] = process
            status_updates['status'] = 'running'

            for line in iter(process.stdout.readline, ''):
                status_updates['terminal'] += f"{line}<br/>"
                yield f"{line}<br/>"

            process.stdout.close()
            process.wait()  # Wait for the process to finish
        except Exception as e:
            yield f"Error: {str(e)}<br/>"
        finally:
            running_processes.pop('build', None)
            status_updates['status'] = 'idle'

    return Response(generate_output(), mimetype='text/html')

@app.route('/stop_kompass', methods=['POST'])
def stop_kompass():
    process = running_processes.pop('build', None)
    if process:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)  # Send SIGTERM to stop the process group
        status_updates['status'] = 'idle'
        return jsonify({'message': 'Build process stopped.'}), 200
    else:
        return jsonify({'error': 'No build process is currently running.'}), 400

@app.route('/start_nagare', methods=['POST'])
def start_nagare():
    data = request.json
    status_updates['version'] = data.get('field1')
    status_updates['customer'] = data.get('field2')

    if not request.is_json:
        return jsonify({'error': 'Invalid input, expected JSON'}), 400

    field1 = data.get('field1')
    field2 = data.get('field2')
    field3 = data.get('field3')

    if not field1 or not field2:
        return jsonify({'error': 'Version and Customer are required fields.'}), 400

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
                status_updates['terminal'] += f"{line}<br/>"
                yield f"{line}<br/>"

            process.stdout.close()
            process.wait()
        except Exception as e:
            yield f"Error: {str(e)}<br/>"
        finally:
            running_processes.pop('build', None)
            status_updates['status'] = 'idle'

    return Response(generate_output(), mimetype='text/html')

@app.route('/stop_nagare', methods=['POST'])
def stop_nagare():
    process = running_processes.pop('build', None)
    if process:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        status_updates['status'] = 'idle'
        return jsonify({'message': 'Build process stopped.'}), 200
    return jsonify({'error': 'No build process is currently running.'}), 400

@app.route('/nagare_status')
def nagare_status():
    return jsonify({
        'status': status_updates.get('status', 'idle'),
        'version': status_updates.get('version', ''),
        'customer': status_updates.get('customer', ''),
        'terminal': status_updates.get('terminal', '')
    })

@app.route('/status')
def status():
    return jsonify({
        'status': status_updates.get('status', 'idle'),
        'version': status_updates.get('version', ''),
        'customer': status_updates.get('customer', ''),
        'terminal': status_updates.get('terminal', '')
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

    