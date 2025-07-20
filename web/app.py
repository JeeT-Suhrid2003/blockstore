from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash
import os
import requests
import base64

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for flashing messages
STORAGE_DIR = "/home/jeet/storage"

# Ensure the storage directory exists
os.makedirs(STORAGE_DIR, exist_ok=True)

@app.route('/')
def index():
    # List stored files
    files = os.listdir(STORAGE_DIR)
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part in the request.')
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash('No selected file.')
        return redirect(url_for('index'))

    try:
        filename = file.filename
        content = file.read()
        b64_content = base64.b64encode(content).decode('utf-8')

        tx_data = f"{filename}:{b64_content}".encode()
        hex_tx = "0x" + tx_data.hex()

        # Send transaction to Tendermint
        res = requests.get(f"http://localhost:26657/broadcast_tx_commit?tx={hex_tx}")
        res_data = res.json()

        # Optionally, save the file locally for retrieval
        with open(os.path.join(STORAGE_DIR, filename), "wb") as f:
            f.write(content)

        if res_data.get("result", {}).get("deliver_tx", {}).get("code", 1) == 0:
            flash("File uploaded successfully and committed to blockchain.")
        else:
            flash("File upload failed: Blockchain rejected the transaction.")

        return redirect(url_for('index'))

    except Exception as e:
        flash(f"Internal Error: {str(e)}")
        return redirect(url_for('index'))

@app.route('/download/<filename>')
def download(filename):
    file_path = os.path.join(STORAGE_DIR, filename)
    if os.path.exists(file_path):
        return send_from_directory(STORAGE_DIR, filename, as_attachment=True)
    else:
        flash("File not found.")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(port=5000, debug=True)
