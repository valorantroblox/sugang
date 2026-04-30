import requests
import json
import traceback
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
# 팝업 메시지나 세션을 사용할 때 필요한 비밀키 (아무 문자나 넣어도 됨)
app.secret_key = "kis_pilot_secret" 

# 1. 구글 앱스 스크립트 배포 후 받은 웹 앱 URL을 여기에 넣으세요
GAS_URL = "https://script.google.com/macros/s/AKfycby87qx58UKlc--Lpqd6OpOe8l2_IJrEZb-gpduBVWpFZILe64joczwQjVKc5jPdLtO2/exec"

# 2. 관리자 페이지에서 바로 갈 구글 스프레드시트 주소를 여기에 넣으세요
SHEET_URL = "https://docs.google.com/spreadsheets/d/1fM3e_ELwfhhW45zLqXZIwjQ_Fd2FDSwwcUXOeWxICoM/edit?hl=ko&gid=0#gid=0"

# 수강신청 과목 데이터
SUBJECTS_DATA = {
    "11": {
        "1학기": {
            "국어/수학/영어": [
                {"name": "문학과 콘텐츠", "type": "진로"},
                {"name": "토론과 글쓰기", "type": "진로"},
                {"name": "미디어와 국어생활", "type": "진로"},
                {"name": "대수", "type": "일반"},
                {"name": "미적분Ⅰ", "type": "일반"},
                {"name": "기하", "type": "진로"},
                {"name": "인공지능 수학", "type": "진로"},
                {"name": "Critical Literacy in English", "type": "진로"},
                {"name": "English Literature", "type": "진로"},
                {"name": "History of Early Civilizations", "type": "진로"}
            ],
            "사회/과학": [
                {"name": "사회와 문화", "type": "일반"},
                {"name": "세계사", "type": "일반"},
                {"name": "윤리와 사상", "type": "일반"},
                {"name": "지리적 사고와 탐구", "type": "진로"},
                {"name": "한국 사회의 법과 정치", "type": "진로"},
                {"name": "심리학의 기초", "type": "진로"},
                {"name": "경제학 원론", "type": "진로"},
                {"name": "물리학", "type": "일반"},
                {"name": "화학", "type": "일반"},
                {"name": "생명과학", "type": "일반"},
                {"name": "지구과학", "type": "일반"},
                {"name": "기후 변화와 지속 가능한 세계", "type": "융합"},
                {"name": "Introduction to Chemistry", "type": "진로"},
                {"name": "Introduction to Biology", "type": "진로"}
            ],
            "기술·가정/정보/예술/기타": [
                {"name": "데이터 과학", "type": "진로"},
                {"name": "실용 경제", "type": "진로"},
                {"name": "스마트 시티와 미래", "type": "융합"},
                {"name": "창의 공학 설계 기초", "type": "진로"},
                {"name": "미술 전공 실기 기초", "type": "진로"},
                {"name": "시각디자인 기초", "type": "진로"},
                {"name": "실용 음악의 이해", "type": "진로"},
                {"name": "음악 연주와 창작", "type": "진로"},
                {"name": "베트남의 지리와 역사", "type": "진로"},
                {"name": "21세기 문학탐구", "type": "진로"},
                {"name": "한국어 회화", "type": "진로"}
            ],
            "제2외국어": [
                {"name": "베트남어 회화", "type": "진로"},
                {"name": "비즈니스 베트남어", "type": "진로"}
            ]
        },
        "2학기": {
            "국어/수학/영어": [
                {"name": "미디어와 창의적 표현", "type": "융합"},
                {"name": "현대문학의 이해", "type": "진로"},
                {"name": "고급 미적분", "type": "진로"},
                {"name": "고급 대수", "type": "융합"},
                {"name": "실용 통계", "type": "진로"},
                {"name": "수학 과제 탐구", "type": "진로"},
                {"name": "Contemporary Literacy in English", "type": "진로"},
                {"name": "American Literature", "type": "진로"},
                {"name": "Adventures in World History", "type": "진로"}
            ],
            "사회/과학": [
                {"name": "역사로 탐구하는 현대 세계", "type": "융합"},
                {"name": "금융과 경제생활", "type": "융합"},
                {"name": "여행 지리", "type": "진로"},
                {"name": "국제 관계의 이해", "type": "진로"},
                {"name": "윤리와 사회문제 탐구", "type": "융합"},
                {"name": "인문학과 윤리", "type": "진로"},
                {"name": "고급 물리학", "type": "진로"},
                {"name": "고급 화학", "type": "진로"},
                {"name": "고급 생명과학", "type": "진로"},
                {"name": "고급 지구과학", "type": "진로"},
                {"name": "융합과학 탐구", "type": "진로"},
                {"name": "Comprehensive Chemistry", "type": "진로"},
                {"name": "Comprehensive Biology", "type": "진로"},
                {"name": "Comprehensive Engineering", "type": "진로"}
            ],
            "기술·가정/정보/예술/기타": [
                {"name": "소프트웨어와 생활", "type": "융합"},
                {"name": "컴퓨터 그래픽 기초", "type": "진로"},
                {"name": "미술 감상과 비평", "type": "진로"},
                {"name": "음악 감상과 비평", "type": "진로"},
                {"name": "비즈니스 엑셀", "type": "진로"},
                {"name": "비즈니스 경제", "type": "진로"},
                {"name": "동남아 사회문화탐구", "type": "융합"},
                {"name": "한국어 발표와 토론", "type": "진로"},
                {"name": "프레젠테이션 화법", "type": "융합"}
            ],
            "제2외국어": [
                {"name": "비즈니스 베트남어 회화", "type": "진로"},
                {"name": "베트남어 문화탐구", "type": "융합"}
            ]
        }
    }
}
# 관리자용 임시 메모리 저장소
student_submissions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/select_subjects', methods=['POST'])
def select_subjects():
    try:
        student_id = request.form.get('student_id')
        student_name = request.form.get('student_name')
        grade = request.form.get('grade')
        semester = request.form.get('semester')

        # --- 중복 신청 방지 로직 ---
        try:
            # 구글 시트에 이미 등록된 학번 리스트 가져오기 (GET 요청)
            response = requests.get(GAS_URL, timeout=5)
            existing_ids = response.json()
            if student_id in existing_ids:
                return f"<script>alert('{student_id} 학번은 이미 신청 완료되었습니다.'); window.location.href='/';</script>"
        except Exception as e:
            print(f"중복 체크 건너뜀 (구글 응답 없음): {e}")
        # -------------------------

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
        grade = request.form.get('grade')  # 학년 추가
        semester = request.form.get('semester')  # 학기 추가
        selected_list = request.form.getlist('selected_subjects')
        subjects_str = ", ".join(selected_list)
        
        if student_id:
            # 관리자 페이지 표시용 데이터에 학년/학기 추가
            student_submissions[student_id] = {
                'name': student_name,
                'grade': grade,        # 추가
                'semester': semester,  # 추가
                'subjects': selected_list,
                'total_credits': len(selected_list) * 4
            }
            
            # 구글 시트로 보낼 때도 필요하다면 추가 (선택사항)
            payload = {
                "student_id": student_id,
                "student_name": student_name,
                "grade": grade,
                "semester": semester,
                "subjects": subjects_str
            }
            requests.post(GAS_URL, data=json.dumps(payload), timeout=5)
            
        return redirect(url_for('result', student_id=student_id))
    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>", 500

