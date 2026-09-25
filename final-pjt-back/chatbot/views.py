from django.conf import settings
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import requests
import logging
import json
from django.db.models import Q
from financial_products.models import DepositProduct, SavingProduct

logger = logging.getLogger(__name__) 

FINANCE_KEYWORDS = ["예금", "적금", "상품", "추천", "금리", "투자", "만기", "은행", "계좌"]
DEPOSIT_KEYWORDS = ["예금", "거치식"]
SAVING_KEYWORDS = ["적금", "정기적금", "자유적금"]
BANK_NAMES = ["국민", "신한", "우리", "하나", "농협", "기업", "토스", "카카오", "케이뱅크", "SC제일", "씨티", "부산", "경남", "광주", "전북", "대구", "제주", "수협", "산업"]

@api_view(['POST'])
@authentication_classes([]) 
@permission_classes([AllowAny])
def chatbot_response(request):
    logger.info("챗봇 응답 요청 시작")
    
    # API 키 확인
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        logger.error("GEMINI_API_KEY가 설정되지 않았습니다.")
        return Response({"error": "서버 환경 변수(.env)에 GEMINI_API_KEY가 설정되지 않았습니다."}, status=500)

    user_message = request.data.get('message', "")
    previous_messages = request.data.get('messages', [])
    
    is_finance_query = any(keyword in user_message for keyword in FINANCE_KEYWORDS)
    db_product_info_str = ""
    recommended_products = []

    if is_finance_query and user_message:
        deposit_data_list = []
        saving_data_list = []
        
        user_message_lower = user_message.lower()
        
        # 사용자가 특정 은행을 언급했는지 확인
        mentioned_banks = [bank for bank in BANK_NAMES if bank in user_message]
        
        # 특정 상품군(예금/적금)을 언급했는지 확인
        wants_deposit = any(kw in user_message_lower for kw in DEPOSIT_KEYWORDS)
        wants_saving = any(kw in user_message_lower for kw in SAVING_KEYWORDS)
        
        # 만약 '상품', '추천', '국민은행' 등 포괄적인 질문만 하고 콕 집어 예/적금을 말 안했다면 둘 다 검색
        if not wants_deposit and not wants_saving:
            wants_deposit = True
            wants_saving = True

        deposit_qs = DepositProduct.objects.all()
        saving_qs = SavingProduct.objects.all()

        # 은행명 필터링 적용
        if mentioned_banks:
            q_dep = Q()
            q_sav = Q()
            for b in mentioned_banks:
                q_dep |= Q(kor_co_nm__icontains=b)
                q_sav |= Q(kor_co_nm__icontains=b)
            deposit_qs = deposit_qs.filter(q_dep)
            saving_qs = saving_qs.filter(q_sav)

        if wants_deposit:
            deposits = deposit_qs[:3]
            for product in deposits:
                options_info = []
                for opt in product.options.all().order_by('-intr_rate2', '-intr_rate')[:2]: 
                    options_info.append(
                        f"- {opt.save_trm}개월 ({opt.intr_rate_type_nm}): 기본 {opt.intr_rate}%, 최고 우대 {opt.intr_rate2}%"
                    )
                if options_info:
                    deposit_data_list.append({
                        "type": "deposit",
                        "code": product.fin_prdt_cd,
                        "은행명": product.kor_co_nm,
                        "상품명": product.fin_prdt_nm,
                        "특징 요약": product.mtrt_int if product.mtrt_int else "별도 안내 없음",
                        "가입방법": product.join_way if product.join_way else "은행 문의",
                        "주요 금리 조건": options_info,
                    })
            
            if deposit_data_list:
                db_product_info_str += "\n\n## 추천 예금 상품 정보 (DB 기반)\n"
                for info in deposit_data_list:
                    recommended_products.append({"type": info["type"], "code": info["code"], "name": info["상품명"]})
                    db_product_info_str += f"### {info['상품명']} ({info['은행명']})\n"
                    db_product_info_str += f"- 특징: {info['특징 요약']}\n"
                    db_product_info_str += f"- 가입방법: {info['가입방법']}\n"
                    db_product_info_str += "- 주요 금리 조건:\n"
                    for opt_str in info['주요 금리 조건']:
                        db_product_info_str += f"  {opt_str}\n"

        if wants_saving:
            savings = saving_qs[:3]
            for product in savings:
                options_info = []
                for opt in product.options.all().order_by('-intr_rate2', '-intr_rate')[:2]:
                    options_info.append(
                        f"- {opt.save_trm}개월 ({opt.rsrv_type_nm}, {opt.intr_rate_type_nm}): 기본 {opt.intr_rate}%, 최고 우대 {opt.intr_rate2}%"
                    )
                if options_info:
                    saving_data_list.append({
                        "type": "saving",
                        "code": product.fin_prdt_cd,
                        "은행명": product.kor_co_nm,
                        "상품명": product.fin_prdt_nm,
                        "특징 요약": product.mtrt_int if product.mtrt_int else "별도 안내 없음",
                        "가입방법": product.join_way if product.join_way else "은행 문의",
                        "주요 금리 조건": options_info,
                    })
            
            if saving_data_list:
                db_product_info_str += "\n\n## 추천 적금 상품 정보 (DB 기반)\n"
                for info in saving_data_list:
                    recommended_products.append({"type": info["type"], "code": info["code"], "name": info["상품명"]})
                    db_product_info_str += f"### {info['상품명']} ({info['은행명']})\n"
                    db_product_info_str += f"- 특징: {info['특징 요약']}\n"
                    db_product_info_str += f"- 가입방법: {info['가입방법']}\n"
                    db_product_info_str += "- 주요 금리 조건:\n"
                    for opt_str in info['주요 금리 조건']:
                        db_product_info_str += f"  {opt_str}\n"

        if not deposit_data_list and not saving_data_list:
            db_product_info_str = "\n[안내] 현재 DB에서 바로 추천해드릴 만한 실시간 상품 정보를 찾지 못했습니다. 일반적인 금융 지식을 바탕으로 안내해주세요."

    system_prompt_content = (
        "당신은 금융 상품 추천 및 정보 제공을 전문으로 하는 AI 어시스턴트입니다. "
        "모든 답변은 반드시 한국어로 제공해야 합니다. "
        "사용자의 질문에 금융 관련 키워드가 포함되어 있고, 아래 '[DB 예금/적금 상품 정보 (DB 기반)]' 섹션에 관련 정보가 있다면 "
        "해당 DB 정보를 최우선으로 사용하여 사용자에게 상품의 이름, 은행명, 주요 특징, 금리 정보를 명확히 언급하며 설명해주세요. "
        "단순히 정보를 나열하기보다는, 각 상품의 장점을 자연스럽게 풀어서 설명하고, 어떤 상황에 유용한지 조언해주세요. "
        "만약 DB 정보가 비어있거나, 질문이 일반적인 금융 지식 및 재테크 방법에 관한 것이라면 금융 전문가로서 이해하기 쉽고 친절하게 조언해주세요."
    )
    
    enriched_user_message = user_message
    if db_product_info_str:
        enriched_user_message += db_product_info_str

    formatted_contents = []
    for msg in previous_messages:
        role = "model" if msg.get("role") == "assistant" else "user"
        content_text = msg.get("content", "")
        if content_text.strip():
            formatted_contents.append({
                "role": role,
                "parts": [{"text": content_text}]
            })
            
    formatted_contents.append({
        "role": "user",
        "parts": [{"text": enriched_user_message}]
    })

    payload = {
        "system_instruction": {
            "parts": {"text": system_prompt_content}
        },
        "contents": formatted_contents,
        "generationConfig": {
            "temperature": 0.6
        }
    }
    
    # 전달주신 공식 문서를 참고하여 최신 모델로 재배치했습니다. 
    # v1beta 환경에서 지원 중인 3.5 계열 및 2.5 계열 모델을 순차적으로 탐색합니다.
    models_to_try = [
        "gemini-3.5-flash",
        "gemini-3.1-flash-lite",
        "gemini-2.5-flash", 
        "gemini-2.5-flash-lite"
    ]
    
    last_error_response = None
    
    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        
        try:
            logger.info(f"Gemini 서버에 직접 요청 시도 중... 모델: {model_name}")
            response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                try:
                    chat_response_content = data['candidates'][0]['content']['parts'][0]['text'].strip()
                    logger.info(f"{model_name} 모델에서 응답을 성공적으로 수신했습니다.")
                    return Response({"response": chat_response_content, "recommended_products": recommended_products})
                except (KeyError, IndexError):
                    logger.error(f"Gemini 데이터 구조 읽기 오류. 원본 데이터: {data}")
                    return Response({"error": "AI 응답 형식을 읽을 수 없습니다."}, status=500)
                    
            elif response.status_code == 404:
                # 404를 받으면 리스트의 다음 모델 이름으로 다시 시도
                logger.warning(f"모델 {model_name}은 현재 앱에서 지원하지 않음(404). 다음 모델로 시도합니다.")
                last_error_response = response
                continue
                
            else:
                logger.error(f"Gemini API 에러: {response.status_code} - {response.text}")
                error_msg = f"API 통신 오류가 발생했습니다. (상태코드: {response.status_code})"
                if response.status_code == 429:
                    error_msg = "API 사용량 제한을 초과했습니다. 잠시 후 다시 시도해주세요."
                elif response.status_code == 400:
                     error_msg = "Gemini 서버에서 처리할 수 없는 요청입니다. (400 Bad Request)"
                elif response.status_code == 503:
                     # 503(Service Unavailable) 에러 대응
                     error_msg = "현재 구글 AI 서버(Gemini)에 전 세계적으로 요청이 폭주하여 일시적으로 지연되고 있습니다. 1~2분 뒤 다시 시도해주세요."
                     return Response({"error": error_msg, "details": ""}, status=response.status_code)
                
                return Response({"error": error_msg, "details": response.text}, status=response.status_code)
                
        except requests.exceptions.Timeout:
            logger.error("Gemini API 요청 시간 초과", exc_info=True)
            return Response({"error": "AI API 요청 처리 시간이 초과되었습니다. (Timeout)"}, status=504)
        except Exception as e:
            logger.error(f"챗봇 응답 처리 중 알 수 없는 오류 발생: {str(e)}", exc_info=True)
            return Response({"error": "챗봇 응답 처리 중 서버 내부 오류가 발생했습니다.", "details": str(e)}, status=500)

    # 404가 계속 뜬 경우 최종적으로 오류 반환
    if last_error_response:
        return Response({
            "error": "발급하신 API 키 계정에서 최신 모델에 대한 정보를 찾을 수 없습니다.", 
            "details": last_error_response.text
        }, status=404)
    
    return Response({"error": "모든 모델 요청이 실패했습니다."}, status=500)