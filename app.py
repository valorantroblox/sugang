from flask import Flask, render_template, request, redirect, url_for, make_response
import csv
from io import StringIO

app = Flask(__name__)

# 데이터 저장소 (Vercel에서는 재배포/슬립 시 초기화됨)
student_submissions = {}

# KIS 교과과정 데이터
SUBJECTS_DATA = {
    "11": {
        "1학기": {
            "기초/탐구": ["문학과 콘텐츠", "독서와 국어생활", "토론과 글쓰기", "대수", "미적분I", "Essential Academic Reading"],
            "사회/과학": ["세계사", "사회와 문화", "윤리와 사상", "기후 변화와 지속 가능한 세계", "물리학I", "화학I", "생명과학I"],
            "예술/기타": ["시/뉴미디어 문학", "미술 전공 실기 기초", "데이터 과학", "실용 베트남어"]
        },
        "2학기": {
            "기초/탐구": ["주제 탐구 독서", "심화 국어", "삶과 글쓰기", "미디어와 비판적 사고", "확률과 통계", "미적분II"],
            "사회/과학": ["현대사회와 윤리", "세계 시민과 지리", "경제", "정치", "물리적 실험", "화학 실험", "생명과학 실험"],
            "예술/기타": ["포스트모던음악", "미술 전공 실기 응용", "소프트웨어와 생활", "베트남의 사회와 문화"]
        }
    },
    "12": {
        "1학기": {
            "국영수 심화": ["21세기 문학탐구", "미디어와 창의적 표현", "고급 미적분", "수학과제 탐구", "기하", "인공지능 수학"],
            "사과탐 심화": ["원리와 사상", "한국지리 탐구", "법과 사회", "사회문제 탐구", "역학과 에너지", "전자기와 양자"],
            "예술/IT/기타": ["음악 연주와 창작", "미술 전공 실기 심화", "정보과학 과제연구", "비즈니스 엑셀"]
        },
        "2학기": {
            "국영수 심화": ["문학과 여행", "프레젠테이션 화법", "글로벌 이슈 글쓰기", "고급 대수", "실용 통계", "수학 실험"],
            "사과탐 심화": ["국제 관계의 이해", "인문학적 윤리", "여행지리", "역사로 탐구하는 현대 세계", "금융과 경제생활", "고급 물리", "고급 화학"],
            "예술/IT/기타": ["음악 감상과 비평", "미술 감상과 비평", "베트남어 회화", "베트남 사회문화탐구"]
        }
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/select_subjects', methods=['POST'])
def select_subjects():
    grade = request.form.get('grade')
    semester = request.form.get('semester')
    student_id = request.form.get('student_id')
    student_name = request.form.get('student_name')
    subjects = SUBJECTS_DATA.get(grade, {}).get(semester, {})
    target_credit = 28 if grade == "11" else 32
    return render_template('select.html', grade=grade, semester=semester, 
                           student_id=student_id, student_name=student_name, 
                           subjects=subjects, target_credit=target_credit)

@app.route('/submit', methods=['POST'])
def submit():
    student_id = request.form.get('student_id')
    student_name = request.form.get('student_name')
    grade = request.form.get('grade')
    semester = request.form.get('semester')
    selected_list = request.form.getlist('selected_subjects')
    
    if student_id:
        student_submissions[student_id] = {
            'name': student_name, 'grade': grade, 'semester': semester,
            'subjects': selected_list, 'total_credits': len(selected_list) * 4
        }
    return redirect(url_for('result', student_id=student_id))

@app.route('/result/<student_id>')
def result(student_id):
    data = student_submissions.get(student_id, {})
    return render_template('result.html', data=data)

# --- 어드민 & 반 편성 통합 ---
@app.route('/admin')
def admin():
    # 데이터가 없을 때를 대비해 기본값 설정
    return render_template('admin.html', all_submissions=student_submissions, class_results=None)

@app.route('/assign_classes', methods=['POST'])
def assign_classes():
    class_assignments = {}
    if student_submissions:
        for sid, info in student_submissions.items():
            for subject in info['subjects']:
                if subject not in class_assignments:
                    class_assignments[subject] = []
                class_assignments[subject].append(f"{info['name']}({sid})")
    
    return render_template('admin.html', 
                           all_submissions=student_submissions, 
                           class_results=class_assignments)

@app.route('/download_excel')
def download_excel():
    si = StringIO()
    si.write('\ufeff')
    cw = csv.writer(si)
    cw.writerow(['학번', '이름', '학년', '학기', '선택과목', '총학점'])
    for sid, info in student_submissions.items():
        cw.writerow([sid, info['name'], info['grade'], info['semester'], ", ".join(info['subjects']), info['total_credits']])
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=kis_list.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@app.route('/select_subjects', methods=['POST'])
def select_subjects():
    # 폼에서 넘어온 데이터 안전하게 가져오기
    grade = request.form.get('grade')
    semester = request.form.get('semester')
    student_id = request.form.get('student_id')
    student_name = request.form.get('student_name')

    # 데이터가 하나라도 없으면 다시 메인으로 돌려보내서 에러 방지
    if not all([grade, semester, student_id, student_name]):
        return redirect(url_for('index'))

    # 학년/학기에 맞는 과목 리스트 가져오기
    grade_data = SUBJECTS_DATA.get(grade, {})
    subjects = grade_data.get(semester, {})

    # 과목 데이터가 비어있을 경우 에러 방지
    if not subjects:
        return "선택 가능한 과목 데이터가 없습니다. 학년과 학기를 확인해주세요.", 400

    # KIS 기준 학점 설정
    target_credit = 28 if grade == "11" else 32

    return render_template('select.html', 
                           grade=grade, 
                           semester=semester, 
                           student_id=student_id, 
                           student_name=student_name, 
                           subjects=subjects, 
                           target_credit=target_credit)

if __name__ == '__main__':
    app.run(debug=True)
