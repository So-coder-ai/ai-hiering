from flask import Flask, request, jsonify
import os
import tempfile
from resume_processor import rank_candidates

app = Flask(__name__)
# Use a more reliable path without spaces
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")

# Ensure upload directory exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_files():
    try:
        if "job_description" not in request.files:
            return jsonify({"error": "Job description file missing"}), 400
        
        job_desc_file = request.files["job_description"]
        resume_files = request.files.getlist("resumes")

        if not resume_files:
            return jsonify({"error": "No resumes uploaded"}), 400

        # Save job description
        job_desc_path = os.path.join(app.config["UPLOAD_FOLDER"], job_desc_file.filename)
        job_desc_file.save(job_desc_path)

        # Save resume files
        resume_paths = []
        for resume_file in resume_files:
            resume_path = os.path.join(app.config["UPLOAD_FOLDER"], resume_file.filename)
            resume_file.save(resume_path)
            resume_paths.append(resume_path)

        # Read job description text
        try:
            with open(job_desc_path, "r", encoding="utf-8") as file:
                job_description = file.read()
        except UnicodeDecodeError:
            # Try different encoding if utf-8 fails
            with open(job_desc_path, "r", encoding="latin-1") as file:
                job_description = file.read()

        # Get candidate names for better response
        candidate_names = []
        for path in resume_paths:
            try:
                with open(path, "r", encoding="utf-8") as file:
                    content = file.read()
                    # Simple extraction of name from first line that contains "Name:"
                    for line in content.split('\n'):
                        if "Name:" in line:
                            candidate_names.append(line.split("Name:")[1].strip())
                            break
            except:
                candidate_names.append(os.path.basename(path))

        # Rank candidates
        ranking_results = rank_candidates(resume_paths, job_description)
        
        # Format results with candidate names
        formatted_results = []
        for idx, score in ranking_results:
            name = candidate_names[idx] if idx < len(candidate_names) else f"Candidate {idx+1}"
            formatted_results.append({
                "name": name,
                "file": os.path.basename(resume_paths[idx]),
                "score": float(score),
                "rank": idx + 1
            })
        
        return jsonify({
            "rankings": formatted_results,
            "job_description": job_description
        })

    except Exception as e:
        import traceback
        print("Error:", str(e))
        print(traceback.format_exc())
        return jsonify({"error": f"Failed to process request: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)

