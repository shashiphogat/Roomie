from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

# Configuration
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'Shashi2704@'
MYSQL_DB = 'test3'
SECRET_KEY = 'your_secret_key'

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

def create_connection():
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

def create_tables():
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                fullname VARCHAR(100) NOT NULL,
                cuchd_id VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL
            )
            """
        )
        connection.commit()
        cursor.close()
        connection.close()
    except mysql.connector.Error as e:
        print(f"Error creating tables: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fullname = request.form['fullname']
        cuchd_id = request.form['cuchd_id']
        password = request.form['password']
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                # Check if the CUCHD ID already exists
                cursor.execute(
                    """
                    SELECT * FROM users WHERE cuchd_id = %s
                    """,
                    (cuchd_id,)
                )
                existing_user = cursor.fetchone()
                if existing_user:
                    error_message = 'The provided CUCHD ID already exists. Please choose a different one.'
                    return render_template('signup.html', error=error_message)
                else:
                    # Insert the new user into the database
                    cursor.execute(
                        """
                        INSERT INTO users (fullname, cuchd_id, password)
                        VALUES (%s, %s, %s)
                        """,
                        (fullname, cuchd_id, password)
                    )
                    connection.commit()
                    cursor.close()
                    connection.close()
                    session['cuchd_id'] = cuchd_id
                    return redirect(url_for('dashboard'))
            except mysql.connector.Error as e:
                print(f"Error executing SQL query: {e}")
                return 'An error occurred while signing up'
        else:
            return 'Error connecting to database'
    return render_template('signup.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cuchd_id = request.form['cuchd_id']
        password = request.form['password']
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(
                    """
                    SELECT * FROM users WHERE cuchd_id = %s AND password = %s
                    """,
                    (cuchd_id, password)
                )
                user = cursor.fetchone()
                cursor.close()
                connection.close()
                if user:
                    session['cuchd_id'] = cuchd_id
                    return redirect(url_for('dashboard'))
                else:
                    error_message = 'Invalid CUCHD ID or password. Please try again.'
                    return render_template('login.html', error=error_message)
            except mysql.connector.Error as e:
                print(f"Error executing SQL query: {e}")
                return 'An error occurred while logging in'
        else:
            return 'Error connecting to database'
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'cuchd_id' in session:
        cuchd_id = session['cuchd_id']
        return f'Logged in as {cuchd_id}'
    return redirect(url_for('login'))

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
