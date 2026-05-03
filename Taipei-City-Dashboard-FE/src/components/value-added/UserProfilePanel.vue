<script setup>
import { computed, nextTick, ref, watch } from "vue";
import { useValueAddedStore } from "../../store/valueAddedStore";

const props = defineProps({
	open: {
		type: Boolean,
		default: false,
	},
});

const emit = defineEmits(["close"]);

const store = useValueAddedStore();
const inputText = ref("");
const loading = ref(false);
const chatBody = ref(null);
const messages = ref([]);
const locationText = ref("");
const dateRangeText = ref("");

const initialMessage = "你好，我會用幾個問題幫你建立實策輪廓。你是民眾、餐飲業者，還是政府/治理單位？";

const audienceLabel = computed(() => {
	const labels = {
		B: "B 端業者",
		C: "C 端民眾",
		G: "G 端治理",
	};
	return labels[store.userProfile.audienceType] || "尚未判定";
});

const profileChips = computed(() => {
	const profile = store.userProfile;
	const chips = [
		audienceLabel.value,
		...(profile.focusDistricts || []),
		...(profile.allergens || []).map((item) => `過敏原：${item}`),
		...(profile.foodSafetySensitivityTypes || []).map((item) => `敏感：${item}`),
		profile.businessCategory ? `餐飲類別：${profile.businessCategory}` : "",
	].filter(Boolean);
	return chips.length ? chips : ["等待聊天建立輪廓"];
});

watch(
	() => props.open,
	async (isOpen) => {
		if (!isOpen) return;
		messages.value = [{ role: "assistant", content: initialMessage }];
		inputText.value = "";
		locationText.value = store.userProfile.userLocation
			? `${store.userProfile.userLocation.lat}, ${store.userProfile.userLocation.lng}`
			: "";
		dateRangeText.value = store.userProfile.dateRangeText || "";
		await scrollToBottom();
	},
	{ immediate: true }
);

async function submitMessage() {
	const content = inputText.value.trim();
	if (!content || loading.value) return;

	messages.value.push({ role: "user", content });
	inputText.value = "";
	loading.value = true;
	await scrollToBottom();

	const result = await store.chatProfileAssistant(messages.value);
	messages.value.push({
		role: "assistant",
		content: result.reply || "我已更新輪廓，還可以繼續補充所在地、過敏原或餐飲類別。",
	});
	loading.value = false;
	await scrollToBottom();
}

function useQuickPrompt(text) {
	inputText.value = text;
	submitMessage();
}

function resetConversation() {
	store.resetProfile();
	messages.value = [{ role: "assistant", content: initialMessage }];
	inputText.value = "";
	locationText.value = "";
	dateRangeText.value = "";
}

function close() {
	emit("close");
}

function saveProfileOptions() {
	store.saveProfile({
		userLocation: parseLocation(locationText.value),
		dateRangeText: dateRangeText.value.trim(),
	});
}

function parseLocation(value) {
	const parts = value.split(/[,，\s]+/).map(Number).filter((item) => Number.isFinite(item));
	return parts.length >= 2 ? { lat: parts[0], lng: parts[1] } : null;
}

function useBrowserLocation() {
	if (!navigator.geolocation) return;
	navigator.geolocation.getCurrentPosition((position) => {
		locationText.value = `${position.coords.latitude.toFixed(6)}, ${position.coords.longitude.toFixed(6)}`;
		saveProfileOptions();
	});
}

async function scrollToBottom() {
	await nextTick();
	if (chatBody.value) {
		chatBody.value.scrollTop = chatBody.value.scrollHeight;
	}
}
</script>

