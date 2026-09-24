from django.conf import settings
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import requests
import logging
import json
from financial_products.models import DepositProduct, SavingProduct

logger = logging.getLogger(__name__) 

FINANCE_KEYWORDS = ["예금", "적금", "상품", "추천", "금리", "이자율", "만기", "은행", "계좌"]
DEPOSIT_KEYWORDS = ["예금", "거치식"]
SAVING_KEYWORDS = ["적금", "정기적금", "자유적금"]

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

    if is_finance_query and user_message:
        deposit_data_list = []
        saving_data_list = []

        if any(keyword in user_message.lower() for keyword in DEPOSIT_KEYWORDS) or "예금" in user_message:
            deposits = DepositProduct.objects.all()[:3]
            for product in deposits:
                options_info = []
                for opt in product.options.all().order_by('-intr_rate2', '-intr_rate')[:2]: 
                    options_info.append(
                        f"- {opt.save_trm}개월 ({opt.intr_rate_type_nm}): 기본 {opt.intr_rate}%, 우대 적용시 {opt.intr_rate2}%"
                    )
                if options_info:
                    deposit_data_list.append({
                        "은행": product.kor_co_nm,
                        "상품명": product.fin_prdt_nm,
                        "특징 요약": product.mtrt_int if product.mtrt_int else "별도 안내 없음",
                        "가입 방법": product.join_way if product.join_way else "은행 문의",
                        "주요 금리 조건": options_info,
                    })
            
            if deposit_data_list:
                db_product_info_str += "\n\n## 추천 예금 상품 정보 (DB 기반)\n"
                for info in deposit_data_list:
                    db_product_info_str += f"### {info['상품명']} ({info['은행']})\n"
                    db_product_info_str += f"- 특징: {info['특징 요약']}\n"
                    db_product_info_str += f"- 가입방법: {info['가입 방법']}\n"
                    db_product_info_str += "- 주요 금리 조건:\n"
                    for opt_str in info['주요 금리 조건']:
                        db_product_info_str += f"  {opt_str}\n"

        if any(keyword in user_message.lower() for keyword in SAVING_KEYWORDS) or "적금" in user_message:
            savings = SavingProduct.objects.all()[:3]
            for product in savings:
                options_info = []
                for opt in product.options.all().order_by('-intr_rate2', '-intr_rate')[:2]:
                    options_info.append(
                        f"- {opt.save_trm}개월 ({opt.rsrv_type_nm}, {opt.intr_rate_type_nm}): 기본 {opt.intr_rate}%, 우대 적용시 {opt.intr_rate2}%"
                    )
                if options_info:
                    saving_data_list.append({
                        "은행": product.kor_co_nm,
                        "상품명": product.fin_prdt_nm,
                        "특징 요약": product.mtrt_int if product.mtrt_int else "별도 안내 없음",
                        "가입 방법": product.join_way if product.join_way else "은행 문의",
                        "주요 금리 조건": options_info,
                    })
            
            if saving_data_list:
                db_product_info_str += "\n\n## 추천 적금 상품 정보 (DB 기반)\n"
                for info in saving_data_list:
                    db_product_info_str += f"### {info['상품명']} ({info['은행']})\n"
                    db_product_info_str += f"- 특징: {info['특징 요약']}\n"
                    db_product_info_str += f"- 가입방법: {info['가입 방법']}\n"
                    db_product_info_str += "- 주요 금리 조건:\n"
                    for opt_str in info['주요 금리 조건']:
                        db_product_info_str += f"  {opt_str}\n"

        if not deposit_data_list and not saving_data_list:
            db_product_info_str = "\n[안내] 현재 DB에서 바로 추천해 드릴 만한 상품 정보를 찾지 못했습니다. 대신 일반적인 금융 정보를 바탕으로 답변드릴게요."

    system_prompt_content = (
        "당신은 금융 상품 추천 및 정보 제공을 전문으로 하는 AI 어시스턴트입니다. "
        "모든 답변은 반드시 한국어로 제공해야 합니다. "
        "사용자의 질문에 금융 관련 키워드가 포함되어 있고, 아래 '[DB 예금/적금 상품 정보 (DB 기반)]' 섹션에 관련 정보가 있다면, "
        "해당 DB 정보를 최우선으로 활용하여 사용자에게 상품의 이름, 은행명, 주요 특징, 금리 정보를 명확히 언급하며 설명해주세요. "
        "단순히 정보를 나열하기보다는, 각 상품의 장점을 자연스럽게 풀어서 설명하고, 어떤 상황에 유용할지 조언해주세요. "
        "만약 DB 정보가 없거나, 질문이 일반적인 금융 상식 및 재테크 방법에 대한 것이라면 금융 전문가로서 이해하기 쉽고 친절하게 답변해주세요."
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
    
    # 전달주신 공식 문서를 참고하여 최신 모델들로 재배치했습니다. 
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
            logger.info(f"Gemini 서버로 직접 요청 시도 중... 모델: {model_name}")
            response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                try:
                    chat_response_content = data['candidates'][0]['content']['parts'][0]['text'].strip()
                    logger.info(f"{model_name} 모델에서 답변을 성공적으로 수신했습니다.")
                    return Response({"response": chat_response_content})
                except (KeyError, IndexError):
                    logger.error(f"Gemini 데이터 구조 읽기 오류. 원본 데이터: {data}")
                    return Response({"error": "AI 응답 형식을 읽을 수 없습니다."}, status=500)
                    
            elif response.status_code == 404:
                # 404를 받으면 리스트의 다음 모델 이름으로 다시 시도
                logger.warning(f"모델 {model_name}은 현재 키에서 지원하지 않음(404). 다음 모델을 시도합니다.")
                last_error_response = response
                continue
                
            else:
                logger.error(f"Gemini API 에러: {response.status_code} - {response.text}")
                error_msg = f"API 통신 오류가 발생했습니다. (상태코드: {response.status_code})"
                if response.status_code == 429:
                    error_msg = "API 사용량 제한을 초과했습니다. 잠시 후 다시 시도해주세요."
                if response.status_code == 400:
                     error_msg = "Gemini 서버에서 처리할 수 없는 요청입니다. (400 Bad Request)"
                return Response({"error": error_msg, "details": response.text}, status=response.status_code)
                
        except requests.exceptions.Timeout:
            logger.error("Gemini API 요청 시간 초과", exc_info=True)
            return Response({"error": "AI API 요청 처리 시간이 초과되었습니다. (Timeout)"}, status=504)
        except Exception as e:
            logger.error(f"챗봇 응답 처리 중 내부 오류 발생: {str(e)}", exc_info=True)
            return Response({"error": "챗봇 응답 처리 중 서버 내부 오류가 발생했습니다.", "details": str(e)}, status=500)

    # 404가 계속 뜬 경우 최종적으로 오류 반환
    if last_error_response:
        return Response({
            "error": "발급하신 API 키 계정에서 최신 모델에 대한 정보를 찾을 수 없습니다.", 
            "details": last_error_response. текста
        }, status=404)
    
    return Response({"error": "모든 모델 요청에 실패했습니다."}, status=500)