from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Konfigurasi Koneksi PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:data.analyst@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_google_sheets_data():
    # Setup Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(r"C:\Users\LINGGA\Kapuas Holding\Digital Marketing\website-flask\ui_dcc_mkd\service_account_dcc-mkd.json", scope)
    client = gspread.authorize(creds)

    # Akses data dari Google Sheets
    sheet = client.open("Kabupaten/kota").worksheet('Sheet1')
    regency_city_list = sheet.col_values(2)  # Ambil data dari kolom 1 untuk Regency/City
    province_list = sheet.col_values(1)     # Ambil data dari kolom 2 untuk Province
    return regency_city_list, province_list

# Model Database
class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_no = db.Column(db.String(100), nullable=False)
    cs = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    source = db.Column(db.String(100), nullable=False)
    leads_name = db.Column(db.String(100), nullable=False)
    product = db.Column(db.String(100), nullable=False)
    regency_city = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(100), nullable=False)
    phone_no = db.Column(db.String(15), nullable=False)
    branch = db.Column(db.String(100), nullable=False)
    sales = db.Column(db.String(100), nullable=False)
    status_cs = db.Column(db.String(100), nullable=False)
    estimasi_luasan = db.Column(db.String(100), nullable=False)
    estimasi_revenue = db.Column(db.String(100), nullable=False)
    chat_leveling = db.Column(db.String(100), nullable=False)
    noted = db.Column(db.Text, nullable=True)
    reason = db.Column(db.Text, nullable=True)
    status_sales = db.Column(db.String(100), nullable=False)

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

# Halaman Dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/input_data', methods=['GET', 'POST'])
def input_data():
    # Ambil data dari Google Sheets
    regency_city_list, province_list = get_google_sheets_data()

    if request.method == 'POST':
        data = Data(
            id_no=request.form['id_no'],
            cs=request.form['cs'],
            date=request.form['date'],
            source=request.form['source'],
            leads_name=request.form['leads_name'],
            product=request.form['product'],
            regency_city=request.form['regency_city'],
            province=request.form['province'],
            phone_no=request.form['phone_no'],
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
        db.session.add(data)
        db.session.commit()
        return redirect(url_for('input_data'))

    # Kirim data ke template
    return render_template('input_data.html', regency_city_list=regency_city_list, province_list=province_list)

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
