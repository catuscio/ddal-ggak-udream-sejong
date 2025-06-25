import os
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
from string import Template

class OpenRouterClient:
    def __init__(self, api_key: Optional[str] = None):
        """OpenRouter 클라이언트 초기화"""
        load_dotenv()
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY가 필요합니다")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
        self.default_model = "google/gemma-3-27b-it:free"
        self.system_prompt_template = Template("""
너는 기업에서 현장실습을 진행한 세종대학교 학생의 일간 레포트 작성을 돕는 똑똑한 인공지능이다.
각 날짜에 따라 학생이 입력한 주제에 맞는, 학생이 했을 만한 일을 한 문장씩 적어라.
이 때, 주어진 주제를 분석하여 실제로 학생이 실천했을 법한 계획을 세워, 그 계획을 적어라.

### 주제 ###
{thesis}

### 날짜 ###
{days}

답변은 아래와 같은 형식으로 하라. 아래는 예시이니 실제 값으로 변경하라.
이 때, 문체는 '~도출 하였다.`가 아닌 `~도출`로 통일하라.
[
  {
    'date': `2025-06-24',
    'thesis': 'LLM 파인튜닝' # 주제에 주어진 값 그대로 입력
    'report': 'Roboflow를 사용하여 파인튜닝 데이터 Annotation 진행'
  },
  {
    'date': `2025-06-25',
    'thesis': 'LLM 파인튜닝' # 주제에 주어진 값 그대로 입력
    'report': '생성한 데이터셋 전처리'
  }
]
""")
    
    def chat_completion(
        self, 
        messages: List[Dict[str, Any]], 
        model: Optional[str] = None,
        extra_body: Optional[Dict] = None
    ) -> str:
        try:
            completion = self.client.chat.completions.create(
                extra_body=extra_body or {},
                model=model or self.default_model,
                messages=messages
            )
            return completion.choices[0].message.content
        except Exception as e:
            raise Exception(f"API 요청 실패: {e}")
    
    def invoke(self, content: str, model: Optional[str] = None) -> str:
        """간단한 텍스트 채팅"""
        messages = [
            {
                "role": "system",
                "content": [{"type": "text", "text": self.system_prompt}]
            },
            {
                "role": "user",
                "content": [{"type": "text", "text": content}]
            }
        ]
        return self.chat_completion(messages, model)
    
    def generate_reports(self, thesis: str, days: List[str], model: Optional[str] = None) -> str:
        """실습 보고서 생성 전용 메서드"""
        # 프롬프트에 실제 값 삽입
        formatted_prompt = self.system_prompt_template.substitute(
            thesis=thesis,
            days=", ".join(days)
        )
        
        messages = [
            {
                "role": "system",
                "content": [{"type": "text", "text": formatted_prompt}]
            },
            {
                "role": "user",
                "content": [{"type": "text", "text": f"주제: {thesis}\n날짜: {', '.join(days)}"}]
            }
        ]
        return self.chat_completion(messages, model)