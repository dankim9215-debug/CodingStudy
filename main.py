import os
import requests
from github import Github
from datetime import datetime, timedelta

# 1. 환경 설정
GITHUB_TOKEN = os.getenv("GH_TOKEN") 

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

STUDY_MEMBERS = {
    "김동현": "dankim9215-debug/CodingStudy",
    "강유정": "k-yujeong/stu",
}

def get_score(platform, difficulty):
    # 한글 디렉토리명 '프로그래머스' 대응
    if platform == "프로그래머스":
        try:
            return int(difficulty)
        except:
            return 0
    
    # 한글 디렉토리명 '백준' 대응
    if platform == "백준":
        mapping = {
            'Bronze': 1, 'Silver': 2, 'Gold': 3, 
            'Platinum': 4, 'Diamond': 5, 'Unrated': 0
        }
        return mapping.get(difficulty, 0)
    return 0

def get_last_friday_7pm():
    now = datetime.now()
    days_since_friday = (now.weekday() - 4) % 7
    last_friday = now - timedelta(days=days_since_friday)
    last_friday_7pm = last_friday.replace(hour=19, minute=0, second=0, microsecond=0)
    if now < last_friday_7pm:
        last_friday_7pm -= timedelta(days=7)
    return last_friday_7pm

def check_weekly_progress():
    g = Github(GITHUB_TOKEN)
    since = get_last_friday_7pm()
    report = []
    report.append(f"📅 집계 시작: {since.strftime('%m/%d %H:%M')}")

    for name, repo_path in STUDY_MEMBERS.items():
        try:
            repo = g.get_repo(repo_path)
            commits = repo.get_commits(since=since)
            total_score, solved_list = 0, set()

            for commit in commits:
                for file in commit.files:
                    # 예: 백준/Bronze/문제명/파일.py -> ['백준', 'Bronze', '문제명', '파일.py']
                    parts = file.filename.split('/')
                    if len(parts) >= 3:
                        platform = parts[0]   # '백준' 또는 '프로그래머스'
                        difficulty = parts[1] # 'Bronze' 또는 '0' (레벨)
                        problem_id = parts[2] # '3052.나머지'

                        if problem_id not in solved_list:
                            score = get_score(platform, difficulty)
                            if score > 0:
                                total_score += score
                                solved_list.add(problem_id)
            
            status = "✅ 달성" if total_score >= 20 else f"❌ 미달 ({20 - total_score}점 부족)"
            report.append(f"• *{name}*: {total_score}점 ({status})")
        except Exception as e:
            report.append(f"• *{name}*: 데이터 조회 오류 (레포 확인 필요)")
    
    return "\n".join(report)

def send_to_slack(text):
    payload = {"text": text}
    # 응답 결과 확인을 위해 response 변수 사용
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    return response

if __name__ == "__main__":
    report_content = check_weekly_progress()
    now = datetime.now()
    
    if now.weekday() == 4 and 16 <= now.hour <= 18:
        title = "🏁 *[최종] 이번 주 코딩 스터디 마감 결과*"
    else:
        title = f"☀️ *[현황] 코딩 스터디 진행 현황 ({now.strftime('%m/%d')})*"
        
    final_message = f"{title}\n\n{report_content}"
    
    print(f"전송 메시지:\n{final_message}")
    res = send_to_slack(final_message)
    print(f"슬랙 전송 결과: {res.status_code}, {res.text}")
