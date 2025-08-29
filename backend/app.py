
import os
from flask import Flask, jsonify
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/api/hello')
def hello():
    return jsonify(message="Hello from Flask!")

# Example: Fetch data from a table
@app.route('/api/data')
def get_data():
    # Replace 'your_table' with your actual table name
    data = supabase.table('your_table').select('*').execute()
    return jsonify(data.data)

if __name__ == '__main__':
    app.run(debug=True)
