# vidstar

## Backend Setup

1. Create a virtual environment and activate it:
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```
2. Install Flask and Flask-CORS:
   ```powershell
   pip install flask flask-cors
   ```
3. Run the backend:
   ```powershell
   python app.py
   ```

## Frontend Setup

1. Open a new terminal and run:
   ```powershell
   npx create-react-app frontend
   cd frontend
   npm start
   ```
2. Replace the contents of `src/App.js` with:
   ```javascript
   import React, { useEffect, useState } from 'react';

   function App() {
     const [msg, setMsg] = useState('');

     useEffect(() => {
       fetch('http://localhost:5000/api/hello')
         .then(res => res.json())
         .then(data => setMsg(data.message));
     }, []);

     return <div>{msg}</div>;
   }

   export default App;
   ```