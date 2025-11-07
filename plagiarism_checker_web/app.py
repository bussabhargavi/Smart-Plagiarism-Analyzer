from flask import Flask, render_template, request, url_for, redirect
from utils import check_plagiarism, get_highlighted_texts
import os

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🔹 Root redirects to welcome page
@app.route('/')
def home():
    return redirect(url_for('welcome'))

# 🔹 Welcome page
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

# 🔹 Upload form & results
@app.route('/form', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original = request.files.get('original_file')
        student_files = request.files.getlist('student_files')

        if not original or not student_files or len(student_files) == 0:
            return "Please upload the original and at least one student file."

        original_path = os.path.join(UPLOAD_FOLDER, "original_" + original.filename)
        original.save(original_path)

        results = []

        for student_file in student_files:
            if student_file.filename.endswith('.pdf'):
                student_path = os.path.join(UPLOAD_FOLDER, student_file.filename)
                student_file.save(student_path)

                score = check_plagiarism(original_path, student_path)
                score_value = float(score)

                if score_value <= 20:
                    status_label = "Accepted"
                    status_class = "success"
                elif score_value <= 50:
                    status_label = "Review"
                    status_class = "warning"
                else:
                    status_label = "Rejected"
                    status_class = "danger"

                results.append({
                    'student_file': student_file.filename,
                    'score': f"{score_value:.2f}%",
                    'status_label': status_label,
                    'status_class': status_class
                })

        return render_template('results.html', results=results)

    return render_template('index.html')

# 🔹 View comparison
@app.route('/view')
def view_comparison():
    student_file = request.args.get('student')

    original_file = next((f for f in os.listdir(UPLOAD_FOLDER) if f.startswith("original_")), None)
    if not original_file:
        return "Original file not found."

    original_path = os.path.join(UPLOAD_FOLDER, original_file)
    student_path = os.path.join(UPLOAD_FOLDER, student_file)

    original_html, student_html = get_highlighted_texts(original_path, student_path)

    return render_template('view.html', original=original_html, student=student_html, student_file=student_file)

# 🔹 Start app
if __name__ == '__main__':
    app.run(debug=True)