@app.route('/result/<student_id>')
def result(student_id):
    data = student_submissions.get(student_id, {})
    return render_template('result.html', data=data)

@app.route('/admin')
def admin():
    try:
        return render_template('admin.html', 
                               all_submissions=student_submissions, 
                               class_results=None, 
                               sheet_url=SHEET_URL)
    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>", 500

@app.route('/assign_classes', methods=['POST'])
def assign_classes():
    try:
        class_assignments = {}
        class_stats = {}
        combination_stats = {} # 과목 조합 통계
        
        # 1. 반편성 및 인원 통계 계산
        for sid, info in student_submissions.items():
            current_student_subjects = info.get('subjects', [])
            
            # 과목별 명단 구성
            for subject in current_student_subjects:
                if subject not in class_assignments:
                    class_assignments[subject] = []
                class_assignments[subject].append(f"{info['name']}({sid})")
            
            # 2. 과목 조합 분석 (예: 화학을 듣는 애가 생명도 듣는가?)
            for i in range(len(current_student_subjects)):
                for j in range(i + 1, len(current_student_subjects)):
                    # 과목 쌍을 이름순으로 정렬해서 '화학-생명'과 '생명-화학'을 같은 걸로 취급
                    combo = tuple(sorted([current_student_subjects[i], current_student_subjects[j]]))
                    combination_stats[combo] = combination_stats.get(combo, 0) + 1

        # 인원수에 따른 분반 제안
        for subject, students in class_assignments.items():
            count = len(students)
            if count >= 20: status, color = "분반 권장", "danger"
            elif count <= 5: status, color = "폐강 위기", "warning"
            else: status, color = "정상", "success"
            class_stats[subject] = {"count": count, "status": status, "color": color}

        # 가장 많이 겹치는 조합 TOP 3 추출
        sorted_combos = sorted(combination_stats.items(), key=lambda x: x[1], reverse=True)[:3]
        top_combos = [{"subjects": f"{c[0][0]} + {c[0][1]}", "count": c[1]} for c in sorted_combos]

        return render_template('admin.html', 
                               all_submissions=student_submissions, 
                               class_results=class_assignments,
                               class_stats=class_stats,
                               top_combos=top_combos, # 인기 조합 데이터 추가
                               sheet_url=SHEET_URL)
    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>", 500

if __name__ == '__main__':
    app.run(debug=True)
