DEFAULT_PROMPTS = {
    "resume_enhancement": "Enhance this resume to match the job description:\n\nResume:\n{resume}\n\nJob Description:\n{job_description}",
    "ats_optimization": "Optimize this resume for better ATS compatibility:\n\nResume:\n{resume}\n\nJob Description:\n{job_description}"
}

def get_prompt(key):
    """Fetches the prompt template based on the key"""
    return DEFAULT_PROMPTS.get(key, DEFAULT_PROMPTS["resume_enhancement"])
