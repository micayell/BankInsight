import { defineStore } from "pinia";
import { ref } from "vue";
import { productApi } from "@/features/products/api/productApi.js";
import { useUserStore } from "../../accounts/store/userStore.js";

export const useRecommendStore = defineStore('recommend', () => {
    const recommendFirst = ref([]);
    const recommendSecond = ref([]);
    const userStore = useUserStore();

    const getRecommendFirst = async function () {
        if (!userStore.userInfo?.username) {
            console.error("추천 상품을 조회하기 위해 사용자 정보가 필요합니다.");
            return;
        }
        try {
            const [depositRes, savingRes] = await Promise.all([
                productApi.getRecommendFirstDeposit(userStore.userInfo.username),
                productApi.getRecommendFirstSaving(userStore.userInfo.username)
            ]);
            recommendFirst.value = [...depositRes.data, ...savingRes.data];
        } catch (error) {
            console.error("첫 번째 추천 상품 조회 실패:", error);
            recommendFirst.value = [];
        }
    };

    const getRecommendSecond = async function () {
        if (!userStore.userInfo?.username) {
            console.error("추천 상품을 조회하기 위해 사용자 정보가 필요합니다.");
            return;
        }
        try {
            const [depositRes, savingRes] = await Promise.all([
                productApi.getRecommendSecondDeposit(userStore.userInfo.username),
                productApi.getRecommendSecondSaving(userStore.userInfo.username)
            ]);
            recommendSecond.value = [...depositRes.data, ...savingRes.data];
        } catch (error) {
            console.error("두 번째 추천 상품 조회 실패:", error);
            recommendSecond.value = [];
        }
    };

    return { getRecommendFirst, recommendFirst, getRecommendSecond, recommendSecond };
}, { persist: true });