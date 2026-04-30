import requests
import json
import traceback
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.secret_key = "kis_secret_key"

# --- 설정 데이터 ---
GAS_URL = "https://script.google.com/macros/s/AKfybygSZnM6HeId6CCD15XwRyAKfFVrtXicP5zlVHiUy9Hp9vdnkyAG_igsRF0ncDDkdV/exec"

# --- 과목 데이터 (11학년 & 12학년 사진 반영) ---
SUBJECTS_DATA = {
    "11": {
        "1학기": {
            "국어/수학/영어": ["문학과 콘텐츠", "미디어와 국어생활", "토론과 글쓰기", "대수", "미적분Ⅰ", "Essential Academic Reading", "Essential English Grammar", "Fundamentals of Psychology", "Business Studies", "Introduction to Chemistry", "Introduction to Biology"],
            "사회/과학": ["세계사", "사회와 문화", "윤리문제 탐구", "기후 변화와 지속 가능한 세계", "물리학", "화학", "생명과학"],
            "정보/예술/기타": ["데이터 과학", "AI뉴미디어 음악", "미술 전공 실기 기본", "실용 베트남어", "베트남의 지리와 역사"]
        },
        "2학기": {
            "국어/수학/영어": ["주제 탐구 독서", "삶과 글쓰기", "미디어와 비판적 사고", "확률과 통계", "미적분Ⅱ", "Practical Academic Reading", "Practical English Grammar", "Psychology in Action", "International Business", "Introduction to Chemistry", "Introduction to Biology"],
            "사회/과학": ["현대사회와 윤리", "세계 시민과 지리", "경제", "정치", "세포와 물질대사", "물질과 에너지", "물리학 실험", "화학 실험"],
            "정보/예술/기타": ["소프트웨어와 생활", "포스트모던음악", "미술 전공 실기 응용", "실용 베트남어", "베트남의 사회와 문화"]
        }
    },
    "12": {
        "1학기": {
            "국어/수학/영어": ["21세기 문학탐구", "미디어와 창의적 표현", "심층 융합 독서", "고급 미적분", "수학과제 탐구", "기하", "인공지능 수학", "영어Ⅱ", "Critical Literacy in English", "English Literature", "History of Early Civilizations"],
            "사회/과학": ["윤리와 사상", "한국지리 탐구", "법과 사회", "사회문제 탐구", "역학과 에너지", "전자기와 양자", "화학 반응의 세계", "생물의 유전", "과학과제 연구"],
            "정보/예술/기타": ["음악 연주와 창작", "미술 전공 실기 심화", "정보과학 과제연구", "베트남어 회화", "시사 베트남어"]
        },
        "2학기": {
            "국어/수학/영어": ["문학과 여행", "프레젠테이션 화법", "글로벌 이슈 글쓰기", "고급 대수", "실용 통계", "수학 실험", "영어 발표와 토론", "Contemporary Literacy in English", "American Literature", "Adventures in World History"],
            "사회/과학": ["국제 관계의 이해", "인문학과 윤리", "여행지리", "역사로 탐구하는 현대 세계", "금융과 경제생활", "고급 물리", "고급 화학", "생명과학 실험", "융합과학 탐구"],
            "정보/예술/기타": ["Introduction to Engineering", "Comprehensive Engineering", "Comprehensive Chemistry", "Comprehensive Biology", "음악 감상과 비평", "미술 감상과 비평", "비즈니스 엑셀", "베트남어 회화", "베트남 사회문화탐구"]
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
    return render_template('select.html', student_id=student_id, student_name=student_name, grade=grade, semester=semester, subjects=subjects, target_credit=target_credit)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        student_id = request.form.get('student_id')
        student_name = request.form.get('student_name')
        grade = request.form.get('grade')
        semester = request.form.get('semester')
        selected_list = request.form.getlist('selected_subjects')
        
        student_submissions[student_id] = {
            'name': student_name, 'grade': grade, 'semester': semester,
            'subjects': selected_list, 'total_credits': len(selected_list) * 4
        }
        
        try:
            payload = {"student_id": student_id, "student_name": student_name, "grade": grade, "semester": semester, "subjects": ", ".join(selected_list)}
            requests.post(GAS_URL, data=json.dumps(payload), timeout=2)
        except: pass

        return redirect(url_for('result', student_id=student_id))
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/result/<student_id>')
def result(student_id):
    info = student_submissions.get(student_id)
    return render_template('result.html', info=info)

if __name__ == '__main__':
    app.run(debug=True)