<template>
  <teleport to="body">
    <div
      v-if="open"
      class="profile-modal-overlay"
      @click.self="close"
    >
      <div class="profile-modal-panel">
        <div class="modal-head">
          <div>
            <p class="eyebrow">
              PROFILE CHAT
            </p>
            <h3>用聊天設定輪廓</h3>
          </div>
          <button
            class="icon-btn"
            aria-label="關閉"
            @click="close"
          >
            close
          </button>
        </div>

        <div class="profile-layout">
          <section class="chat-panel">
            <div
              ref="chatBody"
              class="chat-body"
            >
              <div
                v-for="(message, index) in messages"
                :key="`${message.role}-${index}`"
                class="chat-message"
                :class="message.role"
              >
                <span class="message-role">
                  {{ message.role === "user" ? "你" : "助理" }}
                </span>
                <p>{{ message.content }}</p>
              </div>
              <div
                v-if="loading"
                class="chat-message assistant"
              >
                <span class="message-role">助理</span>
                <p>正在整理輪廓...</p>
              </div>
            </div>

            <div class="quick-prompts">
              <button @click="useQuickPrompt('我是民眾，想設定 C 端輪廓')">
                C 民眾
              </button>
              <button @click="useQuickPrompt('我是餐飲業者，想設定 B 端輪廓')">
                B 業者
              </button>
              <button @click="useQuickPrompt('我是政府或治理單位，想設定 G 端輪廓')">
                G 治理
              </button>
            </div>

            <form
              class="chat-input-row"
              @submit.prevent="submitMessage"
            >
              <input
                v-model="inputText"
                type="text"
                :disabled="loading"
                placeholder="例如：我是民眾，住大安區，對海鮮過敏，重視餐廳衛生"
              >
              <button
                type="submit"
                :disabled="loading || !inputText.trim()"
              >
                send
              </button>
            </form>
          </section>

          <aside class="profile-summary">
            <span class="summary-label">目前輪廓</span>
            <strong>{{ audienceLabel }}</strong>
            <div class="chip-list">
              <span
                v-for="chip in profileChips"
                :key="chip"
              >
                {{ chip }}
              </span>
            </div>
            <div class="profile-fields">
              <label>
                <span>目前位置 lat, lng</span>
                <input
                  v-model="locationText"
                  type="text"
                  placeholder="25.033, 121.565"
                  @change="saveProfileOptions"
                >
              </label>
              <button
                type="button"
                class="locate-btn"
                @click="useBrowserLocation"
              >
                使用定位
              </button>
              <label>
                <span>日期區間</span>
                <input
                  v-model="dateRangeText"
                  type="text"
                  placeholder="20260101-20260131"
                  @change="saveProfileOptions"
                >
              </label>
            </div>
          </aside>
        </div>

        <div class="modal-actions">
          <button
            class="ghost-btn"
            @click="resetConversation"
          >
            清除重來
          </button>
          <button
            class="save-btn"
            @click="close"
          >
            完成
          </button>
        </div>
      </div>
    </div>
  </teleport>
</template>

<style scoped lang="scss">
.profile-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  display: grid;
  place-items: center;
  z-index: 2000;
  padding: 1rem;

  .profile-modal-panel {
    width: min(880px, 100%);
    height: min(760px, calc(100vh - 2rem));
    border-radius: 8px;
    border: solid 1px rgba(255, 255, 255, 0.12);
    background: var(--color-component-background);
    box-shadow: 0 18px 54px rgba(0, 0, 0, 0.46);
    padding: var(--font-m);
    color: var(--color-normal-text);
    display: flex;
    flex-direction: column;
    overflow: hidden;

    .modal-head {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 0.8rem;
      margin-bottom: 1rem;

      .eyebrow {
        margin: 0 0 0.35rem;
        font-size: 0.75rem;
        letter-spacing: 0;
        font-weight: 600;
        color: var(--color-complement-text);
      }

      h3 {
        margin: 0;
        font-size: 1.25rem;
        font-weight: 800;
        color: var(--color-normal-text);
        letter-spacing: 0;
      }

      .icon-btn {
        width: 32px;
        height: 32px;
        border-radius: 6px;
        border: solid 1px transparent;
        background: rgba(255, 255, 255, 0.05);
        color: var(--color-complement-text);
        font-family: var(--font-icon);
        font-size: 1.15rem;
        cursor: pointer;
        display: grid;
        place-items: center;
        transition: all 0.2s ease;

        &:hover {
          background: rgba(255, 255, 255, 0.1);
          color: var(--color-normal-text);
        }
      }
    }
  }
}

.profile-layout {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 250px;
  gap: 1rem;
}

.chat-panel,
.profile-summary {
  min-height: 0;
  border: solid 1px rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  background: rgba(9, 9, 9, 0.24);
}

