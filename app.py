import requests
import json
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.secret_key = "kis_secret_key"

# 과목 객체를 만드는 함수 (네 HTML의 subject.name, subject.type 대응용)
def make_obj(name, sub_type="전공선택"):
    return {"name": name, "type": sub_type}

SUBJECTS_DATA = {
    "11": {
        "1학기": {
            "국어/수학/영어": [
                make_obj("문학과 콘텐츠", "국어"), make_obj("미디어와 국어생활", "국어"), 
                make_obj("대수", "수학"), make_obj("미적분Ⅰ", "수학"), 
                make_obj("Essential Academic Reading", "영어")
            ],
            "사회/과학": [
                make_obj("세계사", "사회"), make_obj("물리학", "과학"), make_obj("화학", "과학")
            ],
            "정보/예술/기타": [
                make_obj("데이터 과학", "정보"), make_obj("실용 베트남어", "외국어")
            ]
        },
        "2학기": {
            "국어/수학/영어": [
                make_obj("주제 탐구 독서", "국어"), make_obj("확률과 통계", "수학"), 
                make_obj("Practical Academic Reading", "영어")
            ],
            "사회/과학": [
                make_obj("경제", "사회"), make_obj("물질과 에너지", "과학")
            ],
            "정보/예술/기타": [
                make_obj("소프트웨어와 생활", "정보"), make_obj("실용 베트남어", "외국어")
            ]
        }
    },
    "12": {
        "1학기": {
            "국어/수학/영어": [
                make_obj("21세기 문학탐구", "국어"), make_obj("고급 미적분", "수학"), 
                make_obj("영어Ⅱ", "영어")
            ],
            "사회/과학": [
                make_obj("윤리와 사상", "사회"), make_obj("역학과 에너지", "과학")
            ],
            "정보/예술/기타": [
                make_obj("음악 연주와 창작", "예술"), make_obj("베트남어 회화", "외국어")
            ]
        },
        "2학기": {
            "국어/수학/영어": [
                make_obj("문학과 여행", "국어"), make_obj("고급 대수", "수학"), 
                make_obj("영어 발표와 토론", "영어")
            ],
            "사회/과학": [
                make_obj("국제 관계의 이해", "사회"), make_obj("고급 물리", "과학")
            ],
            "정보/예술/기타": [
                make_obj("Introduction to Engineering", "공학"), make_obj("비즈니스 엑셀", "기타")
            ]
        }
    }
}

student_submissions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/select_subjects', methods=['POST'])
def select_subjects():
    student_id = request.form.get('student_id')
    student_name = request.form.get('student_name')
    grade = request.form.get('grade')
    semester = request.form.get('semester')
    
    # 학년/학기에 맞는 데이터 가져오기
    subjects = SUBJECTS_DATA.get(grade, {}).get(semester, {})
    target_credit = 28 if grade == "11" else 32
    
    return render_template('select.html', 
                           student_id=student_id, student_name=student_name, 
                           grade=grade, semester=semester, 
                           subjects=subjects, target_credit=target_credit)

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
