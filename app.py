import requests
import json
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.secret_key = "kis_secret_key"

# --- 설정 데이터 ---
# 구글 시트 주소 (정민이 시트 주소로 바꿔줘)
SHEET_URL = "https://docs.google.com/spreadsheets/d/your_sheet_id_here"
GAS_URL = "https://script.google.com/macros/s/AKfybygSZnM6HeId6CCD15XwRyAKfFVrtXicP5zlVHiUy9Hp9vdnkyAG_igsRF0ncDDkdV/exec"

# 과목 데이터 (생략 - 기존 11, 12학년 데이터 그대로 유지해줘)
SUBJECTS_DATA = { 
    # ... (기존에 꽉 채워준 SUBJECTS_DATA를 여기에 넣어줘) ...
}

# 데이터 저장소
student_submissions = {} # { student_id: {name, grade, semester, subjects, total_credits} }
class_assignment_results = {} # 반 편성 결과 저장

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/select_subjects', methods=['POST'])
def select_subjects():
    student_id = request.form.get('student_id')
    student_name = request.form.get('student_name')
    grade = request.form.get('grade')
    semester = request.form.get('semester')
    subjects = SUBJECTS_DATA.get(grade, {}).get(semester, {})
    target_credit = 28 if grade == "11" else 32
    return render_template('select.html', student_id=student_id, student_name=student_name, grade=grade, semester=semester, subjects=subjects, target_credit=target_credit)

@app.route('/submit', methods=['POST'])
def submit():
    student_id = request.form.get('student_id')
    student_name = request.form.get('student_name')
    grade = request.form.get('grade')
    semester = request.form.get('semester')
    selected_list = request.form.getlist('selected_subjects')
    
    # 데이터 저장
    student_submissions[student_id] = {
        'name': student_name, 'grade': grade, 'semester': semester,
        'subjects': selected_list, 'total_credits': len(selected_list) * 4
    }
    
    # 구글 시트 전송 (예외처리)
    try:
        payload = {"student_id": student_id, "student_name": student_name, "grade": grade, "semester": semester, "subjects": ", ".join(selected_list)}
        requests.post(GAS_URL, data=json.dumps(payload), timeout=2)
    except: pass

    return redirect(url_for('result', student_id=student_id))

@app.route('/result/<student_id>')
def result(student_id):
    info = student_submissions.get(student_id)
    return render_template('result.html', data=info)

# --- 관리자 페이지 (핵심 수정 부분) ---
@app.route('/admin')
def admin():
    # 반 편성 통계 계산
    class_stats = {}
    if class_assignment_results:
        for subject, students in class_assignment_results.items():
            count = len(students)
            # 인원수에 따른 상태 설정
            if count >= 15:
                status, color = "정상 개설", "success"
            elif count >= 5:
                status, color = "인원 부족 주의", "warning"
            else:
                status, color = "폐강 위기", "danger"
            
            class_stats[subject] = {"count": count, "status": status, "color": color}

    return render_template('admin.html', 
                           all_submissions=student_submissions, 
                           class_results=class_assignment_results,
                           class_stats=class_stats,
                           sheet_url=SHEET_URL)

@app.route('/assign_classes', methods=['POST'])
def assign_classes():
    global class_assignment_results
    temp_results = {}
    
    # 모든 학생의 신청 과목을 순회하며 과목별로 학생 명단 분류
    for sid, info in student_submissions.items():
        for subject in info['subjects']:
            if subject not in temp_results:
                temp_results[subject] = []
            temp_results[subject].append(info['name'])
            
    class_assignment_results = temp_results
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