.chat-panel {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.chat-message {
  max-width: 82%;
  min-height: fit-content;
  flex: 0 0 auto;
  padding: 0.78rem 0.85rem;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--color-normal-text);

  &.user {
    align-self: flex-end;
    background: rgba(92, 155, 255, 0.16);
  }

  &.assistant {
    align-self: flex-start;
  }

  .message-role {
    display: block;
    margin-bottom: 0.35rem;
    font-size: 0.72rem;
    color: var(--color-complement-text);
  }

  p {
    margin: 0;
    line-height: 1.55;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
  }
}

.quick-prompts {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 0 1rem 0.85rem;

  button {
    border: solid 1px rgba(255, 255, 255, 0.12);
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.05);
    color: var(--color-complement-text);
    padding: 0.45rem 0.7rem;
    cursor: pointer;

    &:hover {
      color: var(--color-normal-text);
      background: rgba(255, 255, 255, 0.08);
    }
  }
}

.chat-input-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 44px;
  gap: 0.55rem;
  padding: 0.85rem 1rem 1rem;
  border-top: solid 1px rgba(255, 255, 255, 0.08);

  input {
    min-width: 0;
    height: 44px;
    padding: 0.78rem 0.85rem;
    border: solid 1px rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    background: rgba(9, 9, 9, 0.35);
    color: var(--color-normal-text);
    line-height: 1.25;
    outline: none;

    &::placeholder {
      color: rgba(255, 255, 255, 0.32);
    }

    &:focus {
      border-color: rgba(255, 255, 255, 0.22);
      box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.08);
    }
  }

  button {
    width: 44px;
    height: 44px;
    border: solid 1px rgba(255, 255, 255, 0.14);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.07);
    color: var(--color-normal-text);
    font-family: var(--font-icon);
    font-size: 1.15rem;
    cursor: pointer;

    &:disabled {
      opacity: 0.45;
      cursor: not-allowed;
    }
  }
}

.profile-summary {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;

  .summary-label {
    color: var(--color-complement-text);
    font-size: 0.75rem;
    font-weight: 700;
  }

  strong {
    font-size: 1.1rem;
  }
}

.chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;

  span {
    max-width: 100%;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.06);
    color: var(--color-complement-text);
    padding: 0.42rem 0.62rem;
    font-size: 0.78rem;
    overflow-wrap: anywhere;
  }
}

.profile-fields {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;

  label {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    color: var(--color-complement-text);
    font-size: 0.76rem;
  }

  input {
    min-width: 0;
    border: solid 1px rgba(255, 255, 255, 0.12);
    border-radius: 7px;
    background: rgba(9, 9, 9, 0.35);
    color: var(--color-normal-text);
    padding: 0.58rem 0.65rem;
    outline: none;
  }

  .locate-btn {
    border: solid 1px rgba(255, 255, 255, 0.14);
    border-radius: 7px;
    background: rgba(255, 255, 255, 0.06);
    color: var(--color-normal-text);
    padding: 0.55rem 0.7rem;
    cursor: pointer;
  }
}

.modal-actions {
  margin-top: 1rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.8rem;

  .ghost-btn,
  .save-btn {
    border-radius: 6px;
    padding: 0.65rem 1.2rem;
    border: 1px solid transparent;
    font-weight: 600;
    font-size: 0.95rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .ghost-btn {
    border-color: rgba(255, 255, 255, 0.15);
    background: transparent;
    color: var(--color-complement-text);

    &:hover {
      background: rgba(255, 255, 255, 0.05);
      color: var(--color-normal-text);
    }
  }

  .save-btn {
    border-color: rgba(255, 255, 255, 0.14);
    background: rgba(255, 255, 255, 0.08);
    color: var(--color-normal-text);

    &:hover {
      background: rgba(255, 255, 255, 0.12);
    }
  }
}

@media (max-width: 760px) {
  .profile-modal-overlay {
    align-items: stretch;
  }

  .profile-modal-overlay .profile-modal-panel {
    height: calc(100vh - 2rem);
  }

  .profile-layout {
    grid-template-columns: 1fr;
  }

  .chat-body {
    min-height: 0;
  }

  .modal-actions {
    flex-direction: column;

    .ghost-btn,
    .save-btn {
      width: 100%;
    }
  }
}
</style>
