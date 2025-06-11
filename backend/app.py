from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import json
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
import PyPDF2
import docx
import io
from werkzeug.utils import secure_filename
import tempfile

# Import our custom modules
import sys
sys.path.append('..')
from jd_analyzer import analyze_job_description, format_requirements_for_display, parse_edited_requirements
from resume_analyzer import analyze_resume

# Load environment variables
load_dotenv()

# Configure Flask to serve React build files
app = Flask(__name__, static_folder='../frontend/build', static_url_path='')
CORS(app)

# Initialize OpenAI client
api_key_from_env = os.getenv("OPENAI_API_KEY")
if not api_key_from_env:
    print("❌ OPENAI_API_KEY not found in environment variables!")
    print("Please set OPENAI_API_KEY in your .env file")
    exit(1)

client = OpenAI(api_key=api_key_from_env)
print("✅ OpenAI API key loaded from environment")

# Global variables to store analysis data
current_requirements = None
current_job_description = None
analysis_results = []

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            text += page_text
            
            # Log each page separately for debugging
            print(f"\n--- PAGE {page_num + 1} TEXT ---")
            print(page_text[:300] + "..." if len(page_text) > 300 else page_text)
            print("--- END PAGE ---")
    
    except Exception as e:
        print(f"Error extracting PDF text: {str(e)}")
        return ""
    
    # Clean up the text - remove extra whitespace and normalize
    text = ' '.join(text.split())
    
    # Log the extracted text for debugging
    print("\n" + "="*80)
    print(f"EXTRACTED PDF TEXT FROM: {pdf_file.name if hasattr(pdf_file, 'name') else 'PDF file'}")
    print("="*80)
    print(f"Total text length: {len(text)} characters")
    print("First 1000 characters:")
    print(text[:1000] + "..." if len(text) > 1000 else text)
    print("="*80)
    
    return text

def extract_text_from_docx(docx_file):
    """Extract text from DOCX file"""
    doc = docx.Document(docx_file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def process_file(file):
    """Process uploaded file and extract text"""
    filename = secure_filename(file.filename)
    
    if filename.endswith('.pdf'):
        return extract_text_from_pdf(file)
    elif filename.endswith('.docx'):
        return extract_text_from_docx(file)
    else:
        # Assume it's a text file
        return file.read().decode('utf-8')

def calculate_percentage(score):
    """Convert score like '10/21' to percentage"""
    try:
        numerator, denominator = map(int, score.split('/'))
        percentage = (numerator / denominator) * 100
        return round(percentage)
    except:
        return 0

def flatten_analysis_for_csv(analysis):
    """Flatten the analysis JSON for CSV export"""
    flattened = {}
    
    # Contact Information
    contact_info = analysis.get('contact_info', {})
    flattened['full_name'] = contact_info.get('full_name', '')
    flattened['email'] = contact_info.get('email', '')
    flattened['phone'] = contact_info.get('phone', '')
    flattened['location'] = contact_info.get('location', '')
    flattened['linkedin'] = contact_info.get('linkedin', '')
    flattened['other_links'] = ', '.join(contact_info.get('other_links', []))
    flattened['age'] = contact_info.get('age', '')
    flattened['gender'] = contact_info.get('gender', '')
    flattened['total_work_experience'] = contact_info.get('total_work_experience', '')
    flattened['last_position'] = contact_info.get('last_position', '')

    # Requirement Match - Core Responsibilities (combined in one column)
    req_match = analysis.get('requirement_match', {})
    must_have = req_match.get('must_have_requirements', {})
    core_resp = must_have.get('core_responsibilities', {})
    flattened['core_responsibilities'] = ', '.join([f"{k}: {str(v)}" for k, v in core_resp.items()])

    # Additional Skills (combined in one column)
    good_to_have = req_match.get('good_to_have_requirements', {})
    add_skills = good_to_have.get('additional_skills', {})
    flattened['additional_skills'] = ', '.join([f"{k}: {str(v)}" for k, v in add_skills.items()])

    # Screening Criteria (combined in one column)
    screening = req_match.get('additional_screening_criteria', {})
    flattened['additional_screening_criteria'] = ', '.join([f"{k}: {str(v)}" for k, v in screening.items()])

    # Qualitative Assessment
    qual_assessment = analysis.get('qualitative_assessment', {})
    flattened['inferred_skills_from_projects'] = ', '.join(qual_assessment.get('inferred_skills_from_projects', []))
    flattened['project_gravity'] = qual_assessment.get('project_gravity', '')
    flattened['ownership_and_initiative'] = qual_assessment.get('ownership_and_initiative', '')
    flattened['transferability_to_role'] = qual_assessment.get('transferability_to_role', '')
    flattened['recruiter_style_summary'] = qual_assessment.get('recruiter_style_summary', '')

    # Summary of Key Factors
    flattened['summary_of_key_factors'] = ', '.join(analysis.get('summary_of_key_factors', []))

    return flattened

# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Resume Ranking API is running"})

@app.route('/api/check-api-key', methods=['GET'])
def check_api_key():
    """Check if API key is loaded and working"""
    try:
        # Test the API key with a simple request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=5
        )
        
        return jsonify({"success": True, "message": "API key is working"})
    
    except Exception as e:
        return jsonify({"success": False, "message": f"API key error: {str(e)}"}), 400

