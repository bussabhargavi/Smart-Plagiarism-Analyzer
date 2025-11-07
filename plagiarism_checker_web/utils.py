from PyPDF2 import PdfReader
from difflib import SequenceMatcher
import html

# ✅ Common grammar/function words to ignore during scoring
stopwords = {
    'i', 'we', 'you', 'he', 'she', 'it', 'they', 'me', 'him', 'her', 'us', 'them',
    'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did',
    'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while',
    'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
    'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up',
    'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then',
    'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both',
    'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just'
}

# ✅ Extract plain text from a PDF
def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''
        return text
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ''

# ✅ Compute plagiarism % ignoring stopwords
def check_plagiarism(original_path, student_path):
    original_text = extract_text_from_pdf(original_path)
    student_text = extract_text_from_pdf(student_path)

    # Lowercase & filter out stopwords
    original_words = [w.lower() for w in original_text.split() if w.lower() not in stopwords]
    student_words = [w.lower() for w in student_text.split() if w.lower() not in stopwords]

    matcher = SequenceMatcher(None, original_words, student_words)
    match_ratio = matcher.ratio()

    return match_ratio * 100

# ✅ Highlight matching words in original & student text
def get_highlighted_texts(original_path, student_path):
    original_text = extract_text_from_pdf(original_path)
    student_text = extract_text_from_pdf(student_path)

    original_words = original_text.split()
    student_words = student_text.split()

    matcher = SequenceMatcher(None, original_words, student_words)

    highlighted_original = []
    highlighted_student = []

    for opcode, i1, i2, j1, j2 in matcher.get_opcodes():
        orig_chunk = original_words[i1:i2]
        stud_chunk = student_words[j1:j2]

        if opcode == 'equal':
            # ✅ Highlight exact matching words
            highlighted_original.append(' '.join(
                f'<span style="background-color:#d4edda">{html.escape(w)}</span>' for w in orig_chunk
            ))
            highlighted_student.append(' '.join(
                f'<span style="background-color:#d4edda">{html.escape(w)}</span>' for w in stud_chunk
            ))
        else:
            highlighted_original.append(' '.join(html.escape(w) for w in orig_chunk))
            highlighted_student.append(' '.join(html.escape(w) for w in stud_chunk))

    return ' '.join(highlighted_original), ' '.join(highlighted_student)
