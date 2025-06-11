import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
import PyPDF2
import docx
import pandas as pd
import json
# Remove streamlit-elements import
# from streamlit_elements import elements, mui
from jd_analyzer import analyze_job_description, format_requirements_for_display, parse_edited_requirements
from resume_analyzer import analyze_resume

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize session state for API key verification
# Auto-apply API key from .env file
api_key_from_env = os.getenv("OPENAI_API_KEY")
if 'api_key_verified' not in st.session_state:
    st.session_state.api_key_verified = bool(api_key_from_env)
if 'api_key_value' not in st.session_state:
    st.session_state.api_key_value = api_key_from_env or ""

# Initialize other session states
if "requirements" not in st.session_state:
    st.session_state.requirements = None
if "job_description" not in st.session_state:
    st.session_state.job_description = None
if "formatted_reqs" not in st.session_state:
    st.session_state.formatted_reqs = None
if "selected_models" not in st.session_state:
    st.session_state.selected_models = {"primary": "gpt-4.1", "reasoning": "o4-mini"}

def extract_text_from_pdf(pdf_file):
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
    print(f"EXTRACTED PDF TEXT FROM: {pdf_file.name}")
    print("="*80)
    print(f"Total text length: {len(text)} characters")
    print("First 1000 characters:")
    print(text[:1000] + "..." if len(text) > 1000 else text)
    print("="*80)
    
    return text

