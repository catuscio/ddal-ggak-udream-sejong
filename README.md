<h1 align='center'>
   🖱️딸-깍
</h1>

> **이 프로그램은 세종대학교 유드림 현장실습 보고서를 무료로 써줍니다.**

## 설명
이 프로그램은 세종대학교 유드림 현장실습 보고서를 작성, 제출까지 완전 자동화 합니다.\
하나하나 다 쓰는 것보다 훨씬 빠르고 간편합니다.\
LLM은 OpenRouter의 무료 모델을 사용합니다.\
주말을 자동으로 필터링 하여 주중에만 작성할 수 있도록 해놨습니다.\
자세한 Documentation 및 구조도는 Deep.wiki로 생성한 아래 docs에서 확인하실 수 있습니다.\
https://deepwiki.com/catuscio/ddal-ggak-udream-sejong

## 실행 방법
1. 다운로드 합니다.
2. `.env`파일에 본인 계정 ID, PW, 그리고 Open Router API 키를 입력합니다.
   ```
   UDREAM_ID="학번"
   UDREAM_PW="학사정보시스템 비밀번호"
   OPENROUTER_API_KEY="OpenRouter API 키"
   ```
4. `run.ba`t 혹은 `run.sh` 파일을 실행합니다.
5. 보고서를 쓸 날짜를 선택하고, 쓸 주제를 입력하고, 제출 버튼을 누릅니다.
6. PROFIT!!!!!!!!!!

## 주의사항
- '딸-깍'은 주말은 기록에서 제외하지만 공휴일은 제외하지 않습니다. 추후 수동을 제거해야 합니다.
- '딸-깍'은 모든 일과를 '출석'으로 기록합니다. 지각 혹은 휴가는 알아서 수동으로 제거하십시오.
- '딸-깍'은 OpenRouter의 Gemma3 27B Free 모델을 사용합니다. 모델에게 입력된 내용은 Model Provider에게 전달 혹은 저장될 수 있습니다.
- '딸-깍'의 제작자는 '딸-깍'을 사용하여 발생하는 불이익에 대해 책임지지 않습니다.

## ETC
- Open Router 링크
https://openrouter.ai
