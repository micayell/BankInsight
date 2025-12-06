from django.shortcuts import render
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from openai import OpenAI, APIError, APITimeoutError, RateLimitError, AuthenticationError, BadRequestError
import json
import logging
from financial_products.models import DepositProduct, DepositOption, SavingProduct, SavingOption

logger = logging.getLogger(__name__) 

FINANCE_KEYWORDS = ["예금", "적금", "상품", "추천", "금리", "이자율", "만기", "은행", "계좌"]
DEPOSIT_KEYWORDS = ["예금", "거치식"]
SAVING_KEYWORDS = ["적금", "정기적금", "자유적금"]

@api_view(['POST'])
@authentication_classes([]) 
@permission_classes([AllowAny])
def chatbot_response(request):
    logger.info("챗봇 응답 요청 시작")
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        logger.info("OpenAI 클라이언트 초기화 성공")
    except Exception as e:
        logger.error(f"OpenAI 클라이언트 초기화 실패: {str(e)}", exc_info=True)
        return Response({"error": "OpenAI 클라이언트 설정에 문제가 발생했습니다.", "details": str(e)}, status=500)

    user_message = request.data.get('message', "")
    previous_messages = request.data.get('messages', [])

    logger.debug(f"수신된 사용자 메시지: {user_message}")
    logger.debug(f"수신된 이전 대화: {previous_messages}")
    
    is_finance_query = any(keyword in user_message for keyword in FINANCE_KEYWORDS)
    db_product_info_str = ""

    if is_finance_query and user_message:
        logger.info("금융 관련 질문으로 판단됨. DB 조회 시작.")
        
        deposit_data_list = []
        saving_data_list = []

        if any(keyword in user_message.lower() for keyword in DEPOSIT_KEYWORDS) or "예금" in user_message:
            deposits = DepositProduct.objects.all()[:3]
            logger.debug(f"DB에서 예금 상품 {deposits.count()}개 조회됨 (최대 3개)")
            
            for product in deposits:
                options_info = []
                for opt in product.options.all().order_by('-intr_rate2', '-intr_rate')[:2]: 
                    options_info.append(
                        f"- {opt.save_trm}개월 ({opt.intr_rate_type_nm}): 기본 {opt.intr_rate}%, 우대 적용시 {opt.intr_rate2}%"
                    )
                if options_info:
                    product_info = {
                        "은행": product.kor_co_nm,
                        "상품명": product.fin_prdt_nm,
                        "특징 요약": product.mtrt_int if product.mtrt_int else "별도 안내 없음",
                        "가입 방법": product.join_way if product.join_way else "은행 문의",
                        "주요 금리 조건 (최대 2개, 높은 순)": options_info,
                    }
                    deposit_data_list.append(product_info)
            
            if deposit_data_list:
                db_product_info_str += "\n\n## 추천 예금 상품 정보 (DB 기반)\n"
                for info in deposit_data_list:
                    db_product_info_str += f"### {info['상품명']} ({info['은행']})\n"
                    db_product_info_str += f"- 특징: {info['특징 요약']}\n"
                    db_product_info_str += f"- 가입방법: {info['가입 방법']}\n"
                    db_product_info_str += "- 주요 금리 조건:\n"
                    for opt_str in info['주요 금리 조건 (최대 2개, 높은 순)']:
                        db_product_info_str += f"  {opt_str}\n"
                db_product_info_str += "\n"
            logger.debug(f"가공된 예금 정보 문자열 (일부): {db_product_info_str[:200] if db_product_info_str else '없음'}")

        if any(keyword in user_message.lower() for keyword in SAVING_KEYWORDS) or "적금" in user_message:
            savings = SavingProduct.objects.all()[:3]
            logger.debug(f"DB에서 적금 상품 {savings.count()}개 조회됨 (최대 3개)")
            
            for product in savings:
                options_info = []
                for opt in product.options.all().order_by('-intr_rate2', '-intr_rate')[:2]:
                    options_info.append(
                        f"- {opt.save_trm}개월 ({opt.rsrv_type_nm}, {opt.intr_rate_type_nm}): 기본 {opt.intr_rate}%, 우대 적용시 {opt.intr_rate2}%"
                    )
                if options_info:
                    product_info = {
                        "은행": product.kor_co_nm,
                        "상품명": product.fin_prdt_nm,
                        "특징 요약": product.mtrt_int if product.mtrt_int else "별도 안내 없음",
                        "가입 방법": product.join_way if product.join_way else "은행 문의",
                        "주요 금리 조건 (최대 2개, 높은 순)": options_info,
                    }
                    saving_data_list.append(product_info)
            
            if saving_data_list:
                db_product_info_str += "\n\n## 추천 적금 상품 정보 (DB 기반)\n"
                for info in saving_data_list:
                    db_product_info_str += f"### {info['상품명']} ({info['은행']})\n"
                    db_product_info_str += f"- 특징: {info['특징 요약']}\n"
                    db_product_info_str += f"- 가입방법: {info['가입 방법']}\n"
                    db_product_info_str += "- 주요 금리 조건:\n"
                    for opt_str in info['주요 금리 조건 (최대 2개, 높은 순)']:
                        db_product_info_str += f"  {opt_str}\n"
                db_product_info_str += "\n"
            logger.debug(f"가공된 적금 정보 문자열 (일부): {db_product_info_str[:200] if db_product_info_str else '없음'}")


        if not deposit_data_list and not saving_data_list:
            db_product_info_str = "\n[안내] 현재 DB에서 바로 추천해 드릴 만한 상품 정보를 찾지 못했습니다. 대신 일반적인 금융 정보를 바탕으로 답변드릴게요."
            logger.info("DB에서 해당 금융 상품 정보를 찾지 못함.")
    else:
        logger.info("일반 대화로 판단됨. DB 조회 없음.")
        #프롬프트 내역
    system_prompt_content = (
        "당신은 금융 상품 추천 및 정보 제공을 전문으로 하는 AI 어시스턴트입니다. "
        "모든 답변은 반드시 한국어로 제공해야 합니다. "
        "사용자의 질문에 금융 관련 키워드가 포함되어 있고, 아래 '[DB 예금/적금 상품 정보 (DB 기반)]' 섹션에 관련 정보가 있다면, "
        "해당 DB 정보를 **최우선으로 활용하여, 마치 당신이 직접 찾아서 설명하는 것처럼** 사용자에게 상품의 이름, 은행명, 주요 특징, 금리 정보를 명확히 언급하며 추천하거나 설명해주세요. "
        "단순히 정보를 나열하기보다는, **각 상품의 장점을 자연스럽게 풀어서 설명하고, 어떤 상황의 사용자에게 유용할지** 조언하는 말투로 답변해주세요. "
        "제공된 DB 정보는 일부이며 제한적일 수 있습니다. 만약 정보가 부족하여 완벽한 추천이 어렵다면, 사용자에게 추가적인 정보를 요청하거나, '현재 확인된 정보는 다음과 같으며, 더 자세한 내용은 해당 은행에 직접 문의하시거나 공식 웹사이트를 참고하시는 것이 좋습니다.' 와 같이 안내해주세요. "
        "만약 DB 정보가 없거나, 사용자의 질문이 일반적인 금융 상식, 투자, 재테크 방법 등에 대한 것이라면, 금융 전문가로서 일반적이고 도움이 되는 조언을 친절하고 이해하기 쉬운 말투로 작성해주세요."
    )
    
    messages_for_openai = []
    messages_for_openai.append({"role": "system", "content": system_prompt_content})
    
    for msg in previous_messages:
        if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
            messages_for_openai.append(msg)
        else:
            logger.warning(f"이전 대화 중 유효하지 않은 메시지 형식 발견: {msg}")

    enriched_user_message = user_message
    if db_product_info_str:
        enriched_user_message += db_product_info_str
            
    messages_for_openai.append({"role": "user", "content": enriched_user_message})

    logger.debug(f"OpenAI API로 전송할 메시지 목록: {json.dumps(messages_for_openai, ensure_ascii=False, indent=2)}")

    chat_response_content = "죄송합니다, 현재 답변을 드릴 수 없습니다. 잠시 후 다시 시도해주세요. (ERR_DEFAULT)"

    try:
        logger.info("OpenAI API 호출 시작 (모델: gpt-4o-mini)")
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=messages_for_openai,
            temperature=0.6, 
            timeout=30.0,
        )
        
        logger.info("OpenAI API 호출 성공")
        logger.debug(f"OpenAI API 전체 응답 (Raw Response): {response}")

        if response and response.choices and len(response.choices) > 0:
            choice = response.choices[0]
            if choice.message and choice.message.content is not None:
                chat_response_content = choice.message.content.strip()
                logger.info(f"OpenAI로부터 받은 답변 내용 (일부): {chat_response_content[:100]}...")
                if choice.finish_reason == 'length':
                    chat_response_content += "\n[주의: 답변이 최대 길이 제한으로 인해 잘렸을 수 있습니다.]"
                    logger.warning("OpenAI 응답이 길이 제한으로 잘림.")
                elif choice.finish_reason and choice.finish_reason != 'stop':
                    chat_response_content = f"답변 생성 중단됨 (사유: {choice.finish_reason}). (ERR_FINISH_REASON)"
                    logger.warning(f"OpenAI 답변 생성 중단됨: {choice.finish_reason}")
            else: 
                chat_response_content = "AI가 답변을 생성했지만 내용이 없습니다. (ERR_EMPTY_MSG_CONTENT)"
                logger.error("OpenAI 응답에 유효한 메시지 내용이 없음.")
        else: 
            chat_response_content = "AI로부터 유효한 선택지를 받지 못했습니다. (ERR_NO_CHOICES)"
            logger.error("OpenAI 응답에 유효한 choices가 없음.")
        
        logger.info(f"클라이언트로 최종 응답 전송: {chat_response_content[:100]}...")
        return Response({"response": chat_response_content})

    except RateLimitError as e:
        logger.error(f"OpenAI RateLimitError (할당량 초과 가능성): {str(e)} | HTTP Status: {e.status_code} | Error Code: {e.code}", exc_info=True)
        return Response({"error": "API 사용량 제한에 도달했습니다. 관리자에게 문의하거나 요금제를 확인해주세요. (ERR_RATE_LIMIT)", "details": str(e)}, status=429)
    except AuthenticationError as e:
        logger.error(f"OpenAI AuthenticationError (API 키 인증 실패): {str(e)} | HTTP Status: {e.status_code} | Error Code: {e.code}", exc_info=True)
        return Response({"error": "OpenAI API 키 인증에 실패했습니다. 서버 설정을 확인해주세요. (ERR_AUTH)", "details": str(e)}, status=401)
    except APITimeoutError as e:
        logger.error(f"OpenAI APITimeoutError (요청 시간 초과): {str(e)}", exc_info=True)
        return Response({"error": "OpenAI API 요청 처리 시간이 초과되었습니다. (ERR_TIMEOUT)", "details": str(e)}, status=504)
    except APIError as e: 
        logger.error(f"OpenAI APIError (일반 API 오류): {str(e)} | HTTP Status: {e.status_code} | Error Code: {e.code}", exc_info=True)
        return Response({"error": f"OpenAI API 통신 중 오류가 발생했습니다. (ERR_API_GENERAL - CODE: {e.code or 'N/A'})", "details": str(e)}, status=e.status_code or 500)
    except BadRequestError as e: 
        logger.error(f"OpenAI BadRequestError (잘못된 요청): {str(e)} | Param: {e.param if hasattr(e, 'param') else 'N/A'}", exc_info=True)
        return Response({"error": f"OpenAI API에 잘못된 요청을 보냈습니다. (ERR_BAD_REQUEST - PARAM: {e.param if hasattr(e, 'param') else 'N/A'})", "details": str(e)}, status=400)
    except Exception as e: 
        logger.error(f"챗봇 응답 처리 중 예기치 않은 내부 오류 발생: {str(e)}", exc_info=True)
        return Response({"error": f"챗봇 응답 처리 중 서버 내부 오류가 발생했습니다. (ERR_UNEXPECTED_INTERNAL)", "details": str(e)}, status=500)