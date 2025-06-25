import re
import os
import time
from dotenv import load_dotenv
load_dotenv()

from playwright.sync_api import Playwright, sync_playwright, expect

class ReportSubmitter:
    def __init__(self, playwright: Playwright):
        self.browser = playwright.chromium.launch(headless=False)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.is_logged_in = False
    
    def login(self):
        """로그인 수행"""
        try:
            self.page.goto("https://udream.sejong.ac.kr/Career/tcp/Rpt.aspx")
            
            self.page.get_by_role("textbox", name="아이디").fill(os.getenv('UDREAM_ID'))
            self.page.get_by_role("textbox", name="비밀번호").fill(os.getenv('UDREAM_PW'))
            self.page.get_by_text("로그인").click()
            
            # 로그인 성공 확인
            self.page.wait_for_load_state("networkidle")
            self.is_logged_in = True
            print("로그인 성공")
            
        except Exception as e:
            print(f"로그인 실패: {e}")
            raise
    
    def close_datepicker_if_open(self):
        """날짜피커가 열려있으면 닫기"""
        try:
            # 날짜피커가 보이는지 확인
            datepicker = self.page.locator(".datepicker.dropdown-menu")
            if datepicker.is_visible(timeout=1000):
                # ESC 키로 닫기
                self.page.keyboard.press("Escape")
                # 또는 다른 곳 클릭해서 닫기
                self.page.locator("body").click()
                self.page.wait_for_timeout(500)
        except:
            pass
    
    def submit_report(self, date: str, report: str) -> bool:
        """단일 보고서 제출"""
        if not self.is_logged_in:
            raise Exception("로그인이 필요합니다")
        
        try:
            print(f"{date} 보고서 제출 시작")
            
            # 페이지가 유효한지 확인
            if self.page.is_closed():
                return False
            
            # 폼 필드 입력 전 대기
            self.page.wait_for_load_state("networkidle")
            
            # 날짜 입력
            print("날짜 입력 중...")
            date_input = self.page.locator("#Rdate")
            date_input.wait_for(state="visible", timeout=10000)
            date_input.clear()
            date_input.fill(date)
            
            # 날짜피커 닫기
            self.close_datepicker_if_open()
            
            # 보고서 내용 입력
            print("보고서 내용 입력 중...")
            report_input = self.page.locator("#Week_Rpt")
            report_input.wait_for(state="visible", timeout=10000)
            report_input.clear()
            report_input.fill(report)
            
            # 다시 한번 날짜피커 닫기 (보고서 입력 후에도 열릴 수 있음)
            self.close_datepicker_if_open()
            
            # 출석 체크 (개선된 방법)
            print("출석 체크 중...")
            try:
                # 방법 1: 직접 체크박스 클릭
                attendance_radio = self.page.locator("#Rcheck").locator("input[value='출석']")
                if attendance_radio.is_visible(timeout=2000):
                    attendance_radio.click()
                    print("출석 라디오 버튼 클릭 성공")
                else:
                    # 방법 2: 라벨 클릭
                    attendance_label = self.page.locator("#Rcheck").get_by_text("출석")
                    attendance_label.wait_for(state="visible", timeout=5000)
                    
                    # 날짜피커가 방해하지 않도록 한번 더 확인
                    self.close_datepicker_if_open()
                    
                    # 강제로 JavaScript 클릭
                    self.page.evaluate("""
                        const label = document.querySelector('#Rcheck .custom-control-label');
                        if (label) label.click();
                    """)
                    print("출석 라벨 JavaScript 클릭 성공")
                    
            except Exception as e:
                print(f"출석 체크 실패: {e}")
                # 그래도 계속 진행
            
            # 다이얼로그 처리
            self.page.once("dialog", lambda dialog: dialog.dismiss())
            
            # 등록 버튼 클릭
            print("등록 버튼 클릭...")
            submit_button = self.page.get_by_text("등록")
            submit_button.wait_for(state="visible", timeout=10000)
            submit_button.click()
            
            # 제출 후 결과 확인
            self.page.wait_for_timeout(1000)
            print(f"{date} 완료")
            return True
            
        except Exception as e:
            print(f"{date} 보고서 제출 실패: {e}")
            return False
    
    def submit_multiple_reports(self, report_data: list):
        """여러 보고서 일괄 제출"""
        if not self.is_logged_in:
            self.login()
        
        success_count = 0
        
        for i, data in enumerate(report_data, 1):
            print(f"\n{i}/{len(report_data)} - {data['date']} 처리 중...")
            
            # 페이지가 닫혔는지 확인
            if self.page.is_closed() or self.browser.is_connected() == False:
                print("ERROR: 브라우저 또는 페이지가 닫혔습니다")
                break
            
            # 첫 번째가 아니면 페이지 새로고침 (안전하게)
            if i > 1:
                try:
                    print("페이지 새로고침...")
                    self.page.reload()
                    self.page.wait_for_load_state("networkidle", timeout=15000)
                except Exception as e:
                    print(f"새로고침 실패: {e}")
                    # 새로고침 실패시 새 페이지로 이동
                    try:
                        self.page.goto("https://udream.sejong.ac.kr/Career/tcp/Rpt.aspx")
                        self.page.wait_for_load_state("networkidle")
                    except Exception as e2:
                        print(f"페이지 이동도 실패: {e2}")
                        break
            
            if self.submit_report(data["date"], data["report"]):
                success_count += 1
                print(f"{data['date']} 완료")
            else:
                print(f"{data['date']} 실패")
            
            # 서버 부하 방지를 위한 대기
            time.sleep(1)
        
        print(f"\n전체 완료: {success_count}/{len(report_data)} 성공")
        return success_count
    
    def close(self):
        """브라우저 종료"""
        try:
            if not self.page.is_closed():
                self.context.close()
            if self.browser.is_connected():
                self.browser.close()
        except:
            pass
