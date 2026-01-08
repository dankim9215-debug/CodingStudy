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
        try:
            return int(difficulty)
        except:
            return 0
    
    if "백준" in platform:
        mapping = {
            'Bronze': 1, 'Silver': 2, 'Gold': 3, 
            'Platinum': 4, 'Diamond': 5
        }
        return mapping.get(difficulty, 0)
    return 0

def check_weekly_progress():
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    
    now = datetime.now()
    # 집계 기준일 (지난주 금요일 19:00) 계산
    days_since_friday = (now.weekday() - 4) % 7
    since = (now - timedelta(days=days_since_friday)).replace(hour=19, minute=0, second=0, microsecond=0)
    if now < since:
        since -= timedelta(days=7)
        
    # 슬랙 상단에 노출될 현재 집계 시간
    report = [f"🕒 집계 시각: {now.strftime('%m/%d %H:%M')}"]
    report.append(f"📅 기준 시작: {since.strftime('%m/%d %H:%M')}\n")

    for name, repo_path in STUDY_MEMBERS.items():
        try:
            repo = g.get_repo(repo_path)
            commits = repo.get_commits(since=since)
            total_score, solved_list = 0, set()
            details = [] # 슬랙에 표시할 문제 리스트

            for commit in commits:
                for file in commit.files:
                    parts = file.filename.split('/')
                    if len(parts) >= 3:
                        platform = parts[0]   
                        difficulty = parts[1] 
                        problem_id = parts[2] 

                        if problem_id not in solved_list:
                            score = get_score(platform, difficulty)
                            if score > 0:
                                total_score += score
                                solved_list.add(problem_id)
                                # 문제별 점수 기록
                                details.append(f"    └ {problem_id} ({score}점)")
            
            status = "✅ 달성" if total_score >= 20 else f"❌ 미달 ({20 - total_score}점 부족)"
            report.append(f"• *{name}*: {total_score}점 ({status})")
            
            # 인정된 문제가 있다면 리스트 추가
            if details:
                report.extend(details)
            else:
                report.append("    └ 이번 주 풀이 내역 없음")
            report.append("") # 멤버 간 줄바꿈
            
        except Exception as e:
            report.append(f"• *{name}*: 조회 실패 (권한/주소 확인)\n")
    
    return "\n".join(report)

if __name__ == "__main__":
    try:
        content = check_weekly_progress()
        now = datetime.now()
        
        # 금요일 오후 4~6시 사이면 [최종], 아니면 [현황]
        if now.weekday() == 4 and 16 <= now.hour <= 18:
            title = "🏁 *[최종] 이번 주 코딩 스터디 마감 결과*"
        else:
            title = "☀️ *코딩 스터디 진행 현황*"
            
        final_message = f"{title}\n{content}"
        
        res = requests.post(SLACK_WEBHOOK_URL, json={"text": final_message}, timeout=10)
        print(f"슬랙 전송 결과: {res.status_code}")
    except Exception as e:
        print(f"실행 중 오류 발생: {e}")
