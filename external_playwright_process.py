import sys
import json
import ast
import os
import re
import traceback
import json_repair
from dotenv import load_dotenv
load_dotenv()

from playwright.sync_api import sync_playwright
from llm import OpenRouterClient
from report_submitter import ReportSubmitter


def main():
    try:
        # 인코딩 설정
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
        
        if len(sys.argv) != 2:
            error_result = {"success": False, "error": "잘못된 인수"}
            print("RESULT:" + json.dumps(error_result, ensure_ascii=False))
            sys.exit(1)
        
        print("로그인 시작", file=sys.stderr)
        
        # 데이터 로드
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        thesis = data["thesis"]
        weekdays = data["weekdays"]
        
        print(f"처리할 날짜 수: {len(weekdays)}", file=sys.stderr)
        
        # LLM으로 보고서 생성
        print("보고서 생성 중...", file=sys.stderr)
        client = OpenRouterClient()
        reports = client.generate_reports(thesis=thesis, days=weekdays)
        
        print("LLM 응답 파싱 중...", file=sys.stderr)
        # 파싱
        report_data = json_repair.loads(reports)
        
        print(f"생성된 보고서 수: {len(report_data) if isinstance(report_data, list) else 'Unknown'}", file=sys.stderr)
        
        # Playwright 실행
        print("웹 자동화 시작...", file=sys.stderr)
        with sync_playwright() as playwright:
            submitter = ReportSubmitter(playwright)
            submitter.login()
            
            success_count = submitter.submit_multiple_reports(report_data)
            total_count = len(weekdays)
            
            submitter.close()
        
        print(f"전체 완료: {success_count}/{total_count} 성공", file=sys.stderr)
        
        # 성공 결과 출력
        result = {
            "success": True,
            "count": success_count,
            "total": total_count
        }
        print("RESULT:" + json.dumps(result, ensure_ascii=False))
        
    except Exception as e:
        print(f"ERROR: 예외 발생 - {str(e)}", file=sys.stderr)
        print(f"ERROR: 상세 정보:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        
        result = {
            "success": False, 
            "error": str(e), 
            "traceback": traceback.format_exc()
        }
        print("RESULT:" + json.dumps(result, ensure_ascii=False))
        sys.exit(1)

if __name__ == "__main__":
    main()
