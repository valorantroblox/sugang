from flask import Flask, render_template, request

app = Flask(__name__)

# 사진 데이터를 기반으로 한 전체 과목 리스트
SUBJECTS_DATA = {
    "11": {
        "1학기": {
            "국어/수학/영어": [
                {"name": "문학과 콘텐츠", "type": "진로"}, {"name": "토론과 글쓰기", "type": "진로"},
                {"name": "미디어와 국어생활", "type": "진로"}, {"name": "대수", "type": "일반"},
                {"name": "미적분Ⅰ", "type": "일반"}, {"name": "기하", "type": "진로"},
                {"name": "인공지능 수학", "type": "진로"}, {"name": "Critical Literacy in English", "type": "진로"},
                {"name": "English Literature", "type": "진로"}, {"name": "History of Early Civilizations", "type": "진로"}
            ],
            "사회/과학": [
                {"name": "사회와 문화", "type": "일반"}, {"name": "세계사", "type": "일반"},
                {"name": "윤리와 사상", "type": "일반"}, {"name": "지리적 사고와 탐구", "type": "진로"},
                {"name": "한국 사회의 법과 정치", "type": "진로"}, {"name": "심리학의 기초", "type": "진로"},
                {"name": "경제학 원론", "type": "진로"}, {"name": "물리학", "type": "일반"},
                {"name": "화학", "type": "일반"}, {"name": "생명과학", "type": "일반"},
                {"name": "지구과학", "type": "일반"}, {"name": "기후 변화와 지속 가능한 세계", "type": "융합"},
                {"name": "Introduction to Chemistry", "type": "진로"}, {"name": "Introduction to Biology", "type": "진로"}
            ],
            "기술·가정/정보/예술/기타": [
                {"name": "데이터 과학", "type": "진로"}, {"name": "실용 경제", "type": "진로"},
                {"name": "스마트 시티와 미래", "type": "융합"}, {"name": "창의 공학 설계 기초", "type": "진로"},
                {"name": "미술 전공 실기 기초", "type": "진로"}, {"name": "시각디자인 기초", "type": "진로"},
                {"name": "실용 음악의 이해", "type": "진로"}, {"name": "음악 연주와 창작", "type": "진로"},
                {"name": "베트남의 지리와 역사", "type": "진로"}, {"name": "21세기 문학탐구", "type": "진로"},
                {"name": "한국어 회화", "type": "진로"}
            ],
            "제2외국어": [
                {"name": "베트남어 회화", "type": "진로"}, {"name": "비즈니스 베트남어", "type": "진로"}
            ]
        },
        "2학기": {
            "국어/수학/영어": [
                {"name": "미디어와 창의적 표현", "type": "융합"}, {"name": "현대문학의 이해", "type": "진로"},
                {"name": "고급 미적분", "type": "진로"}, {"name": "고급 대수", "type": "융합"},
                {"name": "실용 통계", "type": "진로"}, {"name": "수학 과제 탐구", "type": "진로"},
                {"name": "Contemporary Literacy in English", "type": "진로"}, {"name": "American Literature", "type": "진로"},
                {"name": "Adventures in World History", "type": "진로"}
            ],
            "사회/과학": [
                {"name": "역사로 탐구하는 현대 세계", "type": "융합"}, {"name": "금융과 경제생활", "type": "융합"},
                {"name": "여행 지리", "type": "진로"}, {"name": "국제 관계의 이해", "type": "진로"},
                {"name": "윤리와 사회문제 탐구", "type": "융합"}, {"name": "인문학과 윤리", "type": "진로"},
                {"name": "고급 물리학", "type": "진로"}, {"name": "고급 화학", "type": "진로"},
                {"name": "고급 생명과학", "type": "진로"}, {"name": "고급 지구과학", "type": "진로"},
                {"name": "융합과학 탐구", "type": "진로"}, {"name": "Comprehensive Chemistry", "type": "진로"},
                {"name": "Comprehensive Biology", "type": "진로"}, {"name": "Comprehensive Engineering", "type": "진로"}
            ],
            "기술·가정/정보/예술/기타": [
                {"name": "소프트웨어와 생활", "type": "융합"}, {"name": "컴퓨터 그래픽 기초", "type": "진로"},
                {"name": "미술 감상과 비평", "type": "진로"}, {"name": "음악 감상과 비평", "type": "진로"},
                {"name": "비즈니스 엑셀", "type": "진로"}, {"name": "비즈니스 경제", "type": "진로"},
                {"name": "동남아 사회문화탐구", "type": "융합"}, {"name": "한국어 발표와 토론", "type": "진로"},
                {"name": "프레젠테이션 화법", "type": "융합"}
            ],
            "제2외국어": [
                {"name": "비즈니스 베트남어 회화", "type": "진로"}, {"name": "베트남어 문화탐구", "type": "융합"}
            ]
        }
    }
}

@app.route('/select_subjects', methods=['POST'])
def select_subjects():
    student_id = request.form.get('student_id')
    student_name = request.form.get('student_name')
    grade = request.form.get('grade')
    semester = request.form.get('semester')
    
    subjects = SUBJECTS_DATA.get(grade, {}).get(semester, {})
    
    # 사진 하단 기준 11학년은 28학점 목표
    target_credit = 28 if grade == "11" else 32 
    
    return render_template('select.html', 
                           student_id=student_id, 
                           student_name=student_name, 
                           grade=grade, 
                           semester=semester, 
                           subjects=subjects,
                           target_credit=target_credit)

if __name__ == '__main__':
    app.run(debug=True)
