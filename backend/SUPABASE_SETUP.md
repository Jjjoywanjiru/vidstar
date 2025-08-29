# Supabase Configuration for Flask Backend

1. Install the required package:
   ```powershell
   pip install supabase
   ```

2. Add your Supabase URL and API key to a `.env` file in the backend directory:
   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_or_service_key
   ```

3. Use the following code in your Flask app to connect to Supabase:
   ```python
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
       data = supabase.table('your_table').select('*').execute()
       return jsonify(data.data)

   if __name__ == '__main__':
       app.run(debug=True)
   ```

4. Make sure to add `.env` to your `.gitignore` file.

Replace `your_supabase_url`, `your_supabase_anon_or_service_key`, and `your_table` with your actual Supabase project details.