@app.route('/api/analyze-job-description', methods=['POST'])
def analyze_jd():
    """Analyze job description and extract requirements"""
    global current_requirements, current_job_description
    
    data = request.get_json()
    job_description = data.get('job_description')
    model = data.get('model', 'gpt-4.1')
    
    if not job_description:
        return jsonify({"success": False, "message": "Job description is required"}), 400
    
    try:
        requirements = analyze_job_description(job_description, model=model)
        
        if requirements:
            current_job_description = job_description
            current_requirements = requirements
            
            return jsonify({
                "success": True,
                "message": "Job description analyzed successfully",
                "requirements": requirements
            })
        else:
            return jsonify({"success": False, "message": "Failed to analyze job description"}), 500
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error analyzing job description: {str(e)}"}), 500

@app.route('/api/update-requirements', methods=['POST'])
def update_requirements():
    """Update job requirements after editing"""
    global current_requirements
    
    data = request.get_json()
    must_have_text = data.get('must_have_text', '')
    preferred_text = data.get('preferred_text', '')
    additional_text = data.get('additional_text', '')
    
    try:
        edited_requirements = parse_edited_requirements(must_have_text, preferred_text, additional_text)
        
        if edited_requirements:
            edited_requirements["original_job_description"] = current_job_description
            current_requirements = edited_requirements
            
            return jsonify({
                "success": True,
                "message": "Requirements updated successfully",
                "requirements": edited_requirements
            })
        else:
            return jsonify({"success": False, "message": "Failed to parse edited requirements"}), 500
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error updating requirements: {str(e)}"}), 500

@app.route('/api/analyze-resumes', methods=['POST'])
def analyze_resumes():
    """Analyze uploaded resumes against job requirements"""
    global analysis_results
    
    if current_requirements is None:
        return jsonify({"success": False, "message": "Please analyze job description first"}), 400
    
    if 'files' not in request.files:
        return jsonify({"success": False, "message": "No files uploaded"}), 400
    
    files = request.files.getlist('files')
    model = request.form.get('model', 'o4-mini')
    
    if not files:
        return jsonify({"success": False, "message": "No files selected"}), 400
    
    analysis_results = []
    results = []
    
    try:
        for file in files:
            if file.filename == '':
                continue
                
            # Process the file
            resume_text = process_file(file)
            
            # Log the processed text for debugging
            print("\n" + "="*80)
            print(f"PROCESSED TEXT FOR AI ANALYSIS - FILE: {file.filename}")
            print("="*80)
            print(f"Text length: {len(resume_text)} characters")
            print("First 500 characters:")
            print(resume_text[:500])
            print("="*80)
            
            # Analyze the resume
            analysis = analyze_resume(resume_text, current_requirements, model=model)
            
            if analysis:
                # Calculate percentage scores
                quantitative_percentage = calculate_percentage(analysis['quantitative_score'])
                semantic_percentage = analysis.get('semantic_score', 0)
                
                # Store result
                result = {
                    'filename': file.filename,
                    'quantitative_percentage': quantitative_percentage,
                    'semantic_percentage': semantic_percentage,
                    'percentage': semantic_percentage,  # Use semantic as main percentage
                    'quantitative_score': analysis['quantitative_score'],
                    'semantic_score': analysis['semantic_score'],
                    'analysis': analysis['analysis']
                }
                
                results.append(result)
                analysis_results.append(result)
        
        # Sort results by semantic percentage (descending)
        results.sort(key=lambda x: x['semantic_percentage'], reverse=True)
        
        return jsonify({
            "success": True,
            "message": f"Analyzed {len(results)} resumes successfully",
            "results": results
        })
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error analyzing resumes: {str(e)}"}), 500

@app.route('/api/export-csv', methods=['GET'])
def export_csv():
    """Export analysis results to CSV"""
    if not analysis_results:
        return jsonify({"success": False, "message": "No analysis results to export"}), 400
    
    try:
        # Flatten the analysis data for CSV
        csv_data = []
        for result in analysis_results:
            flattened_data = flatten_analysis_for_csv(result['analysis'])
            flattened_data['filename'] = result['filename']
            flattened_data['quantitative_percentage'] = result['quantitative_percentage']
            flattened_data['semantic_percentage'] = result['semantic_percentage']
            flattened_data['percentage'] = result['semantic_percentage']
            csv_data.append(flattened_data)
        
        # Create DataFrame and CSV
        df = pd.DataFrame(csv_data)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='') as tmp_file:
            df.to_csv(tmp_file.name, index=False)
            tmp_file_path = tmp_file.name
        
        return send_file(
            tmp_file_path,
            as_attachment=True,
            download_name='resume_analysis_results.csv',
            mimetype='text/csv'
        )
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error exporting CSV: {str(e)}"}), 500

@app.route('/api/current-requirements', methods=['GET'])
def get_current_requirements():
    """Get current job requirements"""
    if current_requirements is None:
        return jsonify({"success": False, "message": "No requirements available"}), 404
    
    return jsonify({
        "success": True,
        "requirements": current_requirements
    })

# Serve React App
@app.route('/')
def serve_react_app():
    """Serve the React app"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_react_static(path):
    """Serve React static files"""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=8008, host='0.0.0.0') 