def extract_text_from_docx(docx_file):
    doc = docx.Document(docx_file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def process_file(file):
    if file.name.endswith('.pdf'):
        return extract_text_from_pdf(file)
    elif file.name.endswith('.docx'):
        return extract_text_from_docx(file)
    else:
        return file.getvalue().decode('utf-8')

def create_collapsible_section(header, content):
    """Create a collapsible section using HTML and JavaScript"""
    # Generate a unique ID for this section
    import random
    import string
    section_id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    
    html = f"""
        <div style="margin: 10px 0;">
            <button type="button" style="background-color: #262730; color: #fff; border: 1px solid #555; padding: 5px 10px; cursor: pointer; width: 100%; text-align: left; border-radius: 4px;"
                    onclick="toggleSection_{section_id}()">
                ▼ {header}
            </button>
            <div id="section_{section_id}" style="display: none; margin-left: 20px; margin-top: 8px;">
                {content}
            </div>
        </div>
        <script>
            function toggleSection_{section_id}() {{
                var content = document.getElementById('section_{section_id}');
                var button = content.previousElementSibling;
                if (content.style.display === 'none') {{
                    content.style.display = 'block';
                    button.innerHTML = button.innerHTML.replace('▼', '▲');
                }} else {{
                    content.style.display = 'none';
                    button.innerHTML = button.innerHTML.replace('▲', '▼');
                }}
            }}
        </script>
    """
    return html

def create_details_element(summary, content):
    """Create a custom HTML details element with styling"""
    return f"""
        <style>
            details {{
                background: #1E1E1E;
                padding: 10px;
                margin: 5px 0;
                border-radius: 4px;
                border: 1px solid #333;
            }}
            details summary {{
                cursor: pointer;
                padding: 5px;
                font-weight: bold;
                color: #FFFFFF;
            }}
            details summary:hover {{
                background: #2E2E2E;
                border-radius: 4px;
            }}
            .details-content {{
                margin-top: 10px;
                padding: 10px;
                background: #262630;
                border-radius: 4px;
            }}
            .checkmark {{
                color: #28a745;
            }}
            .cross {{
                color: #dc3545;
            }}
        </style>
        <details>
            <summary>{summary}</summary>
            <div class="details-content">
                {content}
            </div>
        </details>
    """

def display_simple_minimal_requirements(analysis):
    """Display requirements using custom HTML details elements"""
    req_match = analysis.get("requirement_match", {})
    must_have = req_match.get("must_have_requirements", {})
    good_to_have = req_match.get("good_to_have_requirements", {})
    screening = req_match.get("additional_screening_criteria", {})

    st.subheader("Requirements Match Summary")
    
    # --- Must-Have Section --- 
    st.markdown("<h4><b>Must-Have</b></h4>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        tech_skills = must_have.get("technical_skills", {})
        true_count = sum(1 for v in tech_skills.values() if v is True)
        total = len(tech_skills)
        value_str = f"{true_count}/{total}" if total > 0 else "N/A"
        
        # Create content for technical skills
        content = "<br>".join([
            f"<span class='{'checkmark' if met else 'cross'}'>{('✓' if met else '✗')}</span> {skill}" 
            for skill, met in tech_skills.items()
        ])
        summary = f"Technical Skills: {value_str}"
        st.markdown(create_details_element(summary, content), unsafe_allow_html=True)
                
    with col2:
        core_resp = must_have.get("core_responsibilities", {})
        true_count = sum(1 for v in core_resp.values() if v is True)
        total = len(core_resp)
        value_str = f"{true_count}/{total}" if total > 0 else "N/A"
        
        # Create content for core responsibilities
        content = "<br>".join([
            f"<span class='{'checkmark' if met else 'cross'}'>{('✓' if met else '✗')}</span> {resp}" 
            for resp, met in core_resp.items()
        ])
        summary = f"Core Responsibilities: {value_str}"
        st.markdown(create_details_element(summary, content), unsafe_allow_html=True)
                
    # --- Experience & Qualifications --- 
    col_exp, col_qual = st.columns(2)
    with col_exp:
        exp_met = must_have.get("experience", None)
        exp_status = '✓ Met' if exp_met is True else ('✗ Not Met' if exp_met is False else 'N/A')
        st.markdown(f"<span style='font-size: 1.1em; font-weight: 600;'>Experience:</span> <span class='{'checkmark' if exp_met else 'cross'}'>{exp_status}</span>", unsafe_allow_html=True)
    with col_qual:
        qual_met = must_have.get("qualifications", None)
        qual_status = '✓ Met' if qual_met is True else ('✗ Not Met' if qual_met is False else 'N/A')
        st.markdown(f"<span style='font-size: 1.1em; font-weight: 600;'>Qualifications:</span> <span class='{'checkmark' if qual_met else 'cross'}'>{qual_status}</span>", unsafe_allow_html=True)
    
    # --- Good-to-Have & Screening Section --- 
    st.markdown("<h4><b>Good-to-Have & Screening</b></h4>", unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    with col3:
        add_skills = good_to_have.get("additional_skills", {})
        true_count = sum(1 for v in add_skills.values() if v is True)
        total = len(add_skills)
        value_str = f"{true_count}/{total}" if total > 0 else "N/A"
        
        # Create content for additional skills
        content = "<br>".join([
            f"<span class='{'checkmark' if met else 'cross'}'>{('✓' if met else '✗')}</span> {skill}" 
            for skill, met in add_skills.items()
        ])
        summary = f"Additional Skills: {value_str}"
        st.markdown(create_details_element(summary, content), unsafe_allow_html=True)
                
    with col4:
        true_count = sum(1 for v in screening.values() if v is True)
        total = len(screening)
        value_str = f"{true_count}/{total}" if total > 0 else "N/A"
        
        # Create content for screening criteria
        content = "<br>".join([
            f"<span class='{'checkmark' if met else 'cross'}'>{('✓' if met else '✗')}</span> {crit}" 
            for crit, met in screening.items()
        ])
        summary = f"Screening Criteria: {value_str}"
        st.markdown(create_details_element(summary, content), unsafe_allow_html=True)

def display_requirement_matches(matches):
    st.subheader("Requirement Matches")
    st.json(matches)

def display_qualitative_assessment(assessment):
    # Define mapping from qualitative labels to numerical values 
    qualitative_map = {
        "very low": 10,
        "low": 25,
        "moderate": 50,
        "medium": 50,
        "medium-high": 65,
        "high": 85,
        "very high": 95,
        "strong": 85, 
        "n/a": 0,
        None: 0
    }
    
    # Define mapping from numerical ranges/categories to colors
    color_map = {
        "high": "#28a745", # Green
        "mid": "#ffc107", # Yellow
        "low": "#dc3545", # Red
        "n/a": "#6c757d" # Grey
    }
    
    # Helper function to get category from value
    def get_category(value):
        num_val = qualitative_map.get(value.lower().replace(" ", "-").strip(), 0)
        if num_val >= 75: return "high"
        if num_val >= 40: return "mid"
        if num_val > 0: return "low"
        return "n/a"

    # Fields to display as meters - Update label here
    meter_fields = {
        "project_gravity": "Project Gravity",
        "ownership_and_initiative": "Ownership & Initiative",
        "transferability_to_role": "Fit for Role" # Changed Label
    }
    
    st.markdown("<h5><b>Qualitative Factors</b></h5>", unsafe_allow_html=True)
    
    # Create columns for horizontal layout
    cols = st.columns(len(meter_fields))
    
    # Iterate and place each factor in a column
    for i, (key, label) in enumerate(meter_fields.items()):
        value_str = assessment.get(key, "N/A")
        category = get_category(value_str)
        color = color_map.get(category, "#6c757d")
        text_color = "#ffffff" if category != "n/a" else "#212529"
        
        badge_text = category.capitalize() if category != "n/a" else "N/A"
        badge_html = f"<span style='background-color: {color}; color: {text_color}; padding: 3px 8px; border-radius: 5px; font-size: 0.9em; font-weight: 600;'>{badge_text}</span>"
        
        # Place the markdown in the corresponding column
        with cols[i]:
            st.markdown(f"<span style='font-size: 0.9em; font-weight: 600;'>{label}:</span> {badge_html}", unsafe_allow_html=True)

    # Add some space below the horizontal factors before strengths/weaknesses
    st.write("") 

    # Displaying strengths/weaknesses (keep as before)
    if "strengths" in assessment:
        st.markdown("<span style='font-size: 0.9em; font-weight: 600;'>Strengths:</span>", unsafe_allow_html=True)
        for strength in assessment["strengths"]:
             st.markdown(f"<span style='font-size: 0.9em;'>- {strength}</span>", unsafe_allow_html=True)
             
    if "weaknesses" in assessment:
        st.markdown("<span style='font-size: 0.9em; font-weight: 600;'>Weaknesses:</span>", unsafe_allow_html=True)
        for weakness in assessment["weaknesses"]:
             st.markdown(f"<span style='font-size: 0.9em;'>- {weakness}</span>", unsafe_allow_html=True)

def display_requirement_progress(section, title, key):
    """Display requirement progress as a bar or list of checkmarks."""
    if key == "screening":
        # Handle the special case for screening criteria
        items = section.get(key, {})
    else:
        items = section.get(key, {})
    
    if not items:
        st.write(f"**{title}**: No data available")
        return
        
    true_count = sum(1 for v in items.values() if v is True)
    total = len(items)
    
    # Display header with count
    st.write(f"**{title}**: {true_count}/{total}")
    
    # Display individual items with checkmarks
    for item, met in items.items():
        st.write(f"{'✅' if met else '❌'} {item}")

def format_requirements_for_editing(requirements):
    must_have = []
    if "must_have_requirements" in requirements:
        must = requirements["must_have_requirements"]
        must_have.append("Technical Skills:")
        must_have.extend([f"- {skill}" for skill in must.get("technical_skills", [])])
        must_have.append("\nExperience:")
        must_have.append(f"- {must.get('experience', '')}")
        must_have.append("\nQualifications:")
        must_have.extend([f"- {qual}" for qual in must.get("qualifications", [])])
        must_have.append("\nCore Responsibilities:")
        must_have.extend([f"- {resp}" for resp in must.get("core_responsibilities", [])])
    
    preferred = []
    if "good_to_have_requirements" in requirements:
        good = requirements["good_to_have_requirements"]
        preferred.append("Additional Skills:")
        preferred.extend([f"- {skill}" for skill in good.get("additional_skills", [])])
        preferred.append("\nExtra Qualifications:")
        preferred.extend([f"- {qual}" for qual in good.get("extra_qualifications", [])])
        preferred.append("\nBonus Experience:")
        preferred.extend([f"- {exp}" for exp in good.get("bonus_experience", [])])
    
    additional = []
    if "additional_screening_criteria" in requirements:
        additional.extend([f"- {criteria}" for criteria in requirements["additional_screening_criteria"]])
    
    return {
        "must_have": "\n".join(must_have),
        "preferred": "\n".join(preferred),
        "additional": "\n".join(additional)
    }

def calculate_percentage(score):
    """Convert score like '10/21' to percentage"""
    try:
        numerator, denominator = map(int, score.split('/'))
        percentage = (numerator / denominator) * 100
        return round(percentage)
    except:
        return 0

def calculate_quantitative_percentage(score):
    """Convert quantitative score like '10/21' to percentage"""
    try:
        numerator, denominator = map(int, score.split('/'))
        percentage = (numerator / denominator) * 100
        return round(percentage)
    except:
        return 0

def display_contact_info(contact_info):
    """Display candidate contact information in a clean format"""
    # Display name in larger font with custom styling
    if contact_info.get("full_name"):
        st.markdown(f"""
            <div style='margin-bottom: 15px;'>
                <h2 style='margin: 0; color: #1E88E5; font-size: 24px; font-weight: 600;'>
                    {contact_info['full_name']}
                </h2>
            </div>
        """, unsafe_allow_html=True)
    
    # Create a clean two-column layout for contact info with consistent styling
    col1, col2 = st.columns(2)
    
    # Define the style for info labels and values with lighter colors for dark mode
    info_style = """
        <div style='margin-bottom: 8px;'>
            <span style='color: #9AA0A6; font-size: 13px; font-weight: 500;'>{label}:</span>
            <span style='color: #FFFFFF; font-size: 14px; margin-left: 4px;'>{value}</span>
        </div>
    """
    
    with col1:
        if contact_info.get("email"):
            st.markdown(info_style.format(
                label="Email",
                value=f"<a href='mailto:{contact_info['email']}' style='color: #8AB4F8;'>{contact_info['email']}</a>"
            ), unsafe_allow_html=True)
        if contact_info.get("phone"):
            st.markdown(info_style.format(
                label="Phone",
                value=contact_info['phone']
            ), unsafe_allow_html=True)
        if contact_info.get("age") and contact_info['age'] != "N/A":
            st.markdown(info_style.format(
                label="Age",
                value=contact_info['age']
            ), unsafe_allow_html=True)
        if contact_info.get("gender") and contact_info['gender'] != "N/A":
            st.markdown(info_style.format(
                label="Gender",
                value=contact_info['gender']
            ), unsafe_allow_html=True)
            
    with col2:
        if contact_info.get("location"):
            st.markdown(info_style.format(
                label="Location",
                value=contact_info['location']
            ), unsafe_allow_html=True)
        if contact_info.get("linkedin") and contact_info['linkedin'] != "N/A":
            st.markdown(info_style.format(
                label="LinkedIn",
                value=f"<a href='{contact_info['linkedin']}' target='_blank' style='color: #8AB4F8;'>Profile ↗</a>"
            ), unsafe_allow_html=True)
        if contact_info.get("total_work_experience"):
            st.markdown(info_style.format(
                label="Total Experience",
                value=contact_info['total_work_experience']
            ), unsafe_allow_html=True)
        if contact_info.get("last_position"):
            st.markdown(info_style.format(
                label="Last Position",
                value=contact_info['last_position']
            ), unsafe_allow_html=True)
        
    # Display other links if present
    if contact_info.get("other_links") and len(contact_info["other_links"]) > 0:
        st.markdown("<div style='margin-top: 10px;'>", unsafe_allow_html=True)
        st.markdown("""
            <span style='color: #9AA0A6; font-size: 13px; font-weight: 500;'>Other Profiles:</span>
        """, unsafe_allow_html=True)
        for link in contact_info["other_links"]:
            st.markdown(f"""
                <div style='margin-left: 10px; font-size: 14px;'>
                    <a href='https://{link}' target='_blank' style='color: #8AB4F8;'>• {link} ↗</a>
                </div>
            """, unsafe_allow_html=True)

def flatten_analysis_for_csv(analysis):
    """Flatten the analysis JSON for CSV with specific columns"""
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

# Main page title
st.title("Resume Ranking System")

# API Key Verification Section
st.header("🔐 API Key Verification")

# If API key is loaded from .env, skip verification UI
if st.session_state.api_key_verified and api_key_from_env:
    st.success("✅ API Key loaded from environment and active")
    if st.button("Change API Key", key="change_api_key_btn"):
        st.session_state.api_key_verified = False
        st.session_state.api_key_value = ""
        st.rerun()
elif not st.session_state.api_key_verified:
    # Keep the API key input field enabled
    api_key = st.text_input("Enter your OpenAI API Key", 
                           type="password", 
                           key="api_key_input",
                           value=st.session_state.api_key_value)
    
    if st.button("Verify API Key", key="verify_api_key_btn"):
        if api_key:
            try:
                # Try to create a client and make a simple API call
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Test"}],
                    max_tokens=5
                )
                # If no error, key is valid
                st.session_state.api_key_verified = True
                st.session_state.api_key_value = api_key
                os.environ["OPENAI_API_KEY"] = api_key  # Set the API key
                st.success("✅ API Key verified successfully!")
                st.rerun()
            except Exception as e:
                st.error("❌ Invalid API Key. Please check and try again.")
        else:
            st.warning("⚠️ Please enter an API Key.")
    
    # Show the rest of the app but disable functionality
    st.warning("⚠️ Please enter a valid API key to enable all features.")
    st.divider()
    
    # Model Selection Section (disabled)
    st.header("Model Selection")
    st.selectbox(
        "Choose the primary model (general purpose)",
        ["gpt-4.1", "gpt-4.0", "gpt-3.5-turbo"],
        disabled=True,
        key="disabled_model_1"
    )
    st.selectbox(
        "Choose a reasoning-focused model",
        ["o4-mini", "o1-mini", "o1-preview"],
        disabled=True,
        key="disabled_model_2"
    )
    st.button("Update Models", disabled=True, key="disabled_update_models")
    
    st.divider()
    
    # Job Description Section (disabled)
    st.header("Job Description Analysis")
    st.text_area("Enter Job Description:", height=200, disabled=True, key="disabled_job_desc")
    st.button("Analyze Job Description", disabled=True, key="disabled_analyze_jd")
    
    st.divider()
    
    # Resume Analysis Section (disabled)
    st.header("Resume Analysis")
    st.file_uploader("Upload Resumes (PDF, DOCX, or TXT)", 
                    accept_multiple_files=True,
                    disabled=True,
                    key="disabled_file_upload")
    st.button("Analyze Resumes", disabled=True, key="disabled_analyze_resumes")
    
    st.stop()  # Stop here if not verified

st.divider()

# Model Selection Section
st.header("Model Selection")

model_1 = st.selectbox(
    "Choose the primary model (general purpose)",
    ["gpt-4.1", "gpt-4.0", "gpt-3.5-turbo"],
    key="primary_model_select"
)

model_2 = st.selectbox(
    "Choose a reasoning-focused model",
    ["o4-mini", "o1-mini", "o1-preview"],
    key="reasoning_model_select"
)

if st.button("Update Models", key="update_models_btn"):
    st.session_state.selected_models = {
        "primary": model_1,
        "reasoning": model_2
    }
    st.success("✅ Models updated successfully!")

st.divider()

# Job Description Section
st.header("Job Description Analysis")

# Keep job description input visible
job_description = st.text_area("Enter Job Description:", 
                          value=st.session_state.job_description if st.session_state.job_description else "",
                          height=200,
                          key="job_description_input")

if st.button("Analyze Job Description", key="analyze_jd_btn"):
    if not job_description:
        st.error("Please provide a job description.")
    else:
        with st.spinner("Analyzing job description..."):
            requirements = analyze_job_description(job_description, model=st.session_state.selected_models["primary"])
            
            if requirements:
                st.session_state.job_description = job_description
                formatted_reqs = format_requirements_for_editing(requirements)
                st.session_state.formatted_reqs = formatted_reqs
                st.session_state.requirements = requirements
                st.success("✅ Job requirements have been extracted and saved!")
            else:
                st.error("Failed to analyze job description. Please try again.")

# Show requirements fields only if they exist
if st.session_state.formatted_reqs:
    st.subheader("Edit Requirements")
    must_have_edit = st.text_area("Must-Have Requirements:", 
                       value=st.session_state.formatted_reqs["must_have"],
                       height=200,
                       key="must_have_edit")
    preferred_edit = st.text_area("Preferred Requirements:", 
                       value=st.session_state.formatted_reqs["preferred"],
                       height=200,
                       key="preferred_edit")
    additional_edit = st.text_area("Additional Screening Criteria:", 
                        value=st.session_state.formatted_reqs["additional"],
                        height=200,
                        key="additional_edit")
    
    if st.button("Update Requirements", key="update_requirements_btn"):
        edited_requirements = parse_edited_requirements(must_have_edit, preferred_edit, additional_edit)
        if edited_requirements:
            edited_requirements["original_job_description"] = st.session_state.job_description
            st.session_state.requirements = edited_requirements
            st.session_state.formatted_reqs = format_requirements_for_editing(edited_requirements)
            st.success("✅ Requirements updated successfully!")
            st.rerun()

st.divider()

# Resume Analysis Section
if st.session_state.requirements is not None:
    st.header("Resume Analysis")
    uploaded_files = st.file_uploader("Upload Resumes (PDF, DOCX, or TXT)", 
                                    accept_multiple_files=True,
                                    key="resume_file_upload")
    
    if uploaded_files and st.button("Analyze Resumes", key="analyze_resumes_btn"):
        # Initialize session state for results if not exists
        if 'resume_results' not in st.session_state:
            st.session_state.resume_results = []
            st.session_state.csv_data = []
        else:
            # Clear previous results when starting new analysis
            st.session_state.resume_results = []
            st.session_state.csv_data = []
        
        # Create status section
        st.markdown("### 📊 Analyzing Resumes...")
        progress_bar = st.progress(0)
        
        total_files = len(uploaded_files)
        
        # Create one results section that will be updated
        results_section = st.container()
        
        for idx, file in enumerate(uploaded_files, 1):
            with st.spinner(f"Analyzing {file.name}..."):
                resume_text = process_file(file)
                
                # Log the processed text for debugging
                print("\n" + "="*80)
                print(f"PROCESSED TEXT FOR AI ANALYSIS - FILE: {file.name}")
                print("="*80)
                print(f"Text length: {len(resume_text)} characters")
                print("First 500 characters:")
                print(resume_text[:500])
                print("="*80)
                
                analysis = analyze_resume(resume_text, st.session_state.requirements, model=st.session_state.selected_models["reasoning"])
                
                if analysis:
                    # Calculate both percentage scores
                    quantitative_percentage = calculate_quantitative_percentage(analysis['quantitative_score'])
                    semantic_percentage = analysis.get('semantic_score', 0)
                    
                    # Store results
                    result = {
                        'filename': file.name,
                        'quantitative_percentage': quantitative_percentage,
                        'semantic_percentage': semantic_percentage,
                        'percentage': semantic_percentage,  # Use semantic as main percentage
                        'quantitative_score': analysis['quantitative_score'],
                        'semantic_score': analysis['semantic_score'],
                        'score': analysis['score'],  # Keep for backward compatibility
                        'analysis': analysis['analysis']
                    }
                    st.session_state.resume_results.append(result)
                    
                    # Flatten and store data for CSV
                    flattened_data = flatten_analysis_for_csv(analysis['analysis'])
                    flattened_data['filename'] = file.name
                    flattened_data['quantitative_percentage'] = quantitative_percentage
                    flattened_data['semantic_percentage'] = semantic_percentage
                    flattened_data['percentage'] = semantic_percentage  # Use semantic as main percentage
                    st.session_state.csv_data.append(flattened_data)
                    
                    # Update progress
                    progress_bar.progress(idx / total_files)
                    
                    # Display result in the single results section
                    with results_section:
                        with st.expander(f"{file.name} - {semantic_percentage}% (Semantic: {semantic_percentage}% | Quantitative: {quantitative_percentage}%)", expanded=True):
                            # Display contact information first
                            if 'contact_info' in analysis['analysis']:
                                # Debug: Print contact info to console
                                print(f"\n--- CONTACT INFO FOR {file.name} ---")
                                print(json.dumps(analysis['analysis']['contact_info'], indent=2))
                                print("--- END CONTACT INFO ---")
                                
                                display_contact_info(analysis['analysis']['contact_info'])
                                st.divider()
                            else:
                                print(f"\n--- NO CONTACT INFO FOUND FOR {file.name} ---")
                                st.warning("⚠️ No contact information could be extracted from this resume.")
                            
                            # Display requirements match
                            display_simple_minimal_requirements(analysis['analysis'])
                            
                            # Display other parts 
                            st.divider() 
                            display_qualitative_assessment(analysis['analysis']['qualitative_assessment'])
                            
                            # Display Recruiter Summary if available (without title)
                            if 'qualitative_assessment' in analysis['analysis'] and 'recruiter_style_summary' in analysis['analysis']['qualitative_assessment']:
                                st.write("")
                                st.write(analysis['analysis']['qualitative_assessment']['recruiter_style_summary'])
                                st.divider()
                            
                            st.subheader("Final Recommendation")
                            st.write(analysis['analysis']['final_recommendation'])
                            
                            st.subheader("Reason for Recommendation") 
                            for factor in analysis['analysis']['summary_of_key_factors']:
                                st.write(f"- {factor}")
                            st.divider()
        
        # Clear the progress bar and show completion
        progress_bar.empty()
        st.success("✅ All resumes processed!")
        
        # Show CSV download button after all processing is complete
        if st.session_state.csv_data:
            df = pd.DataFrame(st.session_state.csv_data)
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Complete Analysis Results as CSV",
                data=csv,
                file_name="resume_analysis_results.csv",
                mime="text/csv",
            )