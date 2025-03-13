import os
import logging
import anthropic
import google.generativeai as genai
import groq
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .file_parser import save_uploaded_file, extract_text_from_pdf 
from .prompts import get_prompt
import requests

# Importing file functions

# Configure logger
logger = logging.getLogger(__name__)

def get_prompt(template, resume_text, job_description):
    """Generates the AI prompt based on a given template"""
    return template.format(resume=resume_text, job_description=job_description)

def enhance_resume_with_mistral(resume_text, job_description, prompt_template=None):
    """Enhances the resume using Mistral AI API"""
    try:
        mistral_api_key = os.getenv("MISTRAL_API_KEY")
        if not mistral_api_key:
            return "Error: Mistral API key is missing."

        prompt_template = prompt_template or get_prompt("resume_enhancement")
        prompt = prompt_template.format(resume=resume_text, job_description=job_description)

        headers = {
            "Authorization": f"Bearer {mistral_api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "mistral-medium",
            "messages": [  # ✅ Mistral API expects a chat-based format
                {"role": "system", "content": "You are an expert in resume optimization."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1024,
            "temperature": 0.7
        }

        response = requests.post("https://api.mistral.ai/v1/chat/completions", json=data, headers=headers)
        response_data = response.json()

        return response_data.get("choices", [{}])[0].get("message", {}).get("content", "Error enhancing resume")

    except Exception as e:
        logger.error(f"Error calling Mistral API: {str(e)}", exc_info=True)
        return "Error enhancing resume"

def enhance_resume_with_gemini(resume_text, job_description, prompt_template=None):
    """Enhances the resume using Gemini AI API with fallback handling"""
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        prompt_template = prompt_template or get_prompt("resume_enhancement")
        prompt = prompt_template.format(resume=resume_text, job_description=job_description)

        model_name = "gemini-1.5-pro"  # ✅ Try the latest model first

        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
        except Exception as e:
            logger.warning(f"{model_name} is not available. Falling back to gemini-1.5-flash. Error: {str(e)}")
            model_name = "gemini-1.5-flash"  # ✅ Fallback to a lower-tier model
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)

        return response.text if response else "Error enhancing resume"

    except Exception as e:
        logger.error(f"Final failure calling Gemini API: {str(e)}", exc_info=True)
        return "Error enhancing resume"

def enhance_resume_with_groq(resume_text, job_description, prompt_template=None):
    """Enhances the resume using Groq AI API"""
    try:
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            return "Error: GROQ API key is missing."

        client = groq.Groq(api_key=groq_api_key)  # ✅ Correct client initialization
        prompt_template = prompt_template or get_prompt("resume_enhancement")
        prompt = prompt_template.format(resume=resume_text, job_description=job_description)

        response = client.chat.completions.create(
            model="llama3-8b-8192",  # ✅ Adjust this to the correct Groq model
            messages=[
                {"role": "system", "content": "You are an expert in resume optimization."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content if response else "Error enhancing resume"
    
    except Exception as e:
        logger.error(f"Error calling Groq API: {str(e)}", exc_info=True)
        return "Error enhancing resume"

class ResumeEnhancementView(APIView):
    def post(self, request):
        resume_text = request.data.get("resume_text")
        job_description = request.data.get("job_description")
        prompt_template = request.data.get("prompt", None)  # Allow frontend to send a custom prompt

        if not resume_text or not job_description:
            return Response({"error": "Resume text and job description are required"}, status=400)

        # Call AI models
        enhanced_resume_mistral = enhance_resume_with_mistral(resume_text, job_description, prompt_template)
        enhanced_resume_gemini = enhance_resume_with_gemini(resume_text, job_description, prompt_template)
        enhanced_resume_groq = enhance_resume_with_groq(resume_text, job_description, prompt_template)

        return Response({
            "enhanced_resume_mistral": enhanced_resume_mistral,
            "enhanced_resume_gemini": enhanced_resume_gemini,
            "enhanced_resume_groq": enhanced_resume_groq
        }, status=200)

class FileUploadView(APIView):
    parser_classes = [MultiPartParser]
    file_type = "general"

    def post(self, request):
        logger.info(f"Received {self.file_type} upload request")
        
        try:
            uploaded_file = request.FILES.get(self.file_type)
            if not uploaded_file:
                logger.warning(f"No {self.file_type} file uploaded")
                return Response({'error': f'No {self.file_type} file uploaded'}, status=400)
            
            # Save file
            file_path = save_uploaded_file(uploaded_file, self.file_type)
            
            # Extract text from the uploaded file
            extracted_text = extract_text_from_pdf(file_path)
            
            logger.info(f"{self.file_type.capitalize()} processed successfully")
            return Response({'extracted_text': extracted_text}, status=200)
        
        except Exception as e:
            logger.error(f"Error processing {self.file_type}: {str(e)}", exc_info=True)
            return Response({'error': 'Internal Server Error'}, status=500)

class ResumeUploadView(FileUploadView):
    file_type = "resume"

class JobDescriptionUploadView(FileUploadView):
    file_type = "job_description"