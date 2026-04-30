import requests
import json
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.secret_key = "kis_secret_key"

GAS_URL = "https://script.google.com/macros/s/AKfybygSZnM6HeId6CCD15XwRyAKfFVrtXicP5zlVHiUy9Hp9vdnkyAG_igsRF0ncDDkdV/exec"

# --- 과목 데이터를 HTML 객체 형식에 맞게 수정 ---
def make_obj(name, sub_type="전공선택"):
    return {"name": name, "type": sub_type}

SUBJECTS_DATA = {
    "11": {
        "1학기": {
            "국어/수학/영어": [make_obj("문학과 콘텐츠", "국어"), make_obj("미디어와 국어생활", "국어"), make_obj("토론과 글쓰기", "국어"), make_obj("대수", "수학"), make_obj("미적분Ⅰ", "수학"), make_obj("Essential Academic Reading", "영어")],
            "사회/과학": [make_obj("세계사", "사회"), make_obj("사회와 문화", "사회"), make_obj("물리학", "과학"), make_obj("화학", "과학")],
            "정보/예술/기타": [make_obj("데이터 과학", "정보"), make_obj("실용 베트남어", "외국어")]
        },
        "2학기": {
            "국어/수학/영어": [make_obj("주제 탐구 독서", "국어"), make_obj("확률과 통계", "수학"), make_obj("미적분Ⅱ", "수학"), make_obj("Practical Academic Reading", "영어")],
            "사회/과학": [make_obj("경제", "사회"), make_obj("정치", "사회"), make_obj("물질과 에너지", "과학"), make_obj("화학 실험", "과학")],
            "정보/예술/기타": [make_obj("소프트웨어와 생활", "정보"), make_obj("실용 베트남어", "외국어")]
        }
    },
    "12": {
        "1학기": {
            "국어/수학/영어": [make_obj("21세기 문학탐구", "국어"), make_obj("고급 미적분", "수학"), make_obj("기하", "수학"), make_obj("영어Ⅱ", "영어")],
            "사회/과학": [make_obj("윤리와 사상", "사회"), make_obj("법과 사회", "사회"), make_obj("역학과 에너지", "과학"), make_obj("과학과제 연구", "과학")],
            "정보/예술/기타": [make_obj("음악 연주와 창작", "예술"), make_obj("베트남어 회화", "외국어")]
        },
        "2학기": {
            "국어/수학/영어": [make_obj("문학과 여행", "국어"), make_obj("고급 대수", "수학"), make_obj("실용 통계", "수학"), make_obj("영어 발표와 토론", "영어")],
            "사회/과학": [make_obj("국제 관계의 이해", "사회"), make_obj("여행지리", "사회"), make_obj("고급 물리", "과학"), make_obj("융합과학 탐구", "과학")],
            "정보/예술/기타": [make_obj("Introduction to Engineering", "공학"), make_obj("비즈니스 엑셀", "기타")]
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
    
    subjects = SUBJECTS_DATA.get(grade, {}).get(semester, {})
    target_credit = 28 if grade == "11" else 32
    
    return render_template('select.html', 
                           student_id=student_id, student_name=student_name, 
                           grade=grade, semester=semester, 
                           subjects=subjects, target_credit=target_credit)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        student_id = request.form.get('student_id')
        student_name = request.form.get('student_name')
        selected_list = request.form.getlist('selected_subjects')
        
        # result.html의 {{ data.name }}에 맞춰 data라는 이름으로 저장
        student_submissions[student_id] = {
            'name': student_name,
            'subjects': selected_list,
            'total_credits': len(selected_list) * 4
        }
        
        # 구글 시트 전송
        try:
            payload = {"student_id": student_id, "student_name": student_name, "subjects": ", ".join(selected_list)}
            requests.post(GAS_URL, data=json.dumps(payload), timeout=2)
        except: pass

        return redirect(url_for('result', student_id=student_id))
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/result/<student_id>')
def result(student_id):
    info = student_submissions.get(student_id)
    # result.html의 {{ data }} 변수명에 맞춤
    return render_template('result.html', data=info)

if __name__ == '__main__':
    app.run(debug=True)
