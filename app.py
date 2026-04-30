import requests
import json
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.secret_key = "kis_secret_key"

# --- 설정 데이터 ---
# 구글 시트 주소 (네 시트 주소로 바꿔줘)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1fM3e_ELwfhhW45zLqXZIwjQ_Fd2FDSwwcUXOeWxICoM/edit?gid=0#gid=0"
GAS_URL = "https://script.google.com/macros/s/AKfycby87qx58UKlc--Lpqd6OpOe8l2_IJrEZb-gpduBVWpFZILe64joczwQjVKc5jPdLtO2/exec"

# 과목 객체를 만드는 보조 함수
def make_obj(name, sub_type):
    return {"name": name, "type": sub_type}

SUBJECTS_DATA = {
    "11": {
        "1학기": {
            "국어": [
                make_obj("문학과 콘텐츠", "국어"), make_obj("미디어와 국어생활", "국어"), make_obj("토론과 글쓰기", "국어")
            ],
            "수학": [
                make_obj("대수", "수학"), make_obj("미적분Ⅰ", "수학")
            ],
            "영어": [
                make_obj("Essential Academic Reading", "영어"), make_obj("Essential English Grammar", "영어"),
                make_obj("Fundamentals of Psychology", "영어"), make_obj("Business Studies", "영어")
            ],
            "과학": [
                make_obj("물리학", "과학"), make_obj("화학", "과학"), make_obj("생명과학", "과학"),
                make_obj("Introduction to Chemistry", "영어/과학"), make_obj("Introduction to Biology", "영어/과학")
            ],
            "사회": [
                make_obj("세계사", "사회"), make_obj("사회와 문화", "사회"), make_obj("윤리문제 탐구", "사회"),
                make_obj("기후 변화와 지속 가능한 세계", "사회")
            ],
            "기타/외국어": [
                make_obj("데이터 과학", "정보"), make_obj("AI뉴미디어 음악", "예술"),
                make_obj("미술 전공 실기 기본", "예술"), make_obj("실용 베트남어", "외국어"),
                make_obj("베트남의 지리와 역사", "외국어")
            ]
        },
        "2학기": {
            "국어": [
                make_obj("주제 탐구 독서", "국어"), make_obj("삶과 글쓰기", "국어"), make_obj("미디어와 비판적 사고", "국어")
            ],
            "수학": [
                make_obj("확률과 통계", "수학"), make_obj("미적분Ⅱ", "수학")
            ],
            "영어": [
                make_obj("Practical Academic Reading", "영어"), make_obj("Practical English Grammar", "영어"),
                make_obj("Psychology in Action", "영어"), make_obj("International Business", "영어")
            ],
            "과학": [
                make_obj("세포와 물질대사", "과학"), make_obj("물질과 에너지", "과학"),
                make_obj("물리학 실험", "과학"), make_obj("화학 실험", "과학"),
                make_obj("Introduction to Chemistry", "영어/과학"), make_obj("Introduction to Biology", "영어/과학")
            ],
            "사회": [
                make_obj("현대사회와 윤리", "사회"), make_obj("세계 시민과 지리", "사회"), make_obj("경제", "사회"), make_obj("정치", "사회")
            ],
            "기타/외국어": [
                make_obj("소프트웨어와 생활", "정보"), make_obj("포스트모던음악", "예술"),
                make_obj("미술 전공 실기 응용", "예술"), make_obj("실용 베트남어", "외국어"),
                make_obj("베트남의 사회와 문화", "외국어")
            ]
        }
    },
    "12": {
        "1학기": {
            "국어": [
                make_obj("21세기 문학탐구", "국어"), make_obj("미디어와 창의적 표현", "국어"), make_obj("심층 융합 독서", "국어")
            ],
            "수학": [
                make_obj("고급 미적분", "수학"), make_obj("수학과제 탐구", "수학"), make_obj("기하", "수학"), make_obj("인공지능 수학", "수학")
            ],
            "영어": [
                make_obj("영어Ⅱ", "영어"), make_obj("Critical Literacy in English", "영어"),
                make_obj("English Literature", "영어"), make_obj("History of Early Civilizations", "영어")
            ],
            "과학": [
                make_obj("역학과 에너지", "과학"), make_obj("전자기와 양자", "과학"),
                make_obj("화학 반응의 세계", "과학"), make_obj("생물의 유전", "과학"), make_obj("과학과제 연구", "과학")
            ],
            "사회": [
                make_obj("윤리와 사상", "사회"), make_obj("한국지리 탐구", "사회"), make_obj("법과 사회", "사회"), make_obj("사회문제 탐구", "사회")
            ],
            "기타/외국어": [
                make_obj("음악 연주와 창작", "예술"), make_obj("미술 전공 실기 심화", "예술"),
                make_obj("정보과학 과제연구", "정보"), make_obj("베트남어 회화", "외국어"),
                make_obj("시사 베트남어", "외국어")
            ]
        },
        "2학기": {
            "국어": [
                make_obj("문학과 여행", "국어"), make_obj("프레젠테이션 화법", "국어"), make_obj("글로벌 이슈 글쓰기", "국어")
            ],
            "수학": [
                make_obj("고급 대수", "수학"), make_obj("실용 통계", "수학"), make_obj("수학 실험", "수학")
            ],
            "영어": [
                make_obj("영어 발표와 토론", "영어"), make_obj("Contemporary Literacy in English", "영어"),
                make_obj("American Literature", "영어"), make_obj("Adventures in World History", "영어")
            ],
            "과학": [
                make_obj("고급 물리", "과학"), make_obj("고급 화학", "과학"),
                make_obj("생명과학 실험", "과학"), make_obj("융합과학 탐구", "과학"),
                make_obj("Comprehensive Chemistry", "과학"), make_obj("Comprehensive Biology", "과학")
            ],
            "사회": [
                make_obj("국제 관계의 이해", "사회"), make_obj("인문학과 윤리", "사회"), make_obj("여행지리", "사회"),
                make_obj("역사로 탐구하는 현대 세계", "사회"), make_obj("금융과 경제생활", "사회")
            ],
            "기타/외국어": [
                make_obj("Introduction to Engineering", "공학"), make_obj("Comprehensive Engineering", "공학"),
                make_obj("음악 감상과 비평", "예술"), make_obj("미술 감상과 비평", "예술"),
                make_obj("비즈니스 엑셀", "기타"), make_obj("베트남어 회화", "외국어"),
                make_obj("베트남 사회문화탐구", "외국어")
            ]
        }
    }
}

