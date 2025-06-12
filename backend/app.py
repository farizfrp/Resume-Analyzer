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
import re

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
    print(f"Core responsibilities: {flattened['core_responsibilities']}")
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

@app.route('/api/job-description-chat', methods=['POST'])
def job_description_chat():
    """Handle conversational job description creation"""
    data = request.get_json()
    message = data.get('message', '')
    context = data.get('context', {})
    messages = data.get('messages', [])
    
    if not message:
        return jsonify({"success": False, "message": "Message is required"}), 400
    
    try:
        # Build conversation history for OpenAI
        conversation_history = []
        
        # System prompt for job description creation
        system_prompt = """You are a helpful HR assistant specializing in creating comprehensive job descriptions. Your role is to guide users through creating detailed, professional job descriptions by asking relevant questions and gathering information step by step.

When creating job descriptions, include:
- Job title and department
- Company overview (if provided)
- Job summary/overview
- Key responsibilities (5-8 bullet points)
- Required qualifications (education, experience, skills)
- Preferred qualifications
- Benefits and compensation (if discussed)
- Application process

For predefined company profiles, use the provided company overview and benefits information in the job description. When a user selects a company profile, incorporate the company information naturally into the conversation and final job description.

Ask follow-up questions to gather missing information. When you have gathered enough basic information (job title, some responsibilities or requirements), proactively offer to generate a complete job description. Use phrases like "I can now create a job description for you" or "Let me generate a comprehensive job description" to trigger the generation.

Be conversational, helpful, and professional. Always be ready to create job descriptions once you have the essentials.

Current context: {context}""".format(context=json.dumps(context))
        
        conversation_history.append({"role": "system", "content": system_prompt})
        
        # Add previous messages to conversation history
        for msg in messages:
            if msg['type'] == 'user':
                conversation_history.append({"role": "user", "content": msg['content']})
            elif msg['type'] == 'assistant':
                conversation_history.append({"role": "assistant", "content": msg['content']})
        
        # Add current user message
        conversation_history.append({"role": "user", "content": message})
        
        # Get response from OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=conversation_history,
            max_tokens=1000,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Update context based on the conversation
        updated_context = update_job_context(context, message, ai_response)
        
        # Debug logging for context
        print("\n" + "="*80)
        print("CONTEXT DEBUG:")
        print("="*80)
        print(f"Original context: {context}")
        print(f"User message: {message}")
        print(f"AI response (first 200 chars): {ai_response[:200]}...")
        print(f"Updated context: {updated_context}")
        print("="*80)
        
        # Check if we should generate a complete job description
        job_description = None
        if should_generate_job_description(updated_context, ai_response):
            print("\n" + "="*80)
            print("GENERATING JOB DESCRIPTION WITH CONTEXT:")
            print("="*80)
            print(f"Context passed to generation: {updated_context}")
            print("="*80)
            job_description = generate_complete_job_description(updated_context)
        
        return jsonify({
            "success": True,
            "response": ai_response,
            "context": updated_context,
            "jobDescription": job_description
        })
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Error in chat: {str(e)}"}), 500

