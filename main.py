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
    "김재욱": "finstats99/baekjoon",
    "김지연": "JiyeonKim017/coding-test",
    "신나경": "nakyungs/codingtest",
    "안유민": "DEVELOPERYUMIN/CodingTest",
    "이수현": "shjade/codingtest",
    "조혜정": "HYEJEONG-JO/CO_test"
}

ALLOWED_EXTENSIONS = ('.py', '.sql', '.java', '.cpp', '.js', '.c', '.cs', '.ts')

# 정렬 순서 정의
BAEKJOON_TIERS = ['Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Ruby']

def get_score(platform, difficulty):
    platform, difficulty = platform.strip(), difficulty.strip()
    
    if "프로그래머스" in platform:
        try:
            level = int(re.search(r'\d+', difficulty).group())
            return level + 1
        except:
            return 0
            
    if "백준" in platform:
        mapping = {
            'Bronze': 1, 'Silver': 2, 'Gold': 3, 
            'Platinum': 4, 'Diamond': 5, 'Ruby': 6
        }
        return mapping.get(difficulty, 0)
    return 0

def check_weekly_progress():
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    
    now_utc = datetime.utcnow()
    now_kst = now_utc + timedelta(hours=9)
    
    days_since_sat = (now_kst.weekday() - 5) % 7
    start_kst = (now_kst - timedelta(days=days_since_sat)).replace(hour=0, minute=0, second=0, microsecond=0)
    since_utc = start_kst - timedelta(hours=9)
    
    report = [f"🕒 집계 시각: {now_kst.strftime('%m/%d %H:%M')} (KST)"]
    report.append(f"📅 기준 시작: {start_kst.strftime('%m/%d %H:%M')} (KST) (토요일 00:00)\n\n")

    for name, repo_path in STUDY_MEMBERS.items():
        try:
            repo = g.get_repo(repo_path)
            commits = repo.get_commits(since=since_utc)
            
            total_score = 0
            solved_list = set()
            summary_dict = {} 

            for commit in commits:
                for file in commit.files:
                    if file.status == 'removed':
                        continue
                        
                    path = file.filename
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
                                category = f"{platform} {difficulty}"
                                summary_dict[category] = summary_dict.get(category, 0) + 1
            
            status = "✅ 달성" if total_score >= 20 else f"❌ 미달 ({20 - total_score}점 부족)"
            repo_url = f"https://github.com/{repo_path}"
            report.append(f"• *<{repo_url}|{name}>*: {total_score}점 ({status})")
            
            if summary_dict:
                # [정렬 로직 수정] 백준 순서 -> 프로그래머스 레벨 순서
                def sort_key(item):
                    cat = item[0]
                    # 1. 백준 정렬 (0~5번 인덱스 사용)
                    for i, tier in enumerate(BAEKJOON_TIERS):
                        if "백준" in cat and tier in cat:
                            return i
                    # 2. 프로그래머스 정렬 (100 + 레벨 숫자로 인덱스 부여)
                    if "프로그래머스" in cat:
                        try:
                            level = int(re.search(r'\d+', cat).group())
                            return 100 + level
                        except:
                            return 200
                    return 999 

                sorted_summary = sorted(summary_dict.items(), key=sort_key)
                summary_items = [f"{cat}: {count}개" for cat, count in sorted_summary]
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
        final_message = f"🏃🏃🏃🏃🏃*코딩 스터디 진행 현황*🏃🏃🏃🏃🏃\n\n{content}"
        requests.post(SLACK_WEBHOOK_URL, json={"text": final_message}, timeout=10)
    except Exception as e:
        print(f"오류: {e}")
