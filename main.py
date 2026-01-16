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
    "안유민": "DEVELOPERYUMIN/CodingTest",
    "이수현": "shjade/codingtest",
    "조혜정": "HYEJEONG-JO/CO_test"
}

ALLOWED_EXTENSIONS = ('.py', '.sql', '.java', '.cpp', '.js', '.c', '.cs', '.ts')
BAEKJOON_TIERS = ['Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Ruby']

def get_score(platform, difficulty):
    platform, difficulty = platform.strip(), difficulty.strip()
    if "프로그래머스" in platform:
        try:
            level = int(re.search(r'\d+', difficulty).group())
            return level + 1
        except: return 0
    if "백준" in platform:
        mapping = {'Bronze': 1, 'Silver': 2, 'Gold': 3, 'Platinum': 4, 'Diamond': 5, 'Ruby': 6}
        return mapping.get(difficulty, 0)
    return 0

def check_weekly_progress():
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    
    now_utc = datetime.utcnow()
    now_kst = now_utc + timedelta(hours=9)
    
    days_since_friday = (now_kst.weekday() - 4) % 7
    start_kst = (now_kst - timedelta(days=days_since_friday)).replace(hour=20, minute=0, second=0, microsecond=0)
    if now_kst < start_kst:
        start_kst -= timedelta(days=7)
    
    since_utc = start_kst - timedelta(hours=9)
    
    report = [f"🕒 *집계 시각:* {now_kst.strftime('%m/%d %H:%M')} (KST)"]
    report.append(f"📅 *기준 시작:* {start_kst.strftime('%m/%d %H:%M')} (KST) (금요일 20:00)\n")

    for name, repo_path in STUDY_MEMBERS.items():
        try:
            # 레포지토리 정보 가져오기 시도
            repo = g.get_repo(repo_path)
            commits = repo.get_commits(since=since_utc)
            
            total_score, solved_list, summary_dict = 0, set(), {}

            for commit in commits:
                for file in commit.files:
                    if file.status == 'removed': continue
                    path = file.filename
                    if not path.lower().endswith(ALLOWED_EXTENSIONS): continue

                    parts = path.split('/')
                    target_idx = -1
                    for i, p in enumerate(parts):
                        if "백준" in p or "프로그래머스" in p:
                            target_idx = i
                            break
                    
                    if target_idx != -1 and len(parts) > target_idx + 2:
                        platform, diff, pid = parts[target_idx], parts[target_idx+1], parts[target_idx+2]
                        if not re.match(r'^\d+', pid): continue

                        if pid not in solved_list:
                            score = get_score(platform, diff)
                            if score > 0:
                                total_score += score
                                solved_list.add(pid)
                                cat = f"{platform} {diff}"
                                summary_dict[cat] = summary_dict.get(cat, 0) + 1
            
            status_icon = "✅" if total_score >= 20 else "❌"
            status_text = f"{status_icon} 달성" if total_score >= 20 else f"{status_icon} 미달 ({20 - total_score}점 부족)"
            
            # 하이퍼링크 없이 이름만 출력
            report.append(f"• {name}: {total_score}점 ({status_text})")
            
            if summary_dict:
                def sort_key(item):
                    cat = item[0]
                    for i, tier in enumerate(BAEKJOON_TIERS):
                        if "백준" in cat and tier in cat: return i
                    if "프로그래머스" in cat:
                        try: return 100 + int(re.search(r'\d+', cat).group())
                        except: return 200
                    return 999 

                sorted_summary = sorted(summary_dict.items(), key=sort_key)
                summary_str = ", ".join([f"{cat}: {count}개" for cat, count in sorted_summary])
                report.append(f"    └ _{summary_str}_")
            else:
                report.append("    └ _이번 주 풀이 내역 없음_")
            report.append("") 
            
        except Exception as e:
            # 구체적인 실패 이유 출력 (오타 또는 Private 여부)
            reason = "⚠️ 조회 실패"
            if "404" in str(e):
                reason += " (레포명 확인 필요)"
            elif "401" in str(e) or "403" in str(e):
                reason += " (권한/토큰 문제)"
            report.append(f"• *{name}*: {reason}\n")
    
    return "\n".join(report)

if __name__ == "__main__":
    try:
        content = check_weekly_progress()
        title = "🏃🏃 *코딩 스터디 진행 현황* 🏃🏃\n"
        final_message = f"{title}\n{content}"
        
        # 슬랙 워크플로에 데이터 전송
        requests.post(SLACK_WEBHOOK_URL, json={"text": final_message}, timeout=15)
    except Exception as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
