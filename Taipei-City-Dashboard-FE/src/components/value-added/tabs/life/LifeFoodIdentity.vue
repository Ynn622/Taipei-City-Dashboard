<script setup>
import { computed, onMounted, ref } from "vue";
import { useValueAddedStore } from "../../../../store/valueAddedStore";
import ValueAddedCard from "../../ValueAddedCard.vue";
import { COMPONENT_IDS, topRows } from "../../valueAddedAnalytics";

const store = useValueAddedStore();
const loading = ref(true);
const sourceRows = ref([]);
const marketRows = ref([]);
const question = ref("");
const messages = ref([
	{ role: "assistant", text: "想追溯哪一種食材？例如：蛋從哪裡來、蔬菜可能經過哪些市場。" },
]);

onMounted(async () => {
	const [source, market] = await Promise.all([
		store.fetchComponentData(COMPONENT_IDS.foodSource),
		store.fetchComponentData(COMPONENT_IDS.market),
	]);
	sourceRows.value = source;
	marketRows.value = market;
	loading.value = false;
});

const sourceTop = computed(() => topRows(sourceRows.value, 3));
const marketTop = computed(() => topRows(marketRows.value, 3));

function ask() {
	const text = question.value.trim();
	if (!text) return;
	messages.value.push({ role: "user", text });
	messages.value.push({
		role: "assistant",
		text: `依目前資料，可先從「${sourceTop.value[0]?.label || "主要農場來源"}」追到「${marketTop.value[0]?.label || "市場節點"}」，再核對批號、進貨日期與販售端。若要更精準，需要補該食材的批號或店家名稱。`,
	});
	question.value = "";
}
</script>

<template>
  <ValueAddedCard
    title="食物身分證"
    subtitle="用聊天問答追溯食材來源、批號與銷售節點。"
    :loading="loading"
  >
    <div class="identity-chat">
      <div class="chat-log">
        <p
          v-for="(message, index) in messages"
          :key="index"
          :class="message.role"
        >
          {{ message.text }}
        </p>
      </div>
      <form @submit.prevent="ask">
        <input
          v-model="question"
          type="text"
          placeholder="例如：蛋從哪裡來？"
        >
        <button type="submit">
          send
        </button>
      </form>
    </div>
  </ValueAddedCard>
</template>

<style scoped lang="scss">
.identity-chat {
  display: grid;
  gap: 0.8rem;
}

.chat-log {
  display: grid;
  gap: 0.6rem;
  max-height: 220px;
  overflow-y: auto;

  p {
    margin: 0;
    padding: 0.65rem 0.75rem;
    border-radius: 8px;
    color: var(--color-normal-text);
    background: rgba(255, 255, 255, 0.055);
    line-height: 1.5;
  }

  .user {
    justify-self: end;
    background: rgba(92, 155, 255, 0.16);
  }
}

form {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 44px;
  gap: 0.5rem;

  input {
    min-width: 0;
    border: solid 1px rgba(255, 255, 255, 0.12);
    border-radius: 7px;
    background: rgba(9, 9, 9, 0.35);
    color: var(--color-normal-text);
    padding: 0.65rem 0.75rem;
  }

  button {
    border: solid 1px rgba(255, 255, 255, 0.14);
    border-radius: 7px;
    background: rgba(255, 255, 255, 0.07);
    color: var(--color-normal-text);
    font-family: var(--font-icon);
  }
}
</style>
