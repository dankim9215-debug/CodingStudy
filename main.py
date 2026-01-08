import os
import requests
import re
from github import Github, Auth
from datetime import datetime, timedelta

# 1. 환경 설정
GITHUB_TOKEN = os.getenv("GH_TOKEN") 
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

STUDY_MEMBERS = {
    "강유정": "k-yujeong/stu",
    "김동현": "dankim9215-debug/CodingStudy",
    "김동환": "hwan1111/Coding-Test",
    "김수빈": "subin912/codingtest",
    "김재욱": "finstts99/baekjoon",
    "김지연": "JiyeonKim017/coding-test",
    "신나경": "nakyungs/codingtest",
    "안유민": "DEVELOPERYUMIN/CodingTest",
    "이수현": "shjade/codingtest",
    "조혜정": "HYEJEONG-JO/CO_test"
}

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
    
    # 한국 시간(KST) 기준 시간 설정
    now_kst = datetime.utcnow() + timedelta(hours=9)
    days_since_friday = (now_kst.weekday() - 4) % 7
    since_kst = (now_kst - timedelta(days=days_since_friday)).replace(hour=19, minute=0, second=0, microsecond=0)
    if now_kst < since_kst:
        since_kst -= timedelta(days=7)
    
    report = [f"🕒 집계 시각: {now_kst.strftime('%m/%d %H:%M')} (KST)"]
    report.append(f"📅 기준 시작: {since_kst.strftime('%m/%d %H:%M')} (KST)\n")

    for name, repo_path in STUDY_MEMBERS.items():
        try:
            repo = g.get_repo(repo_path)
            default_branch = repo.default_branch
            
            # [핵심 변경] 커밋 로그를 순회하지 않고, 마지막 커밋 시점의 전체 파일 트리(Tree)를 가져옵니다.
            # recursive=True를 통해 모든 하위 폴더의 파일을 한 번에 가져옵니다.
            tree = repo.get_git_tree(default_branch, recursive=True).tree
            
            total_score, solved_list = 0, set()
            details = [] 

            for file in tree:
                path = file.path
                
                # 1. 소스 코드 확장자 검사
                if not path.lower().endswith(ALLOWED_EXTENSIONS):
                    continue

                parts = path.split('/')
                
                # 2. 플랫폼 위치 탐색
                target_idx = -1
                for i, p in enumerate(parts):
                    if "백준" in p or "프로그래머스" in p:
                        target_idx = i
                        break
                
                if target_idx != -1 and len(parts) > target_idx + 2:
                    platform = parts[target_idx]
                    difficulty = parts[target_idx + 1]
                    problem_id = parts[target_idx + 2]

                    # 3. 문제 번호 형식 검사 (숫자로 시작해야 함, '1w task' 등 제외)
                    if not re.match(r'^\d+', problem_id):
                        continue

                    if problem_id not in solved_list:
                        score = get_score(platform, difficulty)
                        if score > 0:
                            total_score += score
                            solved_list.add(problem_id)
                            github_link = f"https://github.com/{repo_path}/blob/{default_branch}/{path}"
                            details.append(f"    └ <{github_link}|{problem_id}> ({score}점)")
            
            status = "✅ 달성" if total_score >= 20 else f"❌ 미달 ({20 - total_score}점 부족)"
            report.append(f"• *{name}*: {total_score}점 ({status})")
            if details: report.extend(details)
            else: report.append("    └ 현재 레포지토리에 풀이 내역 없음")
            report.append("") 
            
        except Exception as e:
            report.append(f"• *{name}*: 조회 실패\n")
    
    return "\n".join(report)

if __name__ == "__main__":
    try:
        content = check_weekly_progress()
        requests.post(SLACK_WEBHOOK_URL, json={"text": f"☀️ *코딩 스터디 현재 상태*\n{content}"}, timeout=10)
    except Exception as e:
        print(f"오류: {e}")
