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
    if platform == "Programmers":
        try:
            return int(difficulty)
        except:
            return 0
    if platform == "Baekjoon":
        mapping = {
            'Bronze': 1, 'Silver': 2, 'Gold': 3, 
            'Platinum': 4, 'Diamond': 5, 'Unrated': 0
        }
        return mapping.get(difficulty, 0)
    return 0

def get_last_friday_7pm():
    now = datetime.now()
    # 요일 계산 (0:월, 1:화, 2:수, 3:목, 4:금, 5:토, 6:일)
    days_since_friday = (now.weekday() - 4) % 7
    last_friday = now - timedelta(days=days_since_friday)
    # 시간을 오후 7시(19:00)로 설정
    last_friday_7pm = last_friday.replace(hour=19, minute=0, second=0, microsecond=0)
    
    # 만약 현재 시각이 금요일 오후 7시 이전이라면, 지난주 금요일로 계산
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
                    parts = file.filename.split('/')
                    if len(parts) >= 3:
                        platform, difficulty, problem_id = parts[0], parts[1], parts[2]
                        if problem_id not in solved_list:
                            total_score += get_score(platform, difficulty)
                            solved_list.add(problem_id)
            
            status = "✅ 달성" if total_score >= 20 else f"❌ 미달 ({20 - total_score}점 부족)"
            report.append(f"• *{name}*: {total_score}점 ({status})")
        except Exception as e:
            report.append(f"• *{name}*: 데이터 조회 오류")
    
    return "\n".join(report)

def send_to_slack(text):
    payload = {"text": text}
    requests.post(SLACK_WEBHOOK_URL, json=payload)

if __name__ == "__main__":
    report_content = check_weekly_progress()
    now = datetime.now()
    
    # 금요일 오후 5시 리포트 (한국 시간 17시 부근)
    if now.weekday() == 4 and 16 <= now.hour <= 18:
        title = "🏁 *[최종] 이번 주 코딩 스터디 마감 결과*"
    else:
        title = f"☀️ *[현황] 코딩 스터디 진행 현황 ({now.strftime('%m/%d')})*"
        
    final_message = f"{title}\n\n{report_content}"
    send_to_slack(final_message)

if __name__ == "__main__":
    report_content = check_weekly_progress()
    # ... 기존 코드들 ...
    final_message = f"{title}\n\n{report_content}"
    
    # [추가] 슬랙 전송 직전에 출력을 찍어봅니다.
    print(f"전송할 메시지: {final_message}") 
    
    send_to_slack(final_message)
