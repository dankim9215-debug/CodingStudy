import os
import requests
from github import Github, Auth
from datetime import datetime, timedelta

# 1. 환경 설정
GITHUB_TOKEN = os.getenv("GH_TOKEN") 
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

STUDY_MEMBERS = {
    "김동현": "dankim9215-debug/CodingStudy",
    "강유정": "k-yujeong/stu",
}

def get_score(platform, difficulty):
    platform = platform.strip()
    difficulty = difficulty.strip()
    
    if "프로그래머스" in platform:
        try: return int(difficulty)
        except: return 0
    
    if "백준" in platform:
        mapping = {'Bronze': 1, 'Silver': 2, 'Gold': 3, 'Platinum': 4, 'Diamond': 5}
        return mapping.get(difficulty, 0)
    return 0

def make_problem_link(platform, problem_id):
    """문제 ID에서 숫자만 추출하여 해당 플랫폼의 링크를 생성합니다."""
    import re
    # 숫자만 추출 (예: '10811.바구니뒤집기' -> '10811')
    problem_num = re.findall(r'\d+', problem_id)
    if not problem_num:
        return problem_id
    
    num = problem_num[0]
    if "백준" in platform:
        return f"<https://www.acmicpc.net/problem/{num}|{problem_id}>"
    elif "프로그래머스" in platform:
        return f"<https://school.programmers.co.kr/learn/courses/30/lessons/{num}|{problem_id}>"
    return problem_id

def check_weekly_progress():
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    
    now = datetime.now()
    days_since_friday = (now.weekday() - 4) % 7
    since = (now - timedelta(days=days_since_friday)).replace(hour=19, minute=0, second=0, microsecond=0)
    if now < since:
        since -= timedelta(days=7)
        
    report = [f"🕒 집계 시각: {now.strftime('%m/%d %H:%M')}"]
    report.append(f"📅 기준 시작: {since.strftime('%m/%d %H:%M')}\n")

    for name, repo_path in STUDY_MEMBERS.items():
        try:
            repo = g.get_repo(repo_path)
            commits = repo.get_commits(since=since)
            total_score, solved_list = 0, set()
            details = [] 

            for commit in commits:
                for file in commit.files:
                    parts = file.filename.split('/')
                    if len(parts) >= 3:
                        platform, difficulty, problem_id = parts[0], parts[1], parts[2]

                        if problem_id not in solved_list:
                            score = get_score(platform, difficulty)
                            if score > 0:
                                total_score += score
                                solved_list.add(problem_id)
                                # 링크 생성 함수 호출
                                link_text = make_problem_link(platform, problem_id)
                                details.append(f"    └ {link_text} ({score}점)")
            
            status = "✅ 달성" if total_score >= 20 else f"❌ 미달 ({20 - total_score}점 부족)"
            report.append(f"• *{name}*: {total_score}점 ({status})")
            if details: report.extend(details)
            else: report.append("    └ 이번 주 풀이 내역 없음")
            report.append("") 
            
        except Exception as e:
            report.append(f"• *{name}*: 조회 실패\n")
    
    return "\n".join(report)

if __name__ == "__main__":
    try:
        content = check_weekly_progress()
        now = datetime.now()
        title = "☀️ *코딩 스터디 진행 현황*"
        if now.weekday() == 4 and 16 <= now.hour <= 18:
            title = "🏁 *[최종] 이번 주 코딩 스터디 마감 결과*"
            
        requests.post(SLACK_WEBHOOK_URL, json={"text": f"{title}\n{content}"}, timeout=10)
    except Exception as e:
        print(f"오류: {e}")
