import requests
import json
import traceback
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# 1. 구글 앱스 스크립트 배포 후 받은 URL을 여기에 꼭 넣어줘!
GAS_URL = "https://script.google.com/macros/s/AKfycby_swDhlmt4b1cjGySfk3nYiy7gli2oVi6GaEB0YVwlQ0giAyImrWd3V2HKiVTnNSOZ/exec"

# 데이터 저장소 (관리자 페이지에서 실시간 확인용 임시 저장)
student_submissions = {}

# 11학년 1학기 실제 과목 데이터
SUBJECTS_DATA = {
    "11": {
        "1학기": {
            "기초/탐구": ["대수", "미적분Ⅰ", "문학과 콘텐츠", "토론과 글쓰기", "Essential English Grammar", "Essential Academic Reading", "미디어와 국어생활"],
            "사회/과학": ["사회와 문화", "세계사", "생명과학", "화학", "윤리문제 탐구", "Fundamentals of Psychology", "Introduction to Chemistry"],
            "예술/기타": ["데이터 과학", "Business Studies"]
        }
    }
}

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/select_subjects', methods=['POST'])
def select_subjects():
    try:
        grade = request.form.get('grade')
        semester = request.form.get('semester')
        student_id = request.form.get('student_id')
        student_name = request.form.get('student_name')
        
        if not all([grade, semester, student_id, student_name]):
            return redirect(url_for('index'))
            
        subjects = SUBJECTS_DATA.get(grade, {}).get(semester, {})
        target_credit = 28 if grade == "11" else 32
        
        return render_template('select.html', grade=grade, semester=semester, 
                               student_id=student_id, student_name=student_name, 
                               subjects=subjects, target_credit=target_credit)
    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>", 500

@app.route('/submit', methods=['POST'])
def submit():
    try:
        student_id = request.form.get('student_id')
        student_name = request.form.get('student_name')
        selected_list = request.form.getlist('selected_subjects')
        subjects_str = ", ".join(selected_list)
        
        if student_id:
            # 1. 로컬 메모리에 저장 (관리자용)
            student_submissions[student_id] = {
                'name': student_name,
                'subjects': selected_list,
                'total_credits': len(selected_list) * 4
            }
            
            # 2. 구글 시트(Apps Script)로 데이터 전송
            payload = {
                "student_id": student_id,
                "student_name": student_name,
                "subjects": subjects_str
            }
            requests.post(GAS_URL, data=json.dumps(payload))
            
        return redirect(url_for('result', student_id=student_id))
    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>", 500

@app.route('/result/<student_id>')
def result(student_id):
    data = student_submissions.get(student_id, {})
    return render_template('result.html', data=data)

@app.route('/admin')
def admin():
    return render_template('admin.html', all_submissions=student_submissions, class_results=None)

@app.route('/assign_classes', methods=['POST'])
def assign_classes():
    class_assignments = {}
    for sid, info in student_submissions.items():
        for subject in info.get('subjects', []):
            if subject not in class_assignments:
                class_assignments[subject] = []
            class_assignments[subject].append(f"{info['name']}({sid})")
    
    return render_template('admin.html', all_submissions=student_submissions, class_results=class_assignments)

if __name__ == '__main__':
    app.run(debug=True)
