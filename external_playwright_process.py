import sys
import json
import ast
import os
import re
import traceback
from dotenv import load_dotenv
load_dotenv()

from playwright.sync_api import sync_playwright
from llm import OpenRouterClient
from report_submitter import ReportSubmitter

def safe_parse_llm_response(response_text):
    """LLM 응답을 안전하게 파싱하는 함수 (모든 형태 지원)"""
    try:
        cleaned = response_text.strip()
        
        # 다양한 백틱 패턴들을 순서대로 시도 (수정됨)
        patterns = [
            r'``````',      # ``````
            r'``````',          # ``````
            r'`(.*?)`',                    # ` ... `
        ]
        
        extracted = False
        for pattern in patterns:
            match = re.search(pattern, cleaned, re.DOTALL)
            if match:
                print(f"DEBUG: 패턴 매치: {pattern}")
                cleaned = match.group(1).strip()
                extracted = True
                break
        
        # 파싱 시도 순서
        parsing_methods = [
            ("json.loads", lambda x: json.loads(x)),
            ("ast.literal_eval", lambda x: ast.literal_eval(x)),
            ("json.loads (quote fix)", lambda x: json.loads(x.replace("'", '"'))),
        ]
        
        for method_name, method_func in parsing_methods:
            try:
                result = method_func(cleaned)
                print(f"DEBUG: {method_name} 성공")
                return result
            except Exception as e:
                print(f"DEBUG: {method_name} 실패: {e}")
        
        # 마지막 수단: 수동 리스트 추출
        start_idx = cleaned.find('[')
        end_idx = cleaned.rfind(']')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            list_part = cleaned[start_idx:end_idx + 1]
            print(f"DEBUG: 리스트 부분 추출: {list_part[:100]}...")
            
            for method_name, method_func in parsing_methods:
                try:
                    result = method_func(list_part)
                    print(f"DEBUG: 리스트 파싱 성공 ({method_name})")
                    return result
                except Exception as e:
                    print(f"DEBUG: 리스트 파싱 실패 ({method_name}): {e}")
                    continue
        
        raise ValueError(f"모든 파싱 방법 실패")
        
    except Exception as e:
        print(f"ERROR: 파싱 실패 - {str(e)}")
        print(f"ERROR: 원본 텍스트 (처음 500자): {response_text[:500]}...")
        raise


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
        report_data = safe_parse_llm_response(reports)
        
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
