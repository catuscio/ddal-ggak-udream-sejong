from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date, timedelta

class DateField(BaseModel):
    start_date: date = Field(description='시작 날짜')
    end_date: date = Field(description='종료 날짜')
    weekdays: Optional[List[str]] = Field(default=None, description='주중')
    weekends: Optional[List[str]] = Field(default=None, description='주말')
    text: Optional[List[str]] = Field(default=None, description='보고서 쓸 내용')

    def get_weekdays_in_range(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[date]:
        """선택된 기간 내 주중 날짜 리스트 반환"""
        start = start_date or self.start_date
        end = end_date or self.end_date
        
        current_date = start
        weekdays = []
        while current_date <= end:
            if current_date.weekday() < 5:  # 월~금 (0~4)
                weekdays.append(current_date)
            current_date += timedelta(days=1)
        return weekdays
    
    def get_weekends_in_range(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[date]:
        """선택된 기간 내 주말 날짜 리스트 반환"""
        start = start_date or self.start_date
        end = end_date or self.end_date
        
        current_date = start
        weekends = []
        while current_date <= end:
            if current_date.weekday() in [5, 6]:  # 토, 일 (5, 6)
                weekends.append(current_date)
            current_date += timedelta(days=1)
        return weekends
    
    def string_list(self, date_list: List[date]) -> List[str]:
        return [d.strftime('%Y-%m-%d') for d in date_list]
    
    def update_weekdays_weekends(self):
        """기간 내 주중과 주말을 문자열 리스트로 업데이트"""
        self.weekdays = self.string_list(self.get_weekdays_in_range())
        self.weekends = self.string_list(self.get_weekends_in_range())

