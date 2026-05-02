<script setup>
import { ref, watch } from "vue";
import { useValueAddedStore } from "../../store/valueAddedStore";

const props = defineProps({
	open: {
		type: Boolean,
		default: false,
	},
});

const emit = defineEmits(["close"]);

const store = useValueAddedStore();

const localProfile = ref({
	name: "",
	focusDistrictsText: "",
	focusCategoriesText: "",
	notes: "",
});

const setLocalProfileFromStore = () => {
	localProfile.value = {
		name: store.userProfile.name || "",
		focusDistrictsText: Array.isArray(store.userProfile.focusDistricts)
			? store.userProfile.focusDistricts.join(", ")
			: store.userProfile.focusDistricts || "",
		focusCategoriesText: Array.isArray(store.userProfile.focusCategories)
			? store.userProfile.focusCategories.join(", ")
			: store.userProfile.focusCategories || "",
		notes: store.userProfile.notes || "",
	};
};

watch(
	() => props.open,
	(isOpen) => {
		if (isOpen) {
			setLocalProfileFromStore();
		}
	},
	{ immediate: true }
);

const parseCommaSeparated = (value) => {
	return value
		.split(",")
		.map((item) => item.trim())
		.filter((item) => item.length > 0);
};

const save = () => {
	store.saveProfile({
		name: localProfile.value.name,
		focusDistricts: parseCommaSeparated(localProfile.value.focusDistrictsText),
		focusCategories: parseCommaSeparated(localProfile.value.focusCategoriesText),
		notes: localProfile.value.notes,
	});
	emit("close");
};

const close = () => {
	emit("close");
};
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
              PROFILE CONFIGURATION
            </p>
            <h3>用戶輪廓設定</h3>
          </div>
          <button
            class="icon-btn"
            @click="close"
          >
            ×
          </button>
        </div>

        <div class="panel-content">
          <div class="form-group">
            <label>稱呼 / 姓名</label>
            <input
              v-model="localProfile.name"
              type="text"
              placeholder="例如：張先生"
            >
          </div>
          <div class="form-group">
            <label>關注行政區</label>
            <input
              v-model="localProfile.focusDistrictsText"
              type="text"
              placeholder="例如：大安區, 信義區 (逗號分隔)"
            >
          </div>
          <div class="form-group">
            <label>關注食安類型</label>
            <input
              v-model="localProfile.focusCategoriesText"
              type="text"
              placeholder="例如：餐廳, 市場 (逗號分隔)"
            >
          </div>
          <div class="form-group full-row">
            <label>備註</label>
            <textarea
              v-model="localProfile.notes"
              placeholder="其他需求或備註..."
            />
          </div>
        </div>

        <div class="modal-actions">
          <button
            class="ghost-btn"
            @click="close"
          >
            取消
          </button>
          <button
            class="save-btn"
            @click="save"
          >
            儲存並更新
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
    width: min(760px, 100%);
    border-radius: 8px;
    border: solid 1px rgba(255, 255, 255, 0.1);
    background: var(--color-component-background);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
    padding: var(--font-m);
    color: var(--color-normal-text);
    position: relative;
    overflow: hidden;

    &::before {
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 1px;
      background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    }

    .modal-head {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 0.8rem;
      margin-bottom: 1.5rem;

      .eyebrow {
        margin: 0 0 0.4rem;
        font-size: 0.75rem;
        letter-spacing: 0.2em;
        font-weight: 600;
        color: var(--color-highlight);
      }

      h3 {
        margin: 0;
        font-size: 1.25rem;
        font-weight: 800;
        color: var(--color-normal-text);
        letter-spacing: 0.02em;
      }

      .icon-btn {
        width: 32px;
        height: 32px;
        border-radius: 6px;
        border: solid 1px transparent;
        background: rgba(255, 255, 255, 0.05);
        color: var(--color-complement-text);
        font-size: 1.2rem;
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

  .panel-content {
    padding: 0;
    display: flex;
    flex-wrap: wrap;
    gap: 1.2rem;

    .form-group {
      flex: 1 1 calc(50% - 0.6rem);
      display: flex;
      flex-direction: column;
      gap: 0.5rem;

      &.full-row {
        flex-basis: 100%;
      }

      label {
        font-weight: 600;
        font-size: 0.85rem;
        color: var(--color-complement-text);
        letter-spacing: 0.02em;
      }

      input,
      textarea {
        padding: 0.75rem 0.85rem;
        border: solid 1px rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        background: rgba(0, 0, 0, 0.2);
        color: var(--color-normal-text);
        outline: none;
        transition: all 0.3s ease;

        &::placeholder {
          color: rgba(255, 255, 255, 0.3);
        }

        &:focus {
          border-color: var(--color-highlight);
          background: rgba(0, 0, 0, 0.3);
          box-shadow: 0 0 0 3px rgba(90, 156, 248, 0.15);
        }
      }
    }
  }

  .modal-actions {
    margin-top: 1.8rem;
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
      border-color: var(--color-highlight);
      background: rgba(90, 156, 248, 0.1);
      color: var(--color-normal-text);
      box-shadow: 0 4px 12px rgba(90, 156, 248, 0.1);

      &:hover {
        background: rgba(90, 156, 248, 0.2);
        box-shadow: 0 4px 15px rgba(90, 156, 248, 0.2);
        transform: translateY(-1px);
      }
    }
  }
}

@media (max-width: 640px) {
  .profile-modal-overlay {
    .panel-content {
      .form-group {
        flex-basis: 100%;
      }
    }

    .modal-actions {
      flex-direction: column;

      .ghost-btn,
      .save-btn {
        width: 100%;
      }
    }
  }
}
</style>
