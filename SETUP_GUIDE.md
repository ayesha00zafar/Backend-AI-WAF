# WAF Dashboard Setup Guide

## 🚀 Quick Start

### Step 1: Install Dependencies

#### Frontend (React)
```bash
# Install Node.js dependencies
npm install

# Install Tailwind CSS dependencies
npm install -D tailwindcss@latest postcss@latest autoprefixer@latest
```

#### Backend (Python)
```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
pip install -r requirements_api.txt
```

### Step 2: Verify Tailwind CSS Setup

1. **Check if Tailwind is working:**
   - Start the React app: `npm start`
   - Navigate to http://localhost:3000
   - You should see a blue test component with styled text
   - If styles aren't applying, try the troubleshooting steps below

2. **If Tailwind isn't working:**
   ```bash
   # Rebuild Tailwind CSS
   npx tailwindcss -i ./src/index.css -o ./src/output.css --watch
   ```

### Step 3: Start the Servers

#### Terminal 1: Flask API Server
```bash
# Make sure virtual environment is activated
python api_server.py
```
- Server will run on http://localhost:5000
- You should see: "Running on http://0.0.0.0:5000"

#### Terminal 2: React Development Server
```bash
npm start
```
- App will run on http://localhost:3000
- You should see the dashboard with Tailwind styles

## 🔧 Troubleshooting

### Tailwind CSS Issues

1. **Styles not applying:**
   ```bash
   # Clear cache and reinstall
   rm -rf node_modules package-lock.json
   npm install
   npm start
   ```

2. **Check if PostCSS is configured:**
   - Verify `postcss.config.js` exists
   - Make sure `tailwind.config.js` is in the root directory

3. **Manual Tailwind build:**
   ```bash
   npx tailwindcss -i ./src/index.css -o ./src/output.css --watch
   ```

### Flask/Mitmproxy Issues

1. **Python version compatibility:**
   ```bash
   # Check Python version (should be 3.7+)
   python --version
   ```

2. **Install specific Flask version:**
   ```bash
   pip install flask>=2.3.0
   pip install mitmproxy>=10.0.0
   ```

3. **Virtual environment issues:**
   ```bash
   # Recreate virtual environment
   deactivate
   rm -rf venv
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   pip install -r requirements.txt
   pip install -r requirements_api.txt
   ```

### Socket.IO Issues

1. **CORS errors:**
   - Make sure Flask-CORS is installed
   - Check that the API server is running on port 5000

2. **Connection refused:**
   ```bash
   # Check if port 5000 is available
   netstat -an | grep 5000
   ```

## 📱 Testing the Dashboard

### 1. Tailwind Test
- Navigate to "Tailwind Test" in the sidebar
- You should see a blue box with white text
- If this works, Tailwind is properly configured

### 2. Live Logs
- Navigate to "Live Logs"
- You should see a table with mock data
- New logs should appear every 5 seconds

### 3. Attack Stats
- Navigate to "Attack Stats"
- You should see charts and statistics
- Data should update in real-time

### 4. Control Panel
- Navigate to "Control Panel"
- Test the proxy start/stop buttons
- Try exporting logs

## 🔍 Debugging

### Check Console for Errors
1. **Frontend:** Open browser DevTools (F12)
2. **Backend:** Check terminal output for Flask errors

### Common Error Messages

1. **"Module not found":**
   ```bash
   npm install
   ```

2. **"Port already in use":**
   ```bash
   # Kill process on port 5000
   lsof -ti:5000 | xargs kill -9
   ```

3. **"CORS error":**
   - Make sure Flask-CORS is installed
   - Check that both servers are running

## 🎯 Expected Behavior

### When Everything Works:
1. **Frontend (http://localhost:3000):**
   - Clean, modern dashboard interface
   - Responsive design that works on mobile
   - Real-time updates every 5 seconds
   - Color-coded status indicators

2. **Backend (http://localhost:5000):**
   - Flask server running without errors
   - Socket.IO connections established
   - API endpoints responding correctly

3. **Real-time Features:**
   - New logs appearing automatically
   - Charts updating with new data
   - Status indicators changing in real-time

## 🚨 Emergency Fixes

### If Nothing Works:
```bash
# Complete reset
rm -rf node_modules package-lock.json
npm install
npm start

# In another terminal
deactivate
rm -rf venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements_api.txt
python api_server.py
```

### If Tailwind Still Not Working:
```bash
# Force rebuild
npx tailwindcss -i ./src/index.css -o ./src/output.css --watch
```

## 📞 Getting Help

If you're still having issues:
1. Check the browser console for JavaScript errors
2. Check the Flask terminal for Python errors
3. Verify all dependencies are installed correctly
4. Make sure both servers are running simultaneously 