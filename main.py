# main.py의 마지막 부분을 아래와 같이 수정
if __name__ == "__main__":
    report_content = check_weekly_progress()
    now = datetime.now()
    
    # 시간대에 따른 제목 변경
    if now.weekday() == 4 and now.hour >= 16: # 금요일 오후 4시 이후 실행 시
        title = "🏁 *[최종] 이번 주 코딩 스터디 마감 결과*"
    else:
        title = f"☀️ *[일일 체크] 현재 스터디 진행 현황 ({now.strftime('%m/%d')})*"
        
    final_message = f"{title}\n\n{report_content}"
    send_to_slack(final_message)
