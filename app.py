import streamlit as st
from datetime import date
import json
import tempfile
import subprocess
import os

from base_model import DateField

st.set_page_config(page_title="\"딸깍\"", page_icon="🖱️")

def run_external_playwright(date_field, thesis):
    """외부 프로세스로 Playwright 실행"""
    
    # 임시 파일에 데이터 저장
    data = {
        "thesis": thesis,
        "weekdays": date_field.weekdays
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
        temp_file = f.name
    
    try:
        # 가상환경의 Python 경로 사용
        python_path = r".venv\Scripts\python.exe"
                
        # 인코딩 문제 해결을 위해 errors='replace' 추가
        result = subprocess.run([
            python_path, "external_playwright_process.py", temp_file
        ], capture_output=True, text=True, timeout=300, 
           encoding='utf-8', errors='replace')
        
        if result.returncode == 0:
            try:
                # RESULT: 로 시작하는 줄 찾기
                lines = result.stdout.split('\n')
                result_line = None
                
                for line in lines:
                    if line.startswith('RESULT:'):
                        result_line = line[7:].strip()
                        break
                
                if result_line:
                    output_data = json.loads(result_line)
                    return output_data
                else:
                    return {"success": False, "error": f"RESULT 라인을 찾을 수 없음\n전체 출력:\n{result.stdout}"}
                    
            except json.JSONDecodeError as e:
                return {"success": False, "error": f"JSON 파싱 실패: {e}\n출력: {result.stdout}"}
        else:
            return {"success": False, "error": f"프로세스 실패 (코드: {result.returncode})\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"}
            
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "실행 시간 초과 (5분)"}
    except Exception as e:
        return {"success": False, "error": f"프로세스 실행 오류: {str(e)}"}
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_file):
            os.unlink(temp_file)


st.title("🖱️ 딸-깍")

# ============================== #
# 저장
# ============================== #

if "period_thesiss" not in st.session_state:
    st.session_state.period_thesiss = []

# ============================== #
# 기간 선택
# ============================== #

st.subheader("1. 기간 선택")
date_range = st.date_input(
    "기간을 선택하세요 (시작일 ~ 종료일)",
    value=(date.today(), date.today()),
    min_value=date(2020, 1, 1),
    max_value=date(2100, 12, 31)
)

# ============================== #
# 한 일 입력
# ============================== #

st.subheader("2. 해당 기간에 한 일")
thesis = st.text_area("무엇을 했나요?", height=150)

# ============================== #
# 저장 반영
# ============================== #

if st.button("저장 및 자동 제출"):
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        if start_date > end_date:
            st.error("시작일이 종료일보다 늦을 수 없습니다.")
        elif not thesis.strip():
            st.error("내용을 입력하세요.")
        else:
            # 세션에 저장
            st.session_state.period_thesiss.append({
                "start": start_date,
                "end": end_date,
                "thesis": thesis.strip()
            })
            st.success(f"{start_date} ~ {end_date} 기록이 저장되었습니다.")
            
            # 날짜 필드 생성
            date_field = DateField(
                start_date=start_date,
                end_date=end_date
            )
            date_field.update_weekdays_weekends()
            
            st.info(f"평일 {len(date_field.weekdays)}일에 대한 보고서를 생성합니다.")
            
            # 진행 상황 표시
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🚀 보고서 생성 및 제출 중...")
            progress_bar.progress(50)
            
            # 외부 프로세스 실행
            result = run_external_playwright(date_field, thesis.strip())
            
            progress_bar.progress(100)
            
            if result["success"]:
                status_text.text("✅ 완료!")
                success_count = result["count"]
                total_count = result["total"]
                
                if success_count == total_count:
                    st.success(f"🎉 모든 보고서 제출 완료! ({success_count}/{total_count})")
                else:
                    st.warning(f"⚠️ 일부 보고서 제출 실패 ({success_count}/{total_count})")
            
            else:
                status_text.text("❌ 실패")
                st.error(f"오류 발생: {result['error']}")
                
            progress_bar.empty()
            status_text.empty()
                
    else:
        st.error("기간을 올바르게 선택하세요.")