def update_job_context(context, user_message, ai_response):
    """Update conversation context based on user input and AI response"""
    updated_context = context.copy()
    
    # Simple keyword-based context extraction from user message
    message_lower = user_message.lower()
    ai_lower = ai_response.lower()
    
    # Extract job title
    if not updated_context.get('jobTitle'):
        # Try to extract job title from message
        common_titles = ['software engineer', 'data scientist', 'product manager', 'marketing manager', 
                        'sales manager', 'developer', 'analyst', 'designer', 'coordinator', 'engineer',
                        'manager', 'director', 'specialist', 'associate', 'lead', 'senior', 'junior',
                        'architect', 'consultant', 'representative', 'executive', 'administrator',
                        'technician', 'supervisor', 'officer', 'assistant']
        
        for title in common_titles:
            if title in message_lower:
                # Extract a more complete job title from the message
                words = user_message.split()
                for i, word in enumerate(words):
                    if word.lower() == title:
                        # Try to get a 2-3 word job title
                        title_parts = []
                        if i > 0:
                            title_parts.append(words[i-1])
                        title_parts.append(word)
                        if i < len(words) - 1:
                            title_parts.append(words[i+1])
                        
                        updated_context['jobTitle'] = ' '.join(title_parts).title()
                        break
                if updated_context.get('jobTitle'):
                    break
    
    # Extract company info
    if 'company' in message_lower or 'organization' in message_lower:
        words = user_message.split()
        for i, word in enumerate(words):
            if word.lower() in ['company', 'organization', 'startup', 'corporation']:
                if i > 0:
                    updated_context['company'] = words[i-1]
                break
    
    # Handle company overview from predefined profiles
    if 'company overview:' in user_message.lower():
        # Extract company overview from message
        overview_start = user_message.lower().find('company overview:')
        if overview_start != -1:
            overview_text = user_message[overview_start + len('company overview:'):].strip()
            # Extract until benefits section if present
            benefits_start = overview_text.lower().find('our benefits include:')
            if benefits_start != -1:
                updated_context['companyOverview'] = overview_text[:benefits_start].strip()
                # Extract benefits
                benefits_text = overview_text[benefits_start + len('our benefits include:'):].strip()
                updated_context['benefits'] = [benefits_text]
            else:
                updated_context['companyOverview'] = overview_text
    
    # Extract benefits information from user message
    if 'benefits include:' in user_message.lower() or 'benefit' in user_message.lower():
        benefits_start = user_message.lower().find('benefits include:')
        if benefits_start != -1:
            benefits_text = user_message[benefits_start + len('benefits include:'):].strip()
            if 'benefits' not in updated_context:
                updated_context['benefits'] = []
            updated_context['benefits'].append(benefits_text)
    
    # Handle benefits updates from AI response (when user asks to change benefits)
    if ('change' in message_lower or 'update' in message_lower or 'revise' in message_lower) and 'benefit' in message_lower:
        # Look for updated benefits in AI response
        import re
        
        # Clean the AI response to handle formatting
        ai_clean = re.sub(r'[*\-•]', '', ai_response)  # Remove bullet points and formatting
        ai_clean = re.sub(r'\s+', ' ', ai_clean)  # Normalize whitespace
        
        # Multiple patterns to find updated benefits
        patterns = [
            r'benefit(?:s?)\s*cuti\s*(\d+)\s*(?:hari|days?)',  # "Benefit cuti X hari"
            r'(\d+)\s*(?:hari|days?)\s*(?:of\s*)?(?:leave|cuti)',  # "X days of leave" or "X hari cuti"
            r'benefit(?:s?).*?(\d+)\s*(?:hari|days?)',  # "Benefits... X days"
            r'cuti\s*(\d+)\s*(?:hari|days?)',  # "cuti X hari"
            r'(\d+)\s*(?:hari|days?)',  # Just "X hari" or "X days"
        ]
        
        benefit_match = None
        days = None
        
        # Try patterns on cleaned AI response
        for pattern in patterns:
            benefit_match = re.search(pattern, ai_clean.lower())
            if benefit_match:
                days = benefit_match.group(1)
                print(f"DEBUG: Found benefits match with pattern '{pattern}': {days} days")
                break
        
        # If no pattern match, try to extract from Benefits section
        if not days and 'benefits:' in ai_lower:
            benefits_start = ai_response.lower().find('benefits:')
            if benefits_start != -1:
                # Extract the benefits section
                benefits_section = ai_response[benefits_start:].split('\n\n')[0]  # Get until next section
                print(f"DEBUG: Benefits section extracted: {benefits_section}")
                
                # Look for days in this section
                for pattern in patterns:
                    section_match = re.search(pattern, benefits_section.lower())
                    if section_match:
                        days = section_match.group(1)
                        print(f"DEBUG: Found days in benefits section: {days}")
                        break
        
        # If we found days, update the context
        if days:
            new_benefits = f"Benefit cuti {days} hari, BPJS, THR, Diskon karyawan"
            updated_context['benefits'] = [new_benefits]
            print(f"DEBUG: Updated benefits to: {new_benefits}")
        else:
            print(f"DEBUG: No days found in AI response. AI response: {ai_response[:500]}...")
            
            # Try to extract the entire benefits line if formatted properly
            if 'benefit cutix' in ai_lower:
                # Find lines containing "benefit cuti"
                lines = ai_response.split('\n')
                for line in lines:
                    if 'benefit cuti' in line.lower():
                        # Clean the line and use it
                        clean_line = re.sub(r'^[*\-•\s]*', '', line).strip()
                        if clean_line:
                            updated_context['benefits'] = [clean_line]
                            print(f"DEBUG: Extracted entire benefits line: {clean_line}")
                            break
    
    # Also check for any benefits information in AI response (not just when user asks for changes)
    if 'benefit' in ai_lower and 'cuti' in ai_lower:
        import re
        
        # Clean the AI response to handle formatting
        ai_clean = re.sub(r'[*\-•]', '', ai_response)  # Remove bullet points and formatting
        ai_clean = re.sub(r'\s+', ' ', ai_clean)  # Normalize whitespace
        
        # Look for benefit cuti pattern
        patterns = [
            r'benefit(?:s?)\s*cuti\s*(\d+)\s*(?:hari|days?)',  # "Benefit cuti X hari"
            r'cuti\s*(\d+)\s*(?:hari|days?)',  # "cuti X hari"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, ai_clean.lower())
            if match:
                days = match.group(1)
                new_benefits = f"Benefit cuti {days} hari, BPJS, THR, Diskon karyawan"
                updated_context['benefits'] = [new_benefits]
                print(f"DEBUG: General benefits extraction - Updated to: {new_benefits}")
                break
    
    # Extract experience requirements
    if 'year' in message_lower and ('experience' in message_lower or 'exp' in message_lower):
        import re
        exp_match = re.search(r'(\d+)[-\s]?(?:to|-)?[\s]?(\d+)?\s*years?', message_lower)
        if exp_match:
            if exp_match.group(2):
                updated_context['experience'] = f"{exp_match.group(1)}-{exp_match.group(2)} years"
            else:
                updated_context['experience'] = f"{exp_match.group(1)}+ years"
    
    # Extract skills mentioned
    common_skills = ['python', 'javascript', 'react', 'node.js', 'sql', 'aws', 'docker', 'kubernetes',
                    'machine learning', 'data analysis', 'excel', 'powerbi', 'tableau', 'figma', 'photoshop']
    
    for skill in common_skills:
        if skill in message_lower and skill not in updated_context.get('skills', []):
            if 'skills' not in updated_context:
                updated_context['skills'] = []
            updated_context['skills'].append(skill.title())
    
    return updated_context

def should_generate_job_description(context, ai_response):
    """Determine if we have enough information to generate a job description"""
    # Check if AI response suggests generating or if we have sufficient context
    generate_keywords = ['generate', 'create', 'draft', 'complete job description', 'ready to create', 
                        'job description', 'here\'s the job description', 'here is the job description',
                        'job posting', 'create the job', 'draft the job', 'write the job', 'final job description']
    
    ai_suggests_generate = any(keyword in ai_response.lower() for keyword in generate_keywords)
    
    # Check if we have minimum required information
    has_job_title = bool(context.get('jobTitle'))
    has_some_info = bool(context.get('skills') or context.get('experience') or context.get('company'))
    
    # Also generate if the AI response is longer than 200 chars and mentions job description
    is_comprehensive_response = len(ai_response) > 200 and 'job description' in ai_response.lower()
    
    # Generate if AI suggests it OR if we have good info and it's a comprehensive response
    return (ai_suggests_generate and has_job_title) or (has_job_title and has_some_info and is_comprehensive_response)

def generate_complete_job_description(context):
    """Generate a complete job description based on context"""
    try:
        # Build the prompt with available context
        company_info = ""
        if context.get('companyOverview'):
            company_info += f"Company Overview: {context.get('companyOverview')}\n"
        if context.get('benefits'):
            benefits_text = context.get('benefits')[0] if isinstance(context.get('benefits'), list) else context.get('benefits')
            company_info += f"Benefits: {benefits_text}\n"
        
        prompt = f"""Based on the following information, create a comprehensive, professional job description:

Job Title: {context.get('jobTitle', 'Position')}
Company: {context.get('company', 'Our Company')}
Department: {context.get('department', '')}
Experience Required: {context.get('experience', '')}
Skills: {', '.join(context.get('skills', []))}
Requirements mentioned: {', '.join(context.get('requirements', []))}
Responsibilities mentioned: {', '.join(context.get('responsibilities', []))}

{company_info}

Create a complete job description with:
1. Job Title
2. Company Overview (use the provided company overview if available)
3. Job Summary/Overview
4. Key Responsibilities (5-8 bullet points)
5. Required Qualifications
6. Preferred Qualifications
7. What We Offer (use the provided benefits if available, otherwise use generic benefits)

Make it professional, engaging, and comprehensive. Format it properly with clear sections. If company overview is provided, use it prominently in the job description."""

        # Debug logging for job description generation
        print("\n" + "="*80)
        print("JOB DESCRIPTION GENERATION PROMPT:")
        print("="*80)
        print(f"Context benefits: {context.get('benefits')}")
        print(f"Company info section: {company_info}")
        print("Full prompt:")
        print(prompt)
        print("="*80)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.7
        )
        
        generated_jd = response.choices[0].message.content.strip()
        
        # Debug logging for generated result
        print("\n" + "="*80)
        print("GENERATED JOB DESCRIPTION:")
        print("="*80)
        print(generated_jd)
        print("="*80)
        
        return generated_jd
        
    except Exception as e:
        print(f"Error generating job description: {str(e)}")
        return None

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