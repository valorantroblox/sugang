from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os

app = Flask(__name__)

# 데이터 저장소
student_submissions = {}

# KIS 교과 데이터 (실제 엑셀 내용 반영)
SUBJECTS_DATA = {
    "11": {
        "1학기": {
            "기초/탐구": ["대수", "미적분Ⅰ", "문학과 콘텐츠", "토론과 글쓰기", "Essential English Grammar", "Essential Academic Reading"],
            "사회/과학": ["사회와 문화", "세계사", "생명과학", "화학", "윤리문제 탐구", "Fundamentals of Psychology"],
            "예술/기타": ["데이터 과학", "Business Studies", "Introduction to Chemistry"]
        }
    }
}

# --- 파비콘 에러 방지 ---
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

        return render_template('select.html', 
                               grade=grade, semester=semester, 
                               student_id=student_id, student_name=student_name, 
                               subjects=subjects, target_credit=target_credit)
    except Exception as e:
        return f"Error: {str(e)}", 500

# ... (나머지 submit, admin 함수 등은 이전과 동일)
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
