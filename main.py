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

# 허용할 소스 코드 확장자
ALLOWED_EXTENSIONS = ('.py', '.sql', '.java', '.cpp', '.js', '.c', '.cs', '.ts')

def get_score(platform, difficulty):
    platform, difficulty = platform.strip(), difficulty.strip()
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
    
    # 한국 시간(KST) 강제 생성
    now_kst = datetime.utcnow() + timedelta(hours=9)
    days_since_friday = (now_kst.weekday() - 4) % 7
    since_kst = (now_kst - timedelta(days=days_since_friday)).replace(hour=19, minute=0, second=0, microsecond=0)
    
    if now_kst < since_kst:
        since_kst -= timedelta(days=7)
        
    since_utc = since_kst - timedelta(hours=9)
        
    report = [f"🕒 집계 시각: {now_kst.strftime('%m/%d %H:%M')} (KST)"]
    report.append(f"📅 기준 시작: {since_kst.strftime('%m/%d %H:%M')} (KST)\n")

    for name, repo_path in STUDY_MEMBERS.items():
        try:
            repo = g.get_repo(repo_path)
            default_branch = repo.default_branch
            commits = repo.get_commits(since=since_utc)
            
            total_score, solved_list = 0, set()
            details = [] 

            for commit in commits:
                for file in commit.files:
                    path = file.filename
                    
                    # 1. 파일 확장자 검사 (의미 없는 폴더/파일 제외)
                    if not path.lower().endswith(ALLOWED_EXTENSIONS):
                        continue

                    parts = path.split('/')
                    # 2. 폴더 깊이 검사 (최소 '플랫폼/난이도/문제명/파일' 구조여야 함)
                    if len(parts) >= 3:
                        p, d, pid = parts[0], parts[1], parts[2]
                        
                        # 3. 중복 방지 및 점수 계산
                        if pid not in solved_list:
                            score = get_score(p, d)
                            if score > 0:
                                total_score += score
                                solved_list.add(pid)
                                github_link = f"https://github.com/{repo_path}/blob/{default_branch}/{path}"
                                details.append(f"    └ <{github_link}|{pid}> ({score}점)")
            
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
        title = "☀️ *코딩 스터디 진행 현황*"
        requests.post(SLACK_WEBHOOK_URL, json={"text": f"{title}\n{content}"}, timeout=10)
    except Exception as e:
        print(f"오류: {e}")
