from flask import Flask, render_template_string
import sqlite3
import requests

BOT_TOKEN = "7558045354:AAG_hRnQaGykSf-QPpZbThqaqFI6Bpx3dwM"
app = Flask(__name__)

HTML_TEMPLATE = """
<h2>📄 {{ file_name }}</h2>
<a href="{{ download_url }}" target="_blank">
    <button>⬇ Download File</button>
</a>
"""

@app.route('/download/<file_code>')
def download(file_code):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT file_id, file_name FROM files WHERE id=?", (file_code,))
    row = cursor.fetchone()
    if not row:
        return "❌ Invalid or expired link.", 404

    file_id, file_name = row
    resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}")
    if not resp.ok:
        return "❌ Could not fetch file.", 500

    file_path = resp.json()["result"]["file_path"]
    tg_file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

    return render_template_string(HTML_TEMPLATE, file_name=file_name, download_url=tg_file_url)

if __name__ == '__main__':
    app.run(port=8000)
