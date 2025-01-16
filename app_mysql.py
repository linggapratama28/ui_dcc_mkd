from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import psycopg2
from sqlalchemy import event
from datetime import datetime
from sqlalchemy import create_engine, text

app = Flask(__name__)

# Konfigurasi Koneksi MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:data.analyst@localhost/kapuasgroup'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Fungsi untuk mengakses data dari Google Sheets
def get_google_sheets_data():
    # Setup Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        r"C:\Users\LINGGA\Kapuas Holding\Digital Marketing\website-flask\ui_dcc_mkd\service_account_dcc-mkd.json", scope)
    client = gspread.authorize(creds)

    # Akses data dari Google Sheets
    sheet = client.open("Kabupaten/kota").worksheet('Sheet1')
    regency_city_list = sheet.col_values(2)  # Ambil data dari kolom 2 untuk Regency/City
    province_list = sheet.col_values(1)     # Ambil data dari kolom 1 untuk Province
    
    return regency_city_list, province_list

# Model Database
class Data(db.Model):
    __tablename__ = 'dcc_mkd'
    
    id_no = db.Column(db.String(100), nullable=False, unique=True, primary_key=True)  # Nomor yang akan otomatis di-generate
    cs = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    source = db.Column(db.String(100), nullable=False)
    leads_name = db.Column(db.String(100), nullable=False)
    product = db.Column(db.String(100), nullable=False)
    regency_city = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(100), nullable=False)
    no_hp_leads = db.Column(db.String(15), nullable=False, unique=True)
    branch = db.Column(db.String(100), nullable=False)
    sales = db.Column(db.String(100), nullable=False)
    status_cs = db.Column(db.String(100), nullable=False)
    estimasi_luasan = db.Column(db.String(100), nullable=False)
    estimasi_revenue = db.Column(db.Integer, nullable=False)
    chat_leveling = db.Column(db.String(100), nullable=False)
    noted = db.Column(db.Text, nullable=True)
    reason = db.Column(db.Text, nullable=True)
    status_sales = db.Column(db.String(100), nullable=False)

# Fungsi untuk generate `id_no` secara otomatis
def generate_id_no(prefix):
    # Ambil entri terakhir berdasarkan prefix
    last_entry = db.session.query(Data).filter(Data.id_no.like(f'{prefix}%')).order_by(Data.id_no.desc()).first()

    if last_entry:
        # Ambil nomor dari id_no dengan memotong prefix
        try:
            last_number = int(last_entry.id_no[len(prefix):])
        except ValueError:
            last_number = 0  # Jika parsing gagal, mulai dari 0
    else:
        last_number = 0  # Jika tidak ada entri sebelumnya, mulai dari 0

    # Tambah nomor berikutnya
    new_number = last_number + 1
    new_id_no = f"{prefix}{new_number:05d}"  # Format ID dengan 5 digit

    # Pastikan tidak ada duplikat ID
    while db.session.query(Data).filter_by(id_no=new_id_no).first() is not None:
        new_number += 1
        new_id_no = f"{prefix}{new_number:04d}"

    return new_id_no

# Buat tabel di database (jalankan ini sekali saja)
with app.app_context():
    db.create_all()

# Halaman login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'lingga' and password == 'test':
            return redirect(url_for('welcome'))
        else:
            return 'Username atau password salah', 401
    return render_template('login.html')

# Halaman selamat datang
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

# Model data
class Lead(db.Model):
    __tablename__ = 'leads_report'
    id = db.Column(db.Integer, primary_key=True)
    cs_name = db.Column(db.String(100))
    registered = db.Column(db.Integer)
    dispatched = db.Column(db.Integer)
    date = db.Column(db.Date)

# Route untuk dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    query = text("""
    SELECT 
        status_cs,
        SUM(CASE WHEN status_cs = 'REGISTERED' THEN 1 ELSE 0 END) AS registered_count,
        SUM(CASE WHEN status_cs IN ('DISPATCHED', 'FOLLOW UP', 'NURTURED') THEN 1 ELSE 0 END) AS dispatched_count
    FROM dcc_mkd
    WHERE date BETWEEN :start_date AND :end_date
    GROUP BY status_cs
    """)

    # Eksekusi query dengan rentang tanggal yang tepat
    results = db.session.execute(query, {'start_date': '2024-07-01', 'end_date': '2024-07-31'}).fetchall()
    
    # Cek hasil query untuk debugging
    print(results)  # Tambahkan untuk melihat hasil query di console

    # Enumerate results before passing them to the template
    results_with_index = list(enumerate(results, start=1))
    return render_template('dashboard.html', results=results_with_index)

# Halaman Input Data
@app.route('/input_data', methods=['GET', 'POST'])
def input_data():
    regency_city_list, province_list = get_google_sheets_data()

    if request.method == 'POST':
        # Ambil prefix dari dropdown form yang benar
        prefix = request.form['id_no']  # Mengambil nilai dari dropdown
        id_no = generate_id_no(prefix)

        data = Data(
            id_no=id_no,
            cs=request.form['cs'],
            date=request.form['date'],
            source=request.form['source'],
            leads_name=request.form['leads_name'],
            product=request.form['product'],
            regency_city=request.form['regency_city'],
            province=request.form['province'],
            no_hp_leads=request.form['no_hp_leads'],
            branch=request.form['branch'],
            sales=request.form['sales'],
            status_cs=request.form['status_cs'],
            estimasi_luasan=request.form['estimasi_luasan'],
            estimasi_revenue=request.form['estimasi_revenue'],
            chat_leveling=request.form['chat_leveling'],
            noted=request.form['noted'],
            reason=request.form['reason'],
            status_sales=request.form['status_sales']
        )

        try:
            db.session.add(data)
            db.session.commit()
            return redirect(url_for('input_data'))
        except Exception as e:
            db.session.rollback()
            return f"Terjadi kesalahan saat menyimpan data: {str(e)}"

    return render_template('input_data.html', regency_city_list=regency_city_list, province_list=province_list)

# Halaman Data
@app.route('/data')
def data():
    conn = psycopg2.connect("dbname=database_name user=username password=password")
    cur = conn.cursor()
    cur.execute("SELECT * FROM nama_tabel;")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('data.html', data=data)

# Halaman Search Data
@app.route('/search_data')
def search_data():
    return render_template('search_data.html')

# Halaman Download Data
@app.route('/download_data')
def download_data():
    return render_template('download_data.html')

if __name__ == '__main__':
    app.run(debug=True)
