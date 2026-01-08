import os
import requests
from github import Github
from datetime import datetime, timedelta

# 1. 환경 설정
GITHUB_TOKEN = os.getenv("GH_TOKEN") 
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL" # 본인의 웹훅 주소
STUDY_MEMBERS = {
    "홍길동": "username1/repo-name",
    "김철수": "username2/repo-name",
}

def get_score(platform, difficulty):
    if platform == "Programmers":
        try:
            # 프로그래머스 폴더명이 숫자가 아닌 경우(예: 'PCCE기출') 대비
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
    """가장 최근 지난 금요일 오후 7시 시점을 계산"""
    now = datetime.now()
    # 요일 계산 (월=0, ..., 금=4, ...)
    days_since_friday = (now.weekday() - 4) % 7
    last_friday = now - timedelta(days=days_since_friday)
    # 시간을 오후 7시(19:00)로 설정
    return last_friday.replace(hour=19, minute=0, second=0, microsecond=0)

def check_weekly_progress():
    g = Github(GITHUB_TOKEN)
    
    # 금요일 19:00를 기준으로 그 이후에 올라온 것만 집계
    # 만약 지금이 금요일 17:00라면 지난주 금요일 19:00 ~ 현재까지 집계됨
    since = get_last_friday_7pm()
    
    # 만약 현재 시각이 금요일 19:00 전이라면 지난주 금요일 19:00를 시작점으로 잡음
    if datetime.now() < since:
        since = since - timedelta(days=7)
        
    report = []
    report.append(f"📅 집계 기간: {since.strftime('%m/%d %H:%M')} ~ 현재")

    for name, repo_path in STUDY_MEMBERS.items():
        try:
            repo = g.get_repo(repo_path)
            commits = repo.get_commits(since=since)
            
            total_score = 0
            solved_list = set()

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
