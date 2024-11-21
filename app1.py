import streamlit as st
import base64
import io
import os
from PIL import Image
import pdf2image
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input_text, pdf_content, prompt):
    """
    Generate response using Gemini AI by analyzing resume and job description
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_text, pdf_content[0], prompt])
    return response.text

def input_pdf_setup(uploaded_file):
    """
    Convert uploaded PDF to image for AI processing
    """
    if uploaded_file is not None:
        # Convert PDF to images
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        first_page = images[0]
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        
        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

def main():
    # Streamlit App Configuration
    st.set_page_config(page_title="ATS Resume Expert")
    st.header("Applicant Tracking System (ATS)")

    # Input Job Description
    input_text = st.text_area("Job Description:", key="input", height=200)

    # Resume Upload
    uploaded_file = st.file_uploader("Upload Resume (PDF):", type=["pdf"])

    # Predefined Prompts
    INPUT_PROMPT1 = """
    You are an experienced Technical Human Resource Manager. Review the provided resume 
    against the job description. Provide a professional evaluation of the candidate's 
    profile alignment with the role. Highlight strengths and weaknesses in relation to 
    the specified job requirements.
    """

    INPUT_PROMPT3 = """
    Act as an skilled ATS scanner with deep understanding of data science and 
    tracking system functionality. Evaluate the resume against the job description. 
    Provide:
    1. Percentage match
    2. Missing keywords 
    3. Final assessment
    """

    # Action Buttons
    col1, col2 = st.columns(2)

    with col1:
        submit1 = st.button("Detailed Resume Review")
    
    with col2:
        submit3 = st.button("Match Percentage")

    # Processing Resume
    if submit1:
        if uploaded_file is not None:
            with st.spinner('Analyzing Resume...'):
                pdf_content = input_pdf_setup(uploaded_file)
                response = get_gemini_response(INPUT_PROMPT1, pdf_content, input_text)
                st.subheader("Detailed Resume Analysis")
                st.write(response)
        else:
            st.warning("Please upload a resume first")

    if submit3:
        if uploaded_file is not None:
            with st.spinner('Calculating Match Percentage...'):
                pdf_content = input_pdf_setup(uploaded_file)
                response = get_gemini_response(INPUT_PROMPT3, pdf_content, input_text)
                st.subheader("Resume Matching Results")
                st.write(response)
        else:
            st.warning("Please upload a resume first")

if __name__ == "__main__":
    main()