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
        # 난이도 문자열에 따른 점수 매핑
        mapping = {
            'Bronze': 1, 'Silver': 2, 'Gold': 3, 
            'Platinum': 4, 'Diamond': 5
        }
        return mapping.get(difficulty, 0)
    return 0

def check_weekly_progress():
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    
    # 지난 금요일 19:00 기준 설정
    now = datetime.now()
    days_since_friday = (now.weekday() - 4) % 7
    since = (now - timedelta(days=days_since_friday)).replace(hour=19, minute=0, second=0, microsecond=0)
    if now < since:
        since -= timedelta(days=7)
        
    report = [f"📅 집계 시작: {since.strftime('%m/%d %H:%M')}"]

    for name, repo_path in STUDY_MEMBERS.items():
        try:
            repo = g.get_repo(repo_path)
            commits = repo.get_commits(since=since)
            total_score, solved_list = 0, set()

            for commit in commits:
                for file in commit.files:
                    # 경로 분석: 백준/Bronze/문제번호.이름/파일
                    parts = file.filename.split('/')
                    if len(parts) >= 3:
                        platform = parts[0]   # 백준 or 프로그래머스
                        difficulty = parts[1] # Bronze or 1
                        problem_id = parts[2] # 문제번호.이름 (중복방지 키)

                        if problem_id not in solved_list:
                            score = get_score(platform, difficulty)
                            if score > 0:
                                total_score += score
                                solved_list.add(problem_id)
            
            status = "✅ 달성" if total_score >= 20 else f"❌ 미달 ({20 - total_score}점 부족)"
            report.append(f"• *{name}*: {total_score}점 ({status})")
        except Exception as e:
            report.append(f"• *{name}*: 조회 실패 (권한/주소 확인 필요)")
    print(f"인정된 문제: {problem_id}")
    
    return "\n".join(report)

if __name__ == "__main__":
    try:
        content = check_weekly_progress()
        final_message = f"☀️ *코딩 스터디 현황*\n\n{content}"
        
        requests.post(SLACK_WEBHOOK_URL, json={"text": final_message}, timeout=10)
        print("정상적으로 실행되었습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")
