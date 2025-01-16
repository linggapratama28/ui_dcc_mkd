from flask import Flask, render_template, request, jsonify
import pymysql
from datetime import datetime

app = Flask(__name__)

# Koneksi ke MySQL
def get_db_connection():
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='data.analyst',
                                 db='kapuas',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

# Route untuk halaman dashboard
@app.route('/dashboard')
def dashboard():
    # Mengambil data untuk tanggal hari ini
    current_date = datetime.today().strftime('%Y-%m-%d')
    data = get_leads_data(current_date)

    return render_template('dashboard.html', current_date=current_date, chart_data=data)

# Route untuk mengambil data berdasarkan tanggal
@app.route('/get-data')
def get_data():
    date = request.args.get('date')
    data = get_leads_data(date)
    return jsonify(data)

# Fungsi untuk mengambil data dari MySQL
def get_leads_data(date):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        # Query untuk mengambil data leads berdasarkan tanggal
        query = """
        SELECT cs_name, registered_leads, dispatched_leads
        FROM leads_report
        WHERE report_date = %s
        """
        cursor.execute(query, (date,))
        results = cursor.fetchall()

        # Struktur data yang akan dikirim ke frontend
        data = {
            'cs_names': [row['cs_name'] for row in results],
            'registered': [row['registered_leads'] for row in results],
            'dispatched': [row['dispatched_leads'] for row in results]
        }
    connection.close()
    return data

if __name__ == '__main__':
    app.run(debug=True)