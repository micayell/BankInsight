# BankInsight 기술 스택 및 구조 명세 (TECH.md)

이 문서는 BankInsight 프로젝트를 구성하는 프론트엔드 및 백엔드의 주요 기술 스택과 서버 아키텍처 환경을 정리한 명세서입니다.

## 1. 프론트엔드 인프라 및 기술 스택 (Front-end)

### 핵심 프레임워크 및 라이브러리
- **프레임워크**: `Vue.js (v3.5.14)` - 컴포지션 API 기반의 SPA(Single Page Application) 개발
- **번들러/빌드툴**: `Vite (v6.2.4)` - 빠르고 경량화된 최신 프론트엔드 개발 환경 및 빌드 속도 확보
- **상태 관리**: `Pinia (v3.0.1)` - 컴포넌트 간 데이터(예: 인증 정보, 추천 리스트, 환율, 맵 등) 상태 공유 및 관리
- **라우팅**: `Vue Router (v4.5.1)` - 클라이언트 사이드 페이지 전환 및 네비게이션
- **네트워크 통신**: `Axios (v1.9.0)` - 백엔드 REST API 서버와의 비동기 HTTP 통신

### UI 및 데이터 시각화
- **UI 컴포넌트 프레임워크**: `Bootstrap (v5.3.6)` & `Element-Plus (v2.9.10)` - 반응형 웹 디자인 및 사전 정의된 UI 컴포넌트 활용 
- **아이콘**: `Bootstrap Icons (v1.13.1)` - 애플리케이션 전반에서 사용되는 아이콘 팩
- **차트 및 데이터 시각화**: `Chart.js (v4.4.9)` & `Plotly.js` - 금리 비교, 환율 변동, 은(Silver) 시세 현황 등을 위한 인터랙티브 그래프 및 차트 구현
- **알림 및 날짜 처리**: `SweetAlert (v2.1.2)` (직관적인 알림 모달), `Day.js (v1.11.13)` (날짜 및 시간 포맷팅 변환)

---

## 2. 백엔드 인프라 및 기술 스택 (Back-end)

### 핵심 프레임워크 및 라이브러리
- **언어 및 프레임워크**: `Python 3 & Django (v4.2.16)` - MVT 기반의 견고한 웹 백엔드 서버 로직 구축
- **API 서버 구축**: `Django REST Framework (DRF, v3.15.2)` - 프론트엔드와 통신하기 위한 RESTful API 환경 구성
- **사용자 인증 및 보안**: 
  - `dj-rest-auth (v7.0.0)` 및 `django-allauth`: 회원가입, 로그인 및 인증 토큰 관리
  - `PyJWT`, `django-cors-headers` 등 보안 및 크로스 도메인 연동 처리

### 외부 API 연동 및 데이터 처리 
- **AI 챗봇 연동**: `OpenAI API Client (v1.82.0)` - GPT 기반 맞춤형 금융 상담 챗봇 구축 (프롬프트 전달 및 응답 처리)
- **외부 서버 모듈 통신**: `Requests`, `Httpx` 라이브러리를 통한 외부 금융 데이터/시세 API(한국 수출입은행 환율 정보, 금감원 금융상품통합비교공시 등 예상) 서버와의 HTTP 요청
- **데이터 파싱 및 직렬화**: `Pydantic` 및 `DRF Serializers`를 활용한 JSON 입출력 검증 및 스키마 적용
- **이미지 및 파일 핸들링**: `Pillow (v11.2.1)`를 활용한 프로필 이미지 등 멀티미디어 파일 처리
- **스크래핑/크롤링**: 은 시세(spot price) 등의 데이터를 정기적으로 가져오기 위한 스크래핑/Cron(커스텀 커맨드 `update_silver_prices.py`) 아키텍처 포함

### 데이터베이스 (Database)
- **RDBMS**: 기본적으로 `SQLite3 (db.sqlite3)`를 통하여 빠르고 간편한 로컬 RDBMS 운용 중 (필요시 향후 PostgreSQL/MySQL로 스케일업 용이하도록 Django ORM 계층 사용완료)
- `alldata.json` 형태의 초기 Fixture File(더미/기본 데이터) 지원

---

## 3. 주요 디렉토리(앱) 구조 명세

### 📁 프론트엔드 (`final-pjt-front/src`)
- `apis/`: 각 도메인별(인증, 게시글, 상품 등) axios axios 통신 로직 모듈화 폴더 
- `components/`: Chatbot, 환율계산기, 검색 등 공통적으로 재사용 가능한 Vue 컴포넌트 조각들
- `router/`: 프론트엔드 페이지 라우팅 설정 파일(`index.js`) 
- `stores/`: Pinia 기반 전역 상태 관리 모듈 (회원상태, 추천목록, 환율 상태 등)
- `views/`: 라우터가 매핑하는 실제 독립 페이지 컴포넌트(Article, Member, Search, Product 도메인별 분리)

### 📁 백엔드 (`final-pjt-back`)
- `accounts/`: 인증 토큰 등 사용자 계정 및 프로필 모델 관련 핵심 로직
- `articles/`: 자유 게시판 커뮤니티(게시물/댓글) CRUD 구현 애플리케이션
- `chatbot/`: OpenAI API 기반의 사용자 질의응답 및 프롬프트 관리 애플리케이션
- `exchange/`: 환율 정보 처리 및 계산 기능 애플리케이션
- `financial_products/`: 예/적금 상품 정보 저장, 사용자 간 상품 추천/비교 데이터 처리 애플리케이션
- `spot/`: 스크래퍼 기반 실물(금, 은 등) 시세 데이터 수집 및 가공 애플리케이션
