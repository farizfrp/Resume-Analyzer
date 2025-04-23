# Resume Ranking Application

This Streamlit application helps recruiters rank multiple resumes based on a job description using AI.

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

1. Run the application:
   ```bash
   streamlit run app.py
   ```
2. Upload multiple resumes (PDF or DOCX format)
3. Enter or upload the job description
4. Click "Rank Resumes" to get AI-powered ranking and analysis

## Features

- Support for multiple resume formats (PDF, DOCX)
- Detailed analysis of each resume
- Ranking based on job description match
- Explanation of ranking decisions 