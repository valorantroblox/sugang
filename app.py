import requests
import json
from flask import Flask, render_template, request, redirect, url_for, session  # 1. session 추가!

app = Flask(__name__)
app.secret_key = "kis_secret_key" # 세션을 위한 비밀키

# --- 설정 데이터 ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1fM3e_ELwfhhW45zLqXZIwjQ_Fd2FDSwwcUXOeWxICoM/edit?gid=0#gid=0"
GAS_URL = "https://script.google.com/macros/s/AKfycbwk7XcnZEU8p7bU2Q1Staw-dXhijMFKijQJ_HuiUgF7yN2kGo--LM5FOtoR8H-kHfFg/exec"

def make_obj(name, sub_type, category="일반"):
    return {"name": name, "type": sub_type, "category": category}

# 2. 데이터 구조는 그대로 유지
SUBJECTS_DATA = {
    "11": {
        "1학기": {
            "국어": [make_obj("문학과 콘텐츠", "국어", "진로"), make_obj("미디어와 국어생활", "국어", "진로"), make_obj("토론과 글쓰기", "국어", "진로")],
            "수학": [make_obj("대수", "수학", "일반"), make_obj("미적분Ⅰ", "수학", "일반")],
            "영어": [make_obj("Essential Academic Reading", "영어", "일반"), make_obj("Essential English Grammar", "영어", "일반"), make_obj("Fundamentals of Psychology", "영어", "진로"), make_obj("Business Studies", "영어", "진로")],
            "영어/과학": [make_obj("Introduction to Chemistry", "영어/과학", "융합"), make_obj("Introduction to Biology", "영어/과학", "융합")],
            "과학": [make_obj("물리학", "과학", "일반"), make_obj("화학", "과학", "일반"), make_obj("생명과학", "과학", "일반")],
            "사회": [make_obj("세계사", "사회", "일반"), make_obj("사회와 문화", "사회", "일반"), make_obj("윤리문제 탐구", "사회", "진로"), make_obj("기후 변화와 지속 가능한 세계", "사회", "진로")],
            "기타/외국어": [make_obj("데이터 과학", "정보", "진로"), make_obj("AI뉴미디어 음악", "예술", "융합"), make_obj("미술 전공 실기 기본", "예술", "진로"), make_obj("실용 베트남어", "외국어", "일반"), make_obj("베트남의 지리와 역사", "외국어", "진로")]
        },
        "2학기": {
            "국어": [make_obj("주제 탐구 독서", "국어", "진로"), make_obj("삶과 글쓰기", "국어", "진로"), make_obj("미디어와 비판적 사고", "국어", "진로")],
            "수학": [make_obj("확률과 통계", "수학", "일반"), make_obj("미적분Ⅱ", "수학", "일반")],
            "영어": [make_obj("Practical Academic Reading", "영어", "일반"), make_obj("Practical English Grammar", "영어", "일반"), make_obj("Psychology in Action", "영어", "진로"), make_obj("International Business", "영어", "진로")],
            "영어/과학": [make_obj("Introduction to Chemistry", "영어/과학", "융합"), make_obj("Introduction to Biology", "영어/과학", "융합")],
            "과학": [make_obj("세포와 물질대사", "과학", "진로"), make_obj("물질과 에너지", "과학", "진로"), make_obj("물리학 실험", "과학", "진로"), make_obj("화학 실험", "과학", "진로")],
            "사회": [make_obj("현대사회와 윤리", "사회", "진로"), make_obj("세계 시민과 지리", "사회", "진로"), make_obj("경제", "사회", "일반"), make_obj("정치", "사회", "일반")],
            "기타/외국어": [make_obj("소프트웨어와 생활", "정보", "진로"), make_obj("포스트모던음악", "예술", "융합"), make_obj("미술 전공 실기 응용", "예술", "진로"), make_obj("실용 베트남어", "외국어", "일반"), make_obj("베트남의 사회와 문화", "외국어", "진로")]
        }
    },
    "12": {
        "1학기": {
            "국어": [make_obj("21세기 문학탐구", "국어", "진로"), make_obj("미디어와 창의적 표현", "국어", "진로"), make_obj("심층 융합 독서", "국어", "융합")],
            "수학": [make_obj("고급 미적분", "수학", "진로"), make_obj("수학과제 탐구", "수학", "진로"), make_obj("기하", "수학", "일반"), make_obj("인공지능 수학", "수학", "융합")],
            "영어": [make_obj("영어Ⅱ", "영어", "일반"), make_obj("Critical Literacy in English", "영어", "진로"), make_obj("English Literature", "영어", "진로"), make_obj("History of Early Civilizations", "영어", "융합")],
            "과학": [make_obj("역학과 에너지", "과학", "진로"), make_obj("전자기와 양자", "과학", "진로"), make_obj("화학 반응의 세계", "과학", "진로"), make_obj("생물의 유전", "과학", "진로"), make_obj("과학과제 연구", "과학", "진로")],
            "사회": [make_obj("윤리와 사상", "사회", "일반"), make_obj("한국지리 탐구", "사회", "진로"), make_obj("법과 사회", "사회", "진로"), make_obj("사회문제 탐구", "사회", "진로")],
            "기타/외국어": [make_obj("음악 연주와 창작", "예술", "진로"), make_obj("미술 전공 실기 심화", "예술", "진로"), make_obj("정보과학 과제연구", "정보", "진로"), make_obj("베트남어 회화", "외국어", "진로"), make_obj("시사 베트남어", "외국어", "진로")]
        },
        "2학기": {
            "국어": [make_obj("문학과 여행", "국어", "진로"), make_obj("프레젠테이션 화법", "국어", "진로"), make_obj("글로벌 이슈 글쓰기", "국어", "융합")],
            "수학": [make_obj("고급 대수", "수학", "진로"), make_obj("실용 통계", "수학", "진로"), make_obj("수학 실험", "수학", "진로")],
            "영어": [make_obj("영어 발표와 토론", "영어", "진로"), make_obj("Contemporary Literacy in English", "영어", "진로"), make_obj("American Literature", "영어", "진로"), make_obj("Adventures in World History", "영어", "융합")],
            "과학": [make_obj("고급 물리", "과학", "진로"), make_obj("고급 화학", "과학", "진로"), make_obj("생명과학 실험", "과학", "진로"), make_obj("융합과학 탐구", "과학", "융합"), make_obj("Comprehensive Chemistry", "과학", "진로"), make_obj("Comprehensive Biology", "과학", "진로")],
            "사회": [make_obj("국제 관계의 이해", "사회", "진로"), make_obj("인문학과 윤리", "사회", "융합"), make_obj("여행지리", "사회", "진로"), make_obj("역사로 탐구하는 현대 세계", "사회", "진로"), make_obj("금융과 경제생활", "사회", "진로")],
            "기타/외국어": [make_obj("Introduction to Engineering", "공학", "융합"), make_obj("Comprehensive Engineering", "공학", "융합"), make_obj("음악 감상과 비평", "예술", "일반"), make_obj("미술 감상과 비평", "예술", "일반"), make_obj("비즈니스 엑셀", "기타", "진로"), make_obj("베트남어 회화", "외국어", "진로"), make_obj("베트남 사회문화탐구", "외국어", "진로")]
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
    
    student_submissions[student_id] = {
        'name': student_name, 
        'grade': grade, 
        'semester': semester,
        'subjects': selected_list, 
        'total_credits': len(selected_list) * 4
    }
    
    try:
        payload = {
            "student_id": student_id, 
            "student_name": student_name, 
            "grade": grade, 
            "semester": semester, 
            "subjects": ", ".join(selected_list)
        }
        response = requests.post(GAS_URL, data=json.dumps(payload), headers={'Content-Type': 'application/json'}, timeout=5)
    except Exception as e:
        print(f"전송 에러: {e}")

    return redirect(url_for('result', student_id=student_id))

@app.route('/result/<student_id>')
def result(student_id):
    info = student_submissions.get(student_id)
    return render_template('result.html', data=info)

# --- 관리자 기능 구역 ---

@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    # 1. 학년/학기 필터 파라미터 가져오기 (기본값은 11학년 1학기)
    selected_grade = request.args.get('grade', '11')
    selected_semester = request.args.get('semester', '1학기')

    # 2. 필터링된 명단 생성
    filtered_submissions = {
        sid: info for sid, info in student_submissions.items()
        if info['grade'] == selected_grade and info['semester'] == selected_semester
    }

    # 3. 과목별 통계 계산 (필터링된 데이터 기준)
    class_stats = {}
    # 전체 선택 결과(class_assignment_results)를 바탕으로 통계 산출
    if class_assignment_results:
        for subject, students in class_assignment_results.items():
            count = len(students)
            if count >= 15: status, color = "정상 개설", "success"
            elif count >= 5: status, color = "인원 부족 주의", "warning"
            else: status, color = "폐강 위기", "danger"
            class_stats[subject] = {"count": count, "status": status, "color": color}

    return render_template('admin.html', 
                           all_submissions=filtered_submissions, # 필터링된 명단만 전달
                           class_results=class_assignment_results,
                           class_stats=class_stats,
                           sheet_url=SHEET_URL,
                           curr_grade=selected_grade,
                           curr_semester=selected_semester)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        pw = request.form.get('password')
        if pw == '1234':
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return "<script>alert('잘못된 비밀번호'); window.history.back();</script>"
            
    return '''
        <div style="text-align:center; margin-top:100px; font-family:sans-serif;">
            <h2>KIS 수강신청 관리자 로그인</h2>
            <form method="post">
                <input type="password" name="password" placeholder="비밀번호" style="padding:10px; border-radius:5px; border:1px solid #ccc;">
                <button type="submit" style="padding:10px 20px; background:#002d5d; color:white; border:none; border-radius:5px; cursor:pointer;">접속</button>
            </form>
        </div>
    '''

@app.route('/assign_classes', methods=['POST'])
def assign_classes():
    global class_assignment_results
    temp_results = {}
    
    for sid, info in student_submissions.items():
        student_display = f"{sid}({info['name']})"
        for subject in info['subjects']:
            if subject not in temp_results:
                temp_results[subject] = []
            temp_results[subject].append(student_display)
            
    class_assignment_results = temp_results
    return redirect(url_for('admin'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)
