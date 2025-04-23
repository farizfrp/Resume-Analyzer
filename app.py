import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
import PyPDF2
import docx
import pandas as pd
import tempfile

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_text_from_pdf(pdf_file):
    print("\n=== Extracting text from PDF ===")
    text = ""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    print(f"Extracted {len(text)} characters from PDF")
    return text

def extract_text_from_docx(docx_file):
    print("\n=== Extracting text from DOCX ===")
    doc = docx.Document(docx_file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    print(f"Extracted {len(text)} characters from DOCX")
    return text

def analyze_job_description(job_description):
    print("\n=== Analyzing Job Description ===")
    
    jd_prompt = f"""
    You are an expert HR analyst skilled at extracting key requirements from job descriptions.
    Analyze this job description and extract the following information:

    1. Core technical requirements (must-have skills)
    2. Secondary technical requirements (nice-to-have skills)
    3. Required experience level and type
    4. Industry-specific requirements
    5. Project/role complexity expectations
    6. Key performance indicators (KPIs)

    Job Description:
    {job_description}

    Format your response as a structured JSON object with these keys:
    {{
        "core_technical": ["list", "of", "core", "skills"],
        "secondary_technical": ["list", "of", "secondary", "skills"],
        "experience_requirements": "detailed description",
        "industry_specific": ["list", "of", "requirements"],
        "complexity_level": "description of expected complexity",
        "kpis": ["list", "of", "key", "indicators"]
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are an expert HR analyst skilled at extracting key requirements from job descriptions."},
                {"role": "user", "content": jd_prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        return response.choices[0].message.content

    except Exception as e:
        print(f"Error in analyze_job_description: {str(e)}")
        return None

def analyze_resume(jd_analysis, resume_text):
    print("\n=== Analyzing Resume ===")
    
    analysis_prompt = f"""
    You are an expert resume reviewer with deep industry knowledge and experience in technical hiring.
    Your task is to analyze this resume against the extracted job requirements and provide a comprehensive evaluation.

    Job Requirements Analysis:
    {jd_analysis}

    Resume:
    {resume_text}

    Evaluate the resume against these requirements using this weighted scoring system:
    
    A. Core Technical Competency (35% weight)
       - Direct matches with core technical requirements
       - Depth of expertise in required technologies
       - Evidence of practical application
       - Industry-specific technical knowledge
       Score: [0.0-10.0] (use single decimal point)
    
    B. Experience & Impact (35% weight)
       - Relevance of past roles to current requirements
       - Demonstrated impact in previous positions
       - Complexity of handled projects
       - Leadership and initiative shown
       Score: [0.0-10.0] (use single decimal point)
    
    C. Secondary Skills & Adaptability (20% weight)
       - Nice-to-have technical skills
       - Learning agility and adaptability
       - Cross-functional experience
       - Problem-solving capabilities
       Score: [0.0-10.0] (use single decimal point)
    
    D. Industry Alignment (10% weight)
       - Industry-specific experience
       - Domain knowledge
       - Understanding of industry challenges
       - Relevant certifications/training
       Score: [0.0-10.0] (use single decimal point)

    For each category, provide:
    - Score (0.0-10.0 with single decimal point)
    - Detailed analysis of strengths
    - Specific examples demonstrating capabilities
    - Impact metrics where available

    Format your response EXACTLY as follows:

    Core Technical Competency (35%):
    Score: [0.0-10.0]
    Analysis: [detailed analysis of technical capabilities]
    Examples: [specific examples demonstrating expertise]
    Impact: [quantifiable impact where available]

    Experience & Impact (35%):
    Score: [0.0-10.0]
    Analysis: [detailed analysis of experience and impact]
    Examples: [specific examples of achievements]
    Impact: [quantifiable results and outcomes]

    Secondary Skills & Adaptability (20%):
    Score: [0.0-10.0]
    Analysis: [detailed analysis of additional capabilities]
    Examples: [specific examples of adaptability]
    Impact: [demonstrated learning and growth]

    Industry Alignment (10%):
    Score: [0.0-10.0]
    Analysis: [detailed analysis of industry fit]
    Examples: [specific industry-relevant experience]
    Impact: [industry-specific achievements]

    FINAL SCORE: [weighted average score out of 10.0]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are an expert resume reviewer with deep industry knowledge and experience in technical hiring."},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        return response.choices[0].message.content

    except Exception as e:
        print(f"Error in analyze_resume: {str(e)}")
        return f"Error analyzing resume: {str(e)}"

def process_file(file):
    print(f"\n=== Processing file: {file.name} ===")
    if file.name.endswith('.pdf'):
        return extract_text_from_pdf(file)
    elif file.name.endswith('.docx'):
        return extract_text_from_docx(file)
    else:
        text = file.getvalue().decode('utf-8')
        print(f"Extracted {len(text)} characters from text file")
        return text

def main():
    st.title("Resume Ranking System")
    st.write("Upload a job description and multiple resumes to get AI-powered analysis and ranking.")
    
    # Job Description Input
    job_description = st.text_area("Enter Job Description:", height=200)
    
    # Resume Upload
    uploaded_files = st.file_uploader("Upload Resumes (PDF, DOCX, or TXT)", accept_multiple_files=True)
    
    if st.button("Rank Resumes"):
        if not job_description or not uploaded_files:
            st.error("Please provide both a job description and at least one resume.")
            return
        
        # Analyze job description once
        jd_analysis = analyze_job_description(job_description)
        if not jd_analysis:
            st.error("Failed to analyze job description. Please try again.")
            return
        
        results = []
        for file in uploaded_files:
            resume_text = process_file(file)
            analysis = analyze_resume(jd_analysis, resume_text)
            
            # Extract final score from analysis with better error handling
            try:
                score_lines = [line for line in analysis.split('\n') if 'FINAL SCORE:' in line.upper()]
                if score_lines:
                    score_text = score_lines[0].split(':')[1].strip()
                    score_chars = [c for c in score_text if c.isdigit() or c == '.']
                    if not score_chars:
                        score = 0.0
                    else:
                        score_str = ''.join(score_chars)
                        if score_str.count('.') > 1:
                            score_str = score_str[:score_str.rindex('.')]
                        score = float(score_str)
                else:
                    score = 0.0
            except Exception as e:
                print(f"Error extracting score: {str(e)}")
                score = 0.0
            
            results.append({
                'filename': file.name,
                'score': score,
                'analysis': analysis
            })
        
        # Sort results by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Display results
        st.subheader("Ranking Results")
        for i, result in enumerate(results, 1):
            with st.expander(f"{i}. {result['filename']} - Score: {result['score']:.1f}/10"):
                sections = result['analysis'].split('\n\n')
                for section in sections:
                    if section.strip():
                        st.markdown(section)

if __name__ == "__main__":
    main() 