student_submissions = {}
class_assignment_results = {}

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
    
    # 1. 서버 메모리에 저장 (admin 페이지용)
    student_submissions[student_id] = {
        'name': student_name, 
        'grade': grade, 
        'semester': semester,
        'subjects': selected_list, 
        'total_credits': len(selected_list) * 4
    }
    
    # 2. 구글 시트로 전송 (이 부분이 생략되어 있었어!)
    try:
        payload = {
            "student_id": student_id, 
            "student_name": student_name, 
            "grade": grade, 
            "semester": semester, 
            "subjects": ", ".join(selected_list) # 리스트를 글자로 합쳐서 보냄
        }
        
        # POST 방식으로 GAS_URL에 데이터 전송
        response = requests.post(
            GAS_URL, 
            data=json.dumps(payload), 
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        print(f"구글 시트 전송 결과: {response.status_code}") # 터미널에서 성공 확인용
    except Exception as e:
        print(f"구글 시트 전송 에러: {e}")

    return redirect(url_for('result', student_id=student_id))
@app.route('/result/<student_id>')
def result(student_id):
    info = student_submissions.get(student_id)
    return render_template('result.html', data=info)

@app.route('/admin')
def admin():
    class_stats = {}
    if class_assignment_results:
        for subject, students in class_assignment_results.items():
            count = len(students)
            if count >= 15: status, color = "정상 개설", "success"
            elif count >= 5: status, color = "인원 부족 주의", "warning"
            else: status, color = "폐강 위기", "danger"
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
    for sid, info in student_submissions.items():
        for subject in info['subjects']:
            if subject not in temp_results: temp_results[subject] = []
            temp_results[subject].append(info['name'])
    class_assignment_results = temp_results
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
