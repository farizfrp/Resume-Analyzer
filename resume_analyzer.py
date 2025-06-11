import json
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_resume(resume_text, requirements, model="o4-mini"):
    """
    Analyzes a resume against the structured requirements from the JD analyzer.
    Returns a comprehensive analysis including quantitative matches and qualitative assessment.
    
    Args:
        resume_text (str): The text content of the resume
        requirements (dict): The JSON output from the JD analyzer containing:
            - original_job_description
            - must_have_requirements
            - good_to_have_requirements
            - additional_screening_criteria
        model (str): The OpenAI model to use for analysis
    """
    try:
        # Format the requirements for the prompt
        requirements_str = f"""
Original Job Description:
{requirements.get('original_job_description', '')}

Must-Have Requirements:
{json.dumps(requirements.get('must_have_requirements', {}), indent=2)}

Good-to-Have Requirements:
{json.dumps(requirements.get('good_to_have_requirements', {}), indent=2)}

Additional Screening Criteria:
{json.dumps(requirements.get('additional_screening_criteria', []), indent=2)}
"""
        
        # Debug: Log the requirements being used
        print("\n" + "="*80)
        print("JOB REQUIREMENTS BEING USED FOR ANALYSIS:")
        print("="*80)
        print(requirements_str)
        print("="*80)
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": """You are a recruiter evaluating a candidate's resume against a given job description (JD). Based on the JD, evaluate whether the candidate meets the necessary requirements.

                    ## Step 0: Contact Information Extraction
                    First, extract all available contact information from the resume:
                    - **Full Name**: Extract the candidate's complete name
                    - **Email**: Extract email address if available
                    - **Phone**: Extract phone number if available  
                    - **Location**: Extract current location/address if available
                    - **LinkedIn**: Extract LinkedIn profile URL if available
                    - **Other Links**: Extract any other social media profiles, portfolio links, GitHub, etc.
                    - **Age**: Extract or infer age if mentioned (use "N/A" if not available)
                    - **Gender**: Extract or infer gender if mentioned (use "N/A" if not available)
                    - **Total Work Experience**: Calculate total years of professional work experience based on employment history
                    - **Last Position**: Extract the most recent job title and company name

                    ## Step 1: Quantitative Check
                    Perform a Boolean (true/false) check for each requirement based on the candidate's resume:

                    - For each skill listed in `must_have_requirements` and `good_to_have_requirements`, determine if the candidate possesses it. Return true or false for each.
                    - For each `core_responsibility`, determine if the candidate has demonstrated SIMILAR or RELATED experience in their past work. Be flexible - if they have done something similar or transferable, mark it as true. Don't require exact word-for-word matches.
                    - For each `additional_screening_criteria`, return a boolean value indicating whether the candidate meets the condition (e.g., full-time, onsite position, work authorization, etc.).
                    
                    **Important**: Be generous in matching core responsibilities. If a candidate has done mobile development, API integration, or similar work, consider it a match even if the exact wording is different.

                    ## Step 2: Qualitative Assessment
                    Now, switch to a recruiter-style qualitative assessment. Use your **intuition like a human** — go beyond what's explicitly stated. Read between the lines, infer intent, and use contextual clues from the resume and the JD to judge fit. Reference the results from Step 1 as part of your reasoning.

                    Assess the following:

                    - **Inferred Skills**: What skills can you infer from the candidate's projects or roles?
                    - **Project Gravity**: Were the projects academic or real-world, high-impact, production-ready, etc.?
                    - **Ownership and Initiative**: Did the candidate lead the work? Show initiative? Or just follow directions?
                    - **Transferability to Role**: How well would their experience transfer to this particular role? Will they onboard quickly?
                    - **Bonus Experience & Extra Qualifications**: If the JD lists any bonus criteria (e.g., fintech, B2B SaaS), consider that a positive signal even if not part of Step 1.

                    ## Step 3: Final Recommendation
                    After both steps, make a final call. Output "Yes" or "No" and summarize your reasoning concisely.

                    ---

                    ### Output Format (strictly follow this JSON structure):

                    {
                    "contact_info": {
                        "full_name": "John Doe",
                        "email": "john.doe@email.com",
                        "phone": "+1-555-123-4567",
                        "location": "San Francisco, CA",
                        "linkedin": "https://linkedin.com/in/johndoe",
                        "other_links": ["github.com/johndoe", "portfolio.johndoe.com"],
                        "age": "28",
                        "gender": "Male",
                        "total_work_experience": "5 years",
                        "last_position": "Senior Software Engineer at Tech Corp"
                    },
                    "requirement_match": {
                        "must_have_requirements": {
                        "technical_skills": {
                            "JavaScript": true,
                            "React.js": true,
                            "Node.js": true,
                            "SQL databases (especially PostgreSQL)": true,
                            "Version control systems (e.g., Git)": true
                        },
                        "experience": true,
                        "qualifications": true,
                        "core_responsibilities": {
                            "Build and maintain scalable frontend components using React.js": true,
                            "Develop backend services using Node.js and PostgreSQL": true,
                            "Integrate with third-party APIs and internal microservices": true,
                            "Participate in code reviews, sprint planning, and architectural discussions": false,
                            "Write unit and integration tests with Jest/Mocha": true
                        }
                        },
                        "good_to_have_requirements": {
                        "additional_skills": {
                            "TypeScript": true,
                            "GraphQL": false,
                            "CI/CD pipelines": true,
                            "Docker": true,
                            "Strong understanding of security best practices": false
                        }
                        },
                        "additional_screening_criteria": {
                        "Position is full-time and onsite at Bangalore office": true,
                        "Fresh graduates and part-time applicants will not be considered": false,
                        "Open only to candidates with valid Indian work authorization": true,
                        "Applications from women and underrepresented groups are especially encouraged": true
                        }
                    },
                    "qualitative_assessment": {
                        "inferred_skills_from_projects": ["JavaScript", "React.js", "Node.js", "Git", "PostgreSQL"],
                        "project_gravity": "Medium",
                        "ownership_and_initiative": "High",
                        "transferability_to_role": "Low",
                        "recruiter_style_summary": "The candidate has strong technical skills and has demonstrated ownership over impactful projects. They possess experience with React.js, Node.js, and PostgreSQL, and are a strong fit for this role. Bonus experience in fintech or B2B SaaS would be considered a strong plus."
                    },
                    "final_recommendation": "Yes",
                    "summary_of_key_factors": [
                        "Demonstrated experience in both frontend (React.js) and backend (Node.js, PostgreSQL) technologies.",
                        "End-to-end ownership of key projects, including integrations with third-party APIs.",
                        "Relevant project experience with a strong fit to the job requirements, especially in web development.",
                        "Bonus experience in fintech/B2B SaaS is a plus."
                    ]
                    }
                    """
                },
                {
                    "role": "user",
                    "content": f"""You are a recruiter evaluating a candidate's resume against a given job description. Act like a human recruiter—use your intuition and read between the lines to assess the candidate's suitability. 

                    **IMPORTANT MATCHING GUIDELINES:**
                    - For technical skills: Look for exact matches or very similar technologies
                    - For core responsibilities: Be FLEXIBLE and generous. If someone has done mobile app development, API work, or similar tasks, consider it a match even if the exact wording differs
                    - For experience: Consider related experience, not just exact matches
                    - Don't penalize candidates for slight variations in terminology

                    First, perform a quantitative check to determine if the candidate meets each required skill, responsibility, and screening criterion. Then, provide a qualitative assessment, including inferred skills, project impact, ownership, and transferability, while considering the context beyond what's explicitly stated. Finally, give a recommendation ("Yes" or "No") with a brief explanation of the key factors that influenced your decision.

                    ## Job Requirements:
                    {requirements_str}

                    ## Resume:
                    {resume_text}

                    Output ONLY the JSON object as specified in the system prompt, with no additional text or formatting."""
                }
            ],
        
            response_format={
                "type": "json_object"
            },
            reasoning_effort="high",
            store=False
        )
        
        # Parse the response into a dictionary
        analysis = json.loads(response.choices[0].message.content)
        
        # Log the complete JSON response for debugging
        print("\n" + "="*80)
        print("COMPLETE AI RESPONSE JSON:")
        print("="*80)
        print(json.dumps(analysis, indent=2))
        print("="*80)
        
        # Calculate both quantitative and semantic scores
        quantitative_score = calculate_quantitative_score(analysis)
        semantic_score = calculate_semantic_score(analysis)
        
        return {
            "quantitative_score": quantitative_score,
            "semantic_score": semantic_score,
            "score": quantitative_score,  # Keep for backward compatibility
            "analysis": analysis
        }
        
    except Exception as e:
        print(f"Error in analyze_resume: {str(e)}")
        return None

def calculate_quantitative_score(analysis):
    """
    Calculates a simple score by counting the number of true values in all boolean fields.
    Returns a string in format "X/Y" where X is the count of true values and Y is the total number of boolean fields.
    """
    try:
        # Initialize counters
        true_count = 0
        total_fields = 0
        
        # Get the requirement match section
        requirement_match = analysis.get("requirement_match", {})
        
        # Count in must_have_requirements
        must_have = requirement_match.get("must_have_requirements", {})
        
        # Technical skills
        tech_skills = must_have.get("technical_skills", {})
        true_count += sum(1 for v in tech_skills.values() if v is True)
        total_fields += len(tech_skills)
        
        # Experience and qualifications
        if isinstance(must_have.get("experience"), bool):
            if must_have["experience"] is True:
                true_count += 1
            total_fields += 1
            
        if isinstance(must_have.get("qualifications"), bool):
            if must_have["qualifications"] is True:
                true_count += 1
            total_fields += 1
        
        # Core responsibilities
        core_resp = must_have.get("core_responsibilities", {})
        true_count += sum(1 for v in core_resp.values() if v is True)
        total_fields += len(core_resp)
        
        # Count in good_to_have_requirements
        good_to_have = requirement_match.get("good_to_have_requirements", {})
        add_skills = good_to_have.get("additional_skills", {})
        true_count += sum(1 for v in add_skills.values() if v is True)
        total_fields += len(add_skills)
        
        # Count in additional_screening_criteria
        screening = requirement_match.get("additional_screening_criteria", {})
        true_count += sum(1 for v in screening.values() if v is True)
        total_fields += len(screening)
        
        # Return score as "X/Y"
        return f"{true_count}/{total_fields}"
        
    except Exception as e:
        print(f"Error calculating quantitative score: {str(e)}")
        return "0/0"

def calculate_semantic_score(analysis):
    """
    Uses an LLM to calculate a semantic score based on the qualitative assessment.
    Returns a percentage (0-100) representing how well the candidate fits the role semantically.
    """
    try:
        # Extract relevant information from the analysis
        qual_assessment = analysis.get("qualitative_assessment", {})
        final_recommendation = analysis.get("final_recommendation", "")
        summary_factors = analysis.get("summary_of_key_factors", [])
        
        # Prepare the prompt for LLM scoring
        assessment_data = {
            "transferability_to_role": qual_assessment.get("transferability_to_role", "N/A"),
            "project_gravity": qual_assessment.get("project_gravity", "N/A"),
            "ownership_and_initiative": qual_assessment.get("ownership_and_initiative", "N/A"),
            "inferred_skills": qual_assessment.get("inferred_skills_from_projects", []),
            "recruiter_summary": qual_assessment.get("recruiter_style_summary", ""),
            "final_recommendation": final_recommendation,
            "key_factors": summary_factors
        }
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert recruiter tasked with calculating a semantic fit score for a candidate based on their qualitative assessment. 

Your job is to analyze the qualitative factors and provide a numerical score from 0-100 that represents how well this candidate would fit the role semantically (beyond just checking boxes).

Consider these factors in your scoring:
1. **Transferability to Role** (40% weight) - How well their experience transfers to the specific role
2. **Project Quality & Impact** (25% weight) - The gravity and real-world impact of their projects  
3. **Leadership & Ownership** (20% weight) - Their initiative, ownership, and leadership potential
4. **Skill Relevance** (15% weight) - How relevant their inferred skills are to the role

Scoring Guidelines:
- 90-100: Exceptional fit, would excel in the role immediately
- 80-89: Strong fit, would perform very well with minimal onboarding
- 70-79: Good fit, would perform well with some onboarding
- 60-69: Moderate fit, has potential but needs development
- 50-59: Weak fit, significant gaps but some transferable skills
- 40-49: Poor fit, major skill/experience gaps
- 0-39: Very poor fit, not suitable for the role

Output ONLY a JSON object with this structure:
{
    "semantic_score": 85,
    "reasoning": "Brief explanation of the score based on the key factors"
}"""
                },
                {
                    "role": "user", 
                    "content": f"""Based on the following qualitative assessment, calculate a semantic fit score (0-100):

**Assessment Data:**
{json.dumps(assessment_data, indent=2)}

Provide a semantic score that reflects how well this candidate would actually perform in the role, considering their experience transferability, project quality, leadership potential, and skill relevance."""
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        # Parse the LLM response
        llm_result = json.loads(response.choices[0].message.content)
        semantic_score = llm_result.get("semantic_score", 0)
        reasoning = llm_result.get("reasoning", "")
        
        # Log the LLM reasoning for debugging
        print(f"\n--- LLM SEMANTIC SCORING ---")
        print(f"Score: {semantic_score}/100")
        print(f"Reasoning: {reasoning}")
        print("--- END LLM SCORING ---")
        
        # Ensure score is within valid range
        semantic_score = max(0, min(100, int(semantic_score)))
        
        return semantic_score
        
    except Exception as e:
        print(f"Error calculating semantic score with LLM: {str(e)}")
        # Fallback to a simple rule-based approach if LLM fails
        try:
            qual_assessment = analysis.get("qualitative_assessment", {})
            final_rec = analysis.get("final_recommendation", "").lower()
            
            # Simple fallback scoring
            if final_rec == "yes":
                base_score = 70
            else:
                base_score = 30
                
            # Adjust based on transferability
            transferability = qual_assessment.get("transferability_to_role", "").lower()
            if "high" in transferability:
                base_score += 15
            elif "medium" in transferability:
                base_score += 5
            elif "low" in transferability:
                base_score -= 10
                
            return max(0, min(100, base_score))
            
        except Exception as fallback_error:
            print(f"Error in fallback scoring: {str(fallback_error)}")
            return 50  # Default neutral score 