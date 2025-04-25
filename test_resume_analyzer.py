from resume_analyzer import analyze_resume
import json

# Sample job requirements
sample_requirements = {
    "original_job_description": """Job Title: Software Development Engineer (SDE)
Location: Bangalore / Remote
Experience: 2-5 years
Type: Full-time

About the Role
We are looking for a passionate Software Development Engineer who loves to build scalable, performant systems and solve real-world problems through clean and efficient code. You will be part of a fast-paced, collaborative environment where your contributions will directly impact millions of users.

Responsibilities
- Design, develop, test, and deploy scalable backend services and APIs.
- Collaborate with cross-functional teams to define, design, and ship new features.
- Own services and systems end-to-end — from design to deployment and monitoring.
- Write clean, maintainable, and testable code following best practices.
- Participate in code reviews, architecture discussions, and improve development processes.
- Troubleshoot, debug, and optimize code to improve system performance and reliability.

Basic Qualifications
- Bachelor's degree in Computer Science or related field.
- 2+ years of professional experience in software development.
- Proficiency in one or more programming languages such as Java, Python, Go, or C++.
- Strong understanding of data structures, algorithms, and computer science fundamentals.
- Experience with RESTful APIs, microservices, and distributed systems.
- Familiarity with CI/CD pipelines and modern DevOps practices.

Preferred Qualifications
- Experience working with cloud platforms (AWS/GCP/Azure).
- Exposure to containerization technologies like Docker and Kubernetes.
- Knowledge of databases (SQL and NoSQL) and caching strategies.
- Prior experience in a product-based or high-scale tech environment.""",
    "must_have_requirements": {
        "technical_skills": {
            "Java/Python/Go/C++": True,
            "Data Structures & Algorithms": True,
            "RESTful APIs": True,
            "Microservices": True,
            "CI/CD": True
        },
        "experience": "2+ years",
        "qualifications": "Bachelor's degree in Computer Science",
        "core_responsibilities": {
            "Design and develop backend services": True,
            "Write clean, maintainable code": True,
            "Participate in code reviews": True,
            "Troubleshoot and optimize code": True
        }
    },
    "good_to_have_requirements": {
        "additional_skills": {
            "Cloud Platforms (AWS/GCP/Azure)": True,
            "Docker & Kubernetes": True,
            "SQL/NoSQL Databases": True,
            "Caching Strategies": True
        }
    },
    "additional_screening_criteria": {
        "Full-time availability": True,
        "Remote work possible": True
    }
}

# Sample resume text
sample_resume = """
Rahul Sharma
Software Development Engineer
rahul.sharma@email.com
Bangalore, India

EXPERIENCE
Senior Software Engineer
Tech Solutions Inc. | 2020 - Present
- Designed and implemented scalable microservices architecture using Java Spring Boot
- Developed RESTful APIs serving 1M+ daily requests
- Led the migration of legacy monolith to microservices, improving system performance by 40%
- Implemented CI/CD pipelines using Jenkins and Docker
- Optimized database queries reducing response time by 30%
- Mentored junior developers and conducted code reviews

Software Engineer
StartupX | 2018 - 2020
- Built and maintained backend services using Python and Django
- Implemented caching strategies using Redis
- Developed automated testing framework reducing bugs by 25%
- Worked on AWS infrastructure (EC2, S3, RDS)
- Participated in architecture design discussions

EDUCATION
Bachelor of Technology in Computer Science
Indian Institute of Technology | 2014 - 2018
- Specialized in Software Systems
- GPA: 8.5/10

SKILLS
Programming: Java, Python, Go
Backend: Spring Boot, Django, REST APIs
Cloud: AWS, Docker, Kubernetes
Databases: MySQL, MongoDB, Redis
Tools: Git, Jenkins, Jira
"""

# Run the analysis
result = analyze_resume(sample_resume, sample_requirements)

# Print the complete raw output in a formatted way
print("\n=== Complete LLM Output ===")
print(json.dumps(result["analysis"], indent=2))

# Print the score
print("\n=== Score ===")
print(result["score"]) 