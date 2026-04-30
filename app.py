import requests
import json
import traceback
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "kis_secret_key"

# --- 설정 데이터 ---
GAS_URL = "https://script.google.com/macros/s/AKfybygSZnM6HeId6CCD15XwRyAKfFVrtXicP5zlVHiUy9Hp9vdnkyAG_igsRF0ncDDkdV/exec"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1fM3e_ElwfhhW45zLqXZIwjQ_Fd2FDswwcUXOeWxICoM/edit?hl=ko&gid=0#gid=0"

# --- 과목 데이터 (11학년 & 12학년 사진 완벽 반영) ---
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

# 메모리 저장소 (서버 재시작 시 초기화됨)
student_submissions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/select_subjects', methods=['POST'])
def select_subjects():
    student_id = request.form.get('student_id')
    student_name = request.form.get('student_name')
    grade = request.form.get('grade', '11')
    semester = request.form.get('semester', '1학기')
    
    subjects = SUBJECTS_DATA.get(grade, {}).get(semester, {})
    # 사진 기준 11학년은 28학점(택7), 12학년은 32학점(택8) 설정
    target_credit = 28 if grade == "11" else 32
    
    return render_template('select.html', 
                           student_id=student_id, 
                           student_name=student_name, 
                           grade=grade, 
                           semester=semester, 
                           subjects=subjects,
                           target_credit=target_credit)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        student_id = request.form.get('student_id')
        student_name = request.form.get('student_name')
        grade = request.form.get('grade')
        semester = request.form.get('semester')
        selected_list = request.form.getlist('selected_subjects')
        
        if student_id:
            student_submissions[student_id] = {
                'name': student_name,
                'grade': grade,
                'semester': semester,
                'subjects': selected_list,
                'total_credits': len(selected_list) * 4
            }
            
            # 구글 시트로 데이터 전송
            payload = {
                "student_id": student_id,
                "student_name": student_name,
                "grade": grade,
                "semester": semester,
                "subjects": ", ".join(selected_list)
            }
            requests.post(GAS_URL, data=json.dumps(payload), timeout=5)
            
        return redirect(url_for('result', student_id=student_id))
    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>", 500

@app.route('/result/<student_id>')
def result(student_id):
    info = student_submissions.get(student_id)
    return render_template('result.html', info=info)

@app.route('/admin')
def admin():
    return render_template('admin.html', 
                           all_submissions=student_submissions, 
                           class_results=None, 
                           sheet_url=SHEET_URL)

@app.route('/assign_classes', methods=['POST'])
def assign_classes():
    class_assignments = {}
    class_stats = {}
    
    # 과목별 인원 분류
    for sid, info in student_submissions.items():
        for subject in info.get('subjects', []):
            if subject not in class_assignments:
                class_assignments[subject] = []
            class_assignments[subject].append(f"{info['name']}({sid})")
    
    # 분반 상태 진단 (1번 아이디어: 분반 제안)
    for subject, students in class_assignments.items():
        count = len(students)
        if count >= 20: status, color = "분반 권장", "danger"
        elif count <= 5: status, color = "폐강 위기", "warning"
        else: status, color = "정상", "success"
        class_stats[subject] = {"count": count, "status": status, "color": color}
        
    return render_template('admin.html', 
                           all_submissions=student_submissions, 
                           class_results=class_assignments,
                           class_stats=class_stats,
                           sheet_url=SHEET_URL)

if __name__ == '__main__':
    app.run(debug=True)
