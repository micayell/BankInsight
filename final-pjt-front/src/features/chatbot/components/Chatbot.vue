<template>
  <div class="chatbot-container h-100 d-flex flex-column bg-white">
    <!-- Chatbot Header (Toss Style) -->
    <div class="chatbot-header p-3 border-bottom d-flex align-items-center">
      <div class="header-icon bg-light text-primary rounded-circle d-flex justify-content-center align-items-center me-3">
        <i class="bi bi-robot fs-5"></i>
      </div>
      <div>
        <h5 class="mb-0 fw-bold">무엇이든 물어보세요</h5>
        <small class="text-muted">24시간 AI 금융비서</small>
      </div>
    </div>

    <!-- Chat Messages Window -->
    <div class="chat-window flex-grow-1 p-3 overflow-auto" ref="chatWindowRef">
      <!-- Bot Welcome Message -->
      <div v-if="chatStore.chatMessages.length === 0" class="message-row bot-row mb-3 justify-content-start">
        <div class="message-bubble bot-bubble px-3 py-2 bg-light text-dark">
          <p class="message-text mb-0 text-break" style="white-space: pre-wrap;">반갑습니다! 금융상품 추천, 가입 방법, 금리 비교 등 투자나 업무에 관해서 어떤 것이든 편하게 물어보세요 ✨</p>
        </div>
      </div>
      
      <div
        v-for="(message, index) in chatStore.chatMessages" :key="index"
        class="message-row mb-3 d-flex"
        :class="message.sender === 'user' ? 'user-row justify-content-end' : 'bot-row justify-content-start'"
      >
        <div class="message-bubble px-3 py-2 shadow-sm" :class="message.sender === 'user' ? 'user-bubble text-white bg-primary' : 'bot-bubble bg-light text-dark'">
          <p class="message-text mb-0 text-break" style="white-space: pre-wrap;">{{ message.text }}</p>

          <!-- 추천 상품 바로가기 버튼 영역 -->
          <div v-if="message.recommendedProducts && message.recommendedProducts.length > 0" class="mt-3 pt-3 border-top border-secondary-subtle">
            <p class="mb-2 fw-semibold text-primary" style="font-size: 0.85rem;"><i class="bi bi-link-45deg"></i> 추천 상품 상세 보기:</p>
            <div class="d-flex flex-column gap-2">
              <button 
                v-for="product in message.recommendedProducts" 
                :key="product.code"
                class="btn btn-sm btn-outline-primary text-start fw-medium rounded-3"
                @click="goToProduct(product.type, product.code)">
                {{ product.name }} ➡
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading / Typing Indicator -->
      <div v-if="chatStore.isLoading" class="message-row bot-row mb-3 justify-content-start">
        <div class="message-bubble bot-bubble px-3 py-2 bg-light text-dark d-flex align-items-center" style="min-height: 48px; min-width: 64px;">
          <div class="typing-indicator mx-2">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="input-area p-3 bg-white border-top">
      <div class="input-group rounded-pill overflow-hidden" style="background-color: #f2f4f6; border: 1px solid #e5e8eb;">
        <input
          type="text"
          class="form-control border-0 bg-transparent shadow-none px-4 py-2"
          v-model="userInput"
          placeholder="챗봇에게 물어보세요..."
          @keyup.enter="handleSendMessage"
          :disabled="chatStore.isLoading"
        />
        <button 
          class="btn btn-primary rounded-pill px-4 m-1 fw-bold border-0 shadow-none" 
          @click="handleSendMessage" 
          :disabled="!userInput.trim() || chatStore.isLoading"
        >
          <i class="bi bi-send-fill fs-6"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useChatStore } from '@/features/chatbot/store/chatStore.js'; 

const chatStore = useChatStore();
const router = useRouter();
const userInput = ref('');
const chatWindowRef = ref(null); 

const handleSendMessage = () => {
  if (userInput.value.trim() && !chatStore.isLoading) {
    chatStore.getAIResponse(userInput.value); 
    userInput.value = ''; 
  }
};

const goToProduct = (type, code) => {
  if (type === 'deposit') {
    router.push({ name: 'deposit-detail', params: { code } });
  } else if (type === 'saving') {
    router.push({ name: 'saving-detail', params: { code } });
  }
};

const scrollToBottomDOM = () => {
  if (chatWindowRef.value) {
    chatWindowRef.value.scrollTop = chatWindowRef.value.scrollHeight;
  }
};

// Array length change (new message)
watch(() => chatStore.chatMessages.length, () => {
  nextTick(() => {
    scrollToBottomDOM();
  });
});

// Loading state change (bouncing dots hide/show)
watch(() => chatStore.isLoading, () => {
  nextTick(() => {
    scrollToBottomDOM();
  });
});
</script>

<style scoped>
.chatbot-container {
  font-family: "Pretendard", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  border-radius: 16px;
}
.header-icon {
  width: 44px;
  height: 44px;
  background-color: #e8f3ff !important; /* soft blue */
  color: #3182f6 !important;
}
.chat-window {
  background-color: #ffffff;
  scroll-behavior: smooth;
}
.message-row {
  display: flex;
}
.message-bubble {
  max-width: 85%;
  border-radius: 20px;
  line-height: 1.5;
  font-size: 0.95rem;
}
.user-bubble {
  border-bottom-right-radius: 4px;
  background-color: #3182f6 !important; /* toss blue */
}
.bot-bubble {
  border-bottom-left-radius: 4px;
  background-color: #f2f4f6 !important; 
  color: #191f28 !important;
}
.input-area .btn-primary {
  background-color: #3182f6 !important;
}
.input-area .btn-primary:active {
  background-color: #1b64da !important;
}
.input-area .btn-primary:disabled {
  background-color: #b0c4de !important;
  color: white !important;
  cursor: not-allowed;
}
.form-control::placeholder {
  color: #8b95a1;
  font-weight: 500;
}
/* Hide scrollbar for a cleaner Toss feel */
.chat-window::-webkit-scrollbar {
  width: 6px;
}
.chat-window::-webkit-scrollbar-thumb {
  background-color: #e5e8eb;
  border-radius: 3px;
}

/* Typing Indicator Animation */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 5px;
}
.typing-dot {
  width: 7px;
  height: 7px;
  background-color: #8b95a1;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out both;
}
.typing-dot:nth-child(1) { animation-delay: -0.32s; }
.typing-dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}
</style>
