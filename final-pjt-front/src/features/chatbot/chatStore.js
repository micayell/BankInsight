import { ref } from 'vue'
import { defineStore } from 'pinia'
import api from '@/features/shared/api/api.js'
import { useUserStore } from '../accounts/store/userStore.js'

export const useChatStore = defineStore('chat', () => {
  const chatMessages = ref([]) 
  const newMessage = ref('') 
  const CHATBOT_ENDPOINT = '/api/v1/chatbot/' 

  const getAIResponse = async (messageText) => { 
    const userStore = useUserStore()

    if (!userStore.isLogin || !userStore.token) {
      chatMessages.value.push({
        sender: 'bot',
        text: '챗봇을 이용하려면 로그인이 필요합니다.'
      });
      return;
    }

    if (!messageText || messageText.trim() === '') { 
      console.warn('빈 메시지는 전송하지 않습니다.');
      return;
    }

    chatMessages.value.push({ 
      sender: 'user',
      text: messageText,
    });

    const previousMessagesForPayload = chatMessages.value 
      .slice(0, -1) 
      .map(msg => ({
        role: msg.sender === 'user' ? 'user' : 'assistant',
        content: msg.text
      }));

    const payload = {
      message: messageText, 
      messages: previousMessagesForPayload,
    };
    
    console.log('백엔드로 전송할 페이로드:', JSON.stringify(payload, null, 2));

    try {
      const response = await api.post(CHATBOT_ENDPOINT, payload, {
        headers: {
          'Authorization': `Token ${userStore.token}`
        }
      });
      
      console.log('백엔드로부터 받은 전체 응답 (Raw Response):', response);
      console.log('백엔드 응답 데이터 (Response Data):', response.data);

      if (response.data && typeof response.data.response === 'string' && response.data.response.trim() !== '') {
        chatMessages.value.push({ 
          sender: 'bot',
          text: response.data.response,
        });
        console.log('챗봇 응답이 채팅에 추가됨:', response.data.response);
      } else if (response.data && typeof response.data.error === 'string') {
        console.error('백엔드에서 에러 응답:', response.data.error, response.data.details || '');
        chatMessages.value.push({ 
          sender: 'bot',
          text: `챗봇 오류: ${response.data.error} ${response.data.details ? '('+response.data.details+')' : ''}`,
        });
      } else {
        console.warn('백엔드로부터 유효하지 않은 챗봇 응답 내용(response.data.response)을 받지 못했습니다. 받은 데이터:', response.data);
        chatMessages.value.push({ 
          sender: 'bot',
          text: '챗봇으로부터 응답을 받았으나 내용이 비어있습니다. 다시 시도해주세요.',
        });
      }
      
    } catch (error) {
      console.error('메시지 전송 중 Axios 오류 발생:', error.response || error.message || error);
      let errorMessageToDisplay = '죄송합니다, 챗봇 서버와 통신 중 오류가 발생했습니다.';
      if (error.response && error.response.data && typeof error.response.data.error === 'string') {
        errorMessageToDisplay = `서버 오류: ${error.response.data.error}`;
        if (error.response.data.details) {
            errorMessageToDisplay += ` (상세: ${error.response.data.details})`;
        }
      } else if (error.message) {
        errorMessageToDisplay = `통신 오류: ${error.message}`;
      }
      chatMessages.value.push({ 
        sender: 'bot',
        text: errorMessageToDisplay,
      });
    }
  };

  return {
    chatMessages, 
    newMessage, 
    getAIResponse, 
  }
}, { persist: true })