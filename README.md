# Resume Analysis System

A powerful resume analysis tool that compares candidate resumes against job descriptions using AI to provide detailed insights and rankings. Built by [Mercity-AI](https://github.com/Mercity-AI).

## 🌟 Features

- **Real-time Analysis**: Process multiple resumes simultaneously with live results
- **Smart Matching**: AI-powered comparison of resumes against job requirements
- **Detailed Analysis**:
  - Technical skills assessment
  - Core responsibility matching
  - Qualitative evaluation of experience
  - Project gravity analysis
  - Candidate fit scoring
- **Interactive Results**:
  - Percentage match scores
  - Detailed requirement breakdowns
  - Recruiter-style summaries
  - Final recommendations with key factors
- **Export Functionality**: Download complete analysis results as CSV

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Mercity-AI/Resume-Analyzer.git
cd Resume-Analyzer
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
   - Create a `.env` file in the root directory
   - Add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

### Running the Application

1. Start the Streamlit app:
```bash
streamlit run app.py
```

2. Open your browser and navigate to the displayed URL (typically `http://localhost:8501`)

## 📝 Usage

1. **Enter OpenAI API Key**
   - Input your OpenAI API key
   - Select preferred models for analysis

2. **Job Description Analysis**
   - Paste the job description
   - Click "Analyze Job Description"
   - Review and edit extracted requirements if needed

3. **Resume Analysis**
   - Upload one or multiple resumes (PDF, DOCX, or TXT)
   - Click "Analyze Resumes"
   - Watch real-time analysis results
   - Download complete analysis as CSV when finished

## 🔍 Analysis Components

- **Requirements Match**:
  - Must-have technical skills
  - Core responsibilities
  - Experience requirements
  - Qualifications

- **Qualitative Assessment**:
  - Project gravity
  - Ownership and initiative
  - Role transferability
  - Strengths and weaknesses

- **Final Evaluation**:
  - Match percentage
  - Recruiter summary
  - Final recommendation
  - Key factors for decision

## 🛠️ Technical Details

- Built with Streamlit for the user interface
- Uses OpenAI's GPT models for analysis
- Supports PDF, DOCX, and TXT file formats
- Real-time processing and display
- Session state management for consistent results

## 📊 CSV Export Format

The exported CSV includes detailed columns for:
- Contact information
- Technical skills assessment
- Core responsibility matching
- Additional skills evaluation
- Screening criteria results
- Qualitative assessments
- Final recommendations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for providing the AI models
- Streamlit for the amazing web framework
- All contributors and users of this project 