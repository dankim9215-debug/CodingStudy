import os
import requests
from github import Github, Auth
from datetime import datetime, timedelta

# 1. 환경 설정
GITHUB_TOKEN = os.getenv("GH_TOKEN") 
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

STUDY_MEMBERS = {
    "김동현": "dankim9215-debug/CodingStudy",
    "김지연": "JiyeonKim017/coding-test",
}

# [추가] 허용할 확장자 리스트 (필요한 언어를 여기에 추가만 하면 됩니다)
ALLOWED_EXTENSIONS = ('.py', '.sql', '.java', '.cpp', '.js', '.c', '.cs', '.ts')

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
            default_branch = repo.default_branch
            commits = repo.get_commits(since=since)
            total_score, solved_list = 0, set()
            details = [] 

            for commit in commits:
                for file in commit.files:
                    path = file.filename
                    
                    # 리스트에 등록된 확장자 중 하나로 끝나는지 확인
                    if not path.lower().endswith(ALLOWED_EXTENSIONS):
                        continue

                    parts = path.split('/')
                    if len(parts) >= 3:
                        platform, difficulty, problem_id = parts[0], parts[1], parts[2]

                        if problem_id not in solved_list:
                            score = get_score(platform, difficulty)
                            if score > 0:
                                total_score += score
                                solved_list.add(problem_id)
                                
                                github_link = f"https://github.com/{repo_path}/blob/{default_branch}/{path}"
                                link_text = f"<{github_link}|{problem_id}>"
                                
                                details.append(f"    └ {link_text} ({score}점)")
            
            status = "✅ 달성" if total_score >= 20 else f"❌ 미달 ({20 - total_score}점 부족)"
            report.append(f"• *{name}*: {total_score}점 ({status})")
            if details: report.extend(details)
            else: report.append("    └ 이번 주 풀이 내역 없음")
            report.append("") 
            
        except Exception as e:
            report.append(f"• *{name}*: 조회 실패 (권한/주소 확인)\n")
    
    return "\n".join(report)

if __name__ == "__main__":
    try:
        content = check_weekly_progress()
        title = "☀️ *코딩 스터디 진행 현황*"
        requests.post(SLACK_WEBHOOK_URL, json={"text": f"{title}\n{content}"}, timeout=10)
    except Exception as e:
        print(f"오류: {e}")
