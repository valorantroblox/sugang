import requests
import json
import traceback
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "kis_secret_key" # 팝업(flash) 메시지를 위해 필요함

GAS_URL = "https://script.google.com/macros/s/AKfycbzH3UsmH5l0jCqkBEpXDrf4LEoON7-WGprnHDfo0ax_sS-kN7ZHvSkpejuQNURxgcFS/exec"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1fM3e_ELwfhhW45zLqXZIwjQ_Fd2FDSwwcUXOeWxICoM/edit?hl=ko&gid=0#gid=0" # 관리자용 링크

SUBJECTS_DATA = {
    "11": {
        "1학기": {
            "기초/탐구": ["대수", "미적분Ⅰ", "문학과 콘텐츠", "토론과 글쓰기", "Essential English Grammar", "Essential Academic Reading", "미디어와 국어생활"],
            "사회/과학": ["사회와 문화", "세계사", "생명과학", "화학", "윤리문제 탐구", "Fundamentals of Psychology", "Introduction to Chemistry"],
            "예술/기타": ["데이터 과학", "Business Studies"]
        }
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/select_subjects', methods=['POST'])
def select_subjects():
    student_id = request.form.get('student_id')
    
    # 1. 구글 시트에서 기존 학번 리스트 가져오기
    try:
        response = requests.get(GAS_URL)
        existing_ids = response.json() # ['10421', '10422', ...] 형태
    except:
        existing_ids = []

    # 2. 중복 체크
    if student_id in existing_ids:
        # 이 메시지가 HTML의 alert 팝업으로 뜰 거야
        return "<script>alert('이미 신청 완료된 학번입니다!'); window.location.href='/';</script>"

    # 중복 아니면 과목 선택 페이지로 진행
    grade = request.form.get('grade')
    semester = request.form.get('semester')
    student_name = request.form.get('student_name')
    subjects = SUBJECTS_DATA.get(grade, {}).get(semester, {})
    target_credit = 28 if grade == "11" else 32
    
    return render_template('select.html', grade=grade, semester=semester, 
                           student_id=student_id, student_name=student_name, 
                           subjects=subjects, target_credit=target_credit)

# ... submit, result 등 기존 코드 동일 ...

@app.route('/admin')
def admin():
    # 관리자 페이지에 시트 바로가기 링크 전달
    return render_template('admin.html', sheet_url=SHEET_URL)
