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
            tree = repo.get_git_tree(default_branch, recursive=True).tree
            
            total_score = 0
            solved_list = set()
            # 난이도별 개수를 저장할 딕셔너리
            summary_dict = {} 

            for file in tree:
                path = file.path
                if not path.lower().endswith(ALLOWED_EXTENSIONS):
                    continue

                parts = path.split('/')
                target_idx = -1
                for i, p in enumerate(parts):
                    if "백준" in p or "프로그래머스" in p:
                        target_idx = i
                        break
                
                if target_idx != -1 and len(parts) > target_idx + 2:
                    platform = parts[target_idx]
                    difficulty = parts[target_idx + 1]
                    problem_id = parts[target_idx + 2]

                    if not re.match(r'^\d+', problem_id):
                        continue

                    if problem_id not in solved_list:
                        score = get_score(platform, difficulty)
                        if score > 0:
                            total_score += score
                            solved_list.add(problem_id)
                            
                            # 요약용 카테고리 이름 생성 (예: 백준 Gold 또는 프로그래머스 Lv.2)
                            category = f"{platform} {difficulty}"
                            summary_dict[category] = summary_dict.get(category, 0) + 1
            
            status = "✅ 달성" if total_score >= 20 else f"❌ 미달 ({20 - total_score}점 부족)"
            report.append(f"• *{name}*: {total_score}점 ({status})")
            
            # 요약 내역 추가
            if summary_dict:
                summary_items = [f"{cat}: {count}개" for cat, count in summary_dict.items()]
                report.append(f"    └ " + ", ".join(summary_items))
            else:
                report.append("    └ 현재 풀이 내역 없음")
            report.append("") 
            
        except Exception as e:
            report.append(f"• *{name}*: 조회 실패\n")
    
    return "\n".join(report)

if __name__ == "__main__":
    try:
        content = check_weekly_progress()
        requests.post(SLACK_WEBHOOK_URL, json={"text": f"☀️ *코딩 스터디 진행 현황*\n{content}"}, timeout=10)
    except Exception as e:
        print(f"오류: {e}")"오류: {e}")
