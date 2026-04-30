from flask import Flask, render_template, request, redirect, url_for
import traceback

app = Flask(__name__)

# 데이터 저장소
student_submissions = {}

# [Raw].xlsx 파일의 실제 과목명을 100% 반영한 데이터
SUBJECTS_DATA = {
    "11": {
        "1학기": {
            "기초/탐구": ["대수", "미적분Ⅰ", "문학과 콘텐츠", "토론과 글쓰기", "Essential English Grammar", "Essential Academic Reading", "미디어와 국어생활"],
            "사회/과학": ["사회와 문화", "세계사", "생명과학", "화학", "윤리문제 탐구", "Fundamentals of Psychology", "Introduction to Chemistry"],
            "예술/기타": ["데이터 과학", "Business Studies", "윤리문제 탐구"]
        }
    }
}

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"메인 화면(index.html)을 찾을 수 없습니다. templates 폴더를 확인하세요: {str(e)}", 500

@app.route('/select_subjects', methods=['POST'])
def select_subjects():
    try:
        grade = request.form.get('grade')
        semester = request.form.get('semester')
        student_id = request.form.get('student_id')
        student_name = request.form.get('student_name')
        
        # 데이터가 잘 넘어왔는지 검사
        if not all([grade, semester, student_id, student_name]):
            return "입력 정보가 부족합니다. 학번과 이름을 모두 입력했는지 확인하세요.", 400
            
        grade_data = SUBJECTS_DATA.get(grade, {})
        subjects = grade_data.get(semester, {})
        
        if not subjects:
            return f"{grade}학년 {semester}에 대한 과목 데이터가 코드에 없습니다.", 404
            
        # KIS 11학년 기준 학점
        target_credit = 28 if grade == "11" else 32
        
        return render_template('select.html', grade=grade, semester=semester, 
                               student_id=student_id, student_name=student_name, 
                               subjects=subjects, target_credit=target_credit)
    except Exception:
        # 에러 발생 시 상세한 파이썬 에러 로그를 화면에 출력
        return f"<h3>서버 내부 에러 발생</h3><pre>{traceback.format_exc()}</pre>", 500

@app.route('/submit', methods=['POST'])
def submit():
    try:
        student_id = request.form.get('student_id')
        student_name = request.form.get('student_name')
        selected_list = request.form.getlist('selected_subjects')
        
        if student_id:
            student_submissions[student_id] = {
                'name': student_name,
                'subjects': selected_list,
                'total_credits': len(selected_list) * 4
            }
        return redirect(url_for('result', student_id=student_id))
    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>", 500

@app.route('/result/<student_id>')
def result(student_id):
    data = student_submissions.get(student_id, {})
    return render_template('result.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
