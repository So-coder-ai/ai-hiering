import re
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Common tech skills for better extraction
COMMON_SKILLS = {
    'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin',
    'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring', 'express',
    'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy', 'matplotlib',
    'sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'firebase', 'aws', 'azure',
    'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab', 'bitbucket',
    'jira', 'confluence', 'agile', 'scrum', 'kanban', 'ci/cd', 'devops', 'nlp',
    'machine learning', 'deep learning', 'artificial intelligence', 'data science',
    'data analysis', 'data visualization', 'big data', 'hadoop', 'spark', 'kafka'
}

# Function to extract skills with better accuracy
def extract_skills(text):
    # Convert to lowercase for better matching
    text_lower = text.lower()
    
    # Find all skills mentioned in the text
    found_skills = []
    for skill in COMMON_SKILLS:
        # Use word boundary to avoid partial matches
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    
    return found_skills

# Function to extract experience with improved pattern matching
def extract_experience(text):
    # Multiple patterns to catch different experience formats
    patterns = [
        r'(\d+)\s*years?', 
        r'(\d+)\s*\+\s*years?',
        r'(\d+)\s*yr',
        r'experience\D*(\d+)',
        r'(\d+)\s*years?\s*experience'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1) + " years"
    
    return "Not specified"

# Resume Parsing with better error handling
def parse_resume(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            resume_text = file.read()
    except UnicodeDecodeError:
        # Try different encoding if utf-8 fails
        try:
            with open(file_path, "r", encoding="latin-1") as file:
                resume_text = file.read()
        except:
            return {
                "name": os.path.basename(file_path),
                "skills": [],
                "experience": "Not specified",
                "education": "Not specified"
            }, "Error reading file"
    
    # Extract basic information
    name = "Unknown"
    education = "Not specified"
    
    # Extract name (simple approach)
    for line in resume_text.split('\n'):
        if "Name:" in line:
            name = line.split("Name:")[1].strip()
            break
    
    # Extract education (simple approach)
    education_keywords = ["B.Tech", "Bachelor", "Master", "PhD", "M.Tech", "BSc", "MSc"]
    for line in resume_text.split('\n'):
        for keyword in education_keywords:
            if keyword in line:
                education = line.strip()
                break
        if education != "Not specified":
            break
    
    extracted_data = {
        "name": name,
        "skills": extract_skills(resume_text),
        "experience": extract_experience(resume_text),
        "education": education
    }
    
    return extracted_data, resume_text

# Enhanced ranking function with skill matching
def rank_candidates(resume_files, job_description):
    if not resume_files:
        return []
    
    resumes = []
    parsed_data_list = []
    
    # Parse each resume
    for file_path in resume_files:
        parsed_data, resume_text = parse_resume(file_path)
        parsed_data_list.append(parsed_data)
        resumes.append(resume_text)
    
    # Extract required skills from job description
    required_skills = extract_skills(job_description)
    
    # Calculate TF-IDF similarity
    all_texts = resumes + [job_description]
    vectorizer = TfidfVectorizer(stop_words='english')
    
    try:
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        similarity_scores = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])[0]
    except:
        # Fallback if TF-IDF fails
        similarity_scores = np.zeros(len(resumes))
    
    # Calculate skill match score
    skill_scores = []
    for data in parsed_data_list:
        candidate_skills = data["skills"]
        if not required_skills:
            skill_score = 0.5  # Neutral score if no required skills specified
        else:
            matching_skills = set(candidate_skills).intersection(set(required_skills))
            skill_score = len(matching_skills) / len(required_skills) if required_skills else 0
        skill_scores.append(skill_score)
    
    # Combine scores (70% TF-IDF, 30% skill matching)
    final_scores = []
    for i in range(len(resumes)):
        tfidf_score = similarity_scores[i] if i < len(similarity_scores) else 0
        combined_score = (0.7 * tfidf_score) + (0.3 * skill_scores[i])
        final_scores.append(combined_score)
    
    # Return ranked indices and scores
    return sorted(enumerate(final_scores), key=lambda x: x[1], reverse=True)

# For testing directly
if __name__ == "__main__":
    # Example usage
    resume_files = ["resume1.txt", "resume2.txt", "resume3.txt"]
    job_desc = "Looking for an AI Engineer with experience in Python, TensorFlow, and NLP."
    
    ranking = rank_candidates(resume_files, job_desc)
    print("\nResume Rankings:")
    for idx, score in ranking:
        print(f"Resume: {resume_files[idx]} → Score: {score:.4f}")

