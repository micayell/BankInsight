<template>
  <div class="chatbot-container">
    <div class="chat-window" ref="chatWindowRef">
      <div
        v-for="(message, index) in chatStore.chatMessages" :key="index"
        class="message-row"
        :class="message.sender === 'user' ? 'user-row' : 'bot-row'"
      >
        <div class="message-bubble" :class="message.sender === 'user' ? 'user-bubble' : 'bot-bubble'">
          <p class="message-text">{{ message.text }}</p>
        </div>
      </div>
      </div>
    <div class="input-area">
      <input
        type="text"
        v-model="userInput"
        placeholder="챗봇에게 물어보세요!"
        @keyup.enter="handleSendMessage"
        :disabled="false" />
      <button @click="handleSendMessage" :disabled="!userInput.trim()">전송</button> </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';
import { useChatStore } from '@/features/chatbot/store/chatStore.js'; 

const chatStore = useChatStore();
const userInput = ref('');
const chatWindowRef = ref(null); 

const handleSendMessage = () => {
  if (userInput.value.trim()) {
    chatStore.getAIResponse(userInput.value); 
    userInput.value = ''; 
  }
};

const scrollToBottomDOM = () => {
  const element = chatWindowRef.value;
  if (element) {
    element.scrollTop = element.scrollHeight;
  }
};

watch(
  () => chatStore.chatMessages, 
  async () => {
    await nextTick(); 
    scrollToBottomDOM();
  },
  { deep: true } 
);

onMounted(() => {
  scrollToBottomDOM();
});

</script>

<style scoped>
/* 스타일은 동일하게 유지 */
.chatbot-container {
  display: flex;
  flex-direction: column;
  width: 100%; 
  height: 100%; 
  border: none; 
  border-radius: 8px; 
  box-shadow: none; 
  font-family: 'Helvetica Neue', Arial, sans-serif;
  overflow: hidden;
  background-color: #ffffff; 
}

.chat-window {
  flex-grow: 1;
  padding: 15px;
  overflow-y: auto;
  background-color: #f9f9f9;
  display: flex;
  flex-direction: column;
}

.message-row {
  display: flex;
  margin-bottom: 12px;
  max-width: 95%; 
}
.user-row {
  justify-content: flex-end;
  align-self: flex-end; 
}
.bot-row {
  justify-content: flex-start;
  align-self: flex-start; 
}

.message-bubble {
  padding: 10px 15px;
  border-radius: 20px;
  max-width: 85%; 
  word-wrap: break-word;
}
.message-text {
  margin: 0;
  white-space: pre-wrap;
  font-size: 0.95em;
  line-height: 1.4;
}

.user-bubble {
  background-color: #007bff;
  color: white;
  border-bottom-right-radius: 5px;
}

.bot-bubble {
  background-color: #e9ecef;
  color: #343a40;
  border-bottom-left-radius: 5px;
}

.loading-message, .error-message {
  text-align: center;
  color: #6c757d;
  padding: 15px;
  font-style: italic;
}
.error-message {
  color: red;
}

.input-area {
  display: flex;
  padding: 12px;
  border-top: 1px solid #e0e0e0;
  background-color: #fff;
}

.input-area input[type="text"] {
  flex-grow: 1;
  padding: 10px 12px;
  border: 1px solid #ced4da;
  border-radius: 20px;
  margin-right: 10px;
  font-size: 0.95em;
  outline: none;
}
.input-area input[type="text"]:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
}

.input-area button {
  padding: 10px 18px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.95em;
  transition: background-color 0.2s ease;
}
.input-area button:hover {
  background-color: #0056b3;
}
.input-area button:disabled {
  background-color: #b0c4de;
  cursor: not-allowed;
}
</style>