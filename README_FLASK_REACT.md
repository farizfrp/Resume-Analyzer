# Resume Ranking System - Flask + React Version

A modern web application for AI-powered resume analysis and ranking, built with Flask backend and React frontend.

## 🚀 Features

- **AI-Powered Analysis**: Uses OpenAI's GPT models for intelligent resume evaluation
- **Job Description Analysis**: Automatically extracts requirements from job descriptions
- **Dual Scoring System**: 
  - Quantitative scoring (requirement matching)
  - Semantic scoring (qualitative assessment)
- **Contact Information Extraction**: Automatically extracts candidate details
- **Interactive Web Interface**: Modern React UI with Material-UI components
- **File Upload Support**: PDF, DOCX, and TXT resume formats
- **CSV Export**: Export detailed analysis results
- **Real-time Progress**: Live updates during analysis process

## 🏗 Architecture

```
Resume-Analyzer/
├── backend/                 # Flask API Server
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   └── venv/              # Virtual environment (auto-created)
├── frontend/               # React Web Application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── App.js         # Main React app
│   │   └── index.js       # React entry point
│   ├── public/
│   │   └── index.html     # HTML template
│   ├── package.json       # Node.js dependencies
│   └── node_modules/      # Node modules (auto-created)
├── jd_analyzer.py         # Job description analysis
├── resume_analyzer.py     # Resume analysis logic
├── start.sh              # Combined startup script
├── start_backend.sh      # Backend startup script
├── start_frontend.sh     # Frontend startup script
└── .env                  # Environment variables
```

## 📋 Prerequisites

### Backend Requirements
- Python 3.8 or higher
- pip (Python package manager)

### Frontend Requirements
- Node.js 16 or higher
- npm (Node package manager)

### API Requirements
- OpenAI API key

## 🛠 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Resume-Analyzer
```

### 2. Set Up Environment Variables
Create a `.env` file in the root directory:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Quick Start (Recommended)
Run both backend and frontend with one command:
```bash
./start.sh
```

This will:
- Set up Python virtual environment
- Install backend dependencies
- Install frontend dependencies
- Start both servers

### 4. Manual Setup (Alternative)

#### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start backend server
python app.py
```

#### Frontend Setup (In a separate terminal)
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start frontend development server
npm start
```

## 🌐 Usage

1. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8008

2. **API Key Verification**
   - Enter your OpenAI API key when prompted
   - Or set it in the `.env` file

3. **Model Selection**
   - Choose primary model for job description analysis
   - Choose reasoning model for resume analysis

4. **Job Description Analysis**
   - Paste the job description
   - Click "Analyze Job Description"
   - Review extracted requirements

5. **Requirements Editing (Optional)**
   - Edit the extracted requirements if needed
   - Or skip to proceed with current requirements

6. **Resume Analysis**
   - Upload resume files (PDF, DOCX, TXT)
   - Click "Analyze Resumes"
   - View detailed results

7. **Export Results**
   - Click "Export CSV" to download analysis results

## 🔧 API Endpoints

### Backend API (Port 8008)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/verify-api-key` | POST | Verify OpenAI API key |
| `/api/analyze-job-description` | POST | Analyze job description |
| `/api/update-requirements` | POST | Update job requirements |
| `/api/analyze-resumes` | POST | Analyze uploaded resumes |
| `/api/export-csv` | GET | Export results to CSV |
| `/api/current-requirements` | GET | Get current requirements |

## 🎨 Features in Detail

### Job Description Analysis
- Extracts must-have requirements (technical skills, experience, qualifications)
- Identifies good-to-have requirements (additional skills, bonus experience)
- Detects screening criteria (work authorization, location constraints)

### Resume Analysis
- **Contact Information**: Name, email, phone, location, LinkedIn, experience
- **Quantitative Matching**: Boolean matching against specific requirements
- **Qualitative Assessment**: Project gravity, ownership, transferability
- **Semantic Scoring**: AI-powered holistic evaluation (0-100%)

### Scoring System
- **Quantitative Score**: Fraction of requirements met (e.g., "15/21")
- **Semantic Score**: Percentage representing overall fit (0-100%)
- **Final Ranking**: Sorted by semantic score

## 🚧 Development

### Project Structure
```
frontend/src/components/
├── ApiKeyVerification.js    # API key input component
├── ModelSelection.js        # Model selection component
├── JobDescriptionAnalysis.js # Job description input
├── RequirementsEditor.js    # Requirements editing
├── ResumeAnalysis.js        # File upload and analysis
└── ResultsDisplay.js        # Results visualization
```

### Adding New Features
1. **Backend**: Add new routes in `backend/app.py`
2. **Frontend**: Create new components in `frontend/src/components/`
3. **Analysis Logic**: Modify `jd_analyzer.py` or `resume_analyzer.py`

## 🔍 Troubleshooting

### Common Issues

**Backend won't start**
```bash
# Check Python version
python3 --version

# Ensure virtual environment is activated
source backend/venv/bin/activate

# Reinstall dependencies
pip install -r backend/requirements.txt
```

**Frontend won't start**
```bash
# Check Node.js version
node --version

# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**API Key Issues**
- Verify your OpenAI API key is valid
- Check the `.env` file format
- Ensure you have sufficient API credits

**File Upload Issues**
- Ensure files are PDF, DOCX, or TXT format
- Check file size limits
- Verify backend is running and accessible

### Debug Mode
Set `debug=True` in `backend/app.py` for detailed error messages.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- OpenAI for the GPT models
- React and Material-UI for the frontend framework
- Flask for the backend framework
- All contributors to the open-source libraries used

---

**Happy Recruiting! 🎯** 