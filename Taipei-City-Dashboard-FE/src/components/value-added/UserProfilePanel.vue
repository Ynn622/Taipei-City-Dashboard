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
  background: var(--color-overlay);
  display: grid;
  place-items: center;
  z-index: 2000;
  padding: 1rem;

  .profile-modal-panel {
    width: min(760px, 100%);
    border-radius: 5px;
    border: solid 1px var(--color-border);
    background: var(--color-component-background);
    box-shadow: none;
    padding: var(--font-m);
    color: var(--color-normal-text);

    .modal-head {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 0.8rem;
      margin-bottom: 1rem;

      .eyebrow {
        margin: 0 0 0.3rem;
        font-size: 0.72rem;
        letter-spacing: 0.16em;
        color: var(--color-complement-text);
      }

      h3 {
        margin: 0;
        font-size: 1.2rem;
        color: var(--color-normal-text);
      }

      .icon-btn {
        width: 32px;
        height: 32px;
        border-radius: 5px;
        border: solid 1px var(--color-border);
        background: transparent;
        color: var(--color-complement-text);
        font-size: 1.2rem;
        cursor: pointer;
      }
    }
  }

  .panel-content {
    padding: 0;
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;

    .form-group {
      flex: 1 1 calc(50% - 0.5rem);
      display: flex;
      flex-direction: column;
      gap: 0.45rem;

      &.full-row {
        flex-basis: 100%;
      }

      label {
        font-weight: 600;
        font-size: 0.82rem;
        color: var(--color-complement-text);
      }

      input,
      textarea {
        padding: 0.62rem 0.72rem;
        border: solid 1px var(--color-border);
        border-radius: 5px;
        background: var(--color-background);
        color: var(--color-normal-text);
        outline: none;

        &::placeholder {
          color: var(--color-complement-text);
        }

        &:focus {
          border-color: var(--color-highlight);
          box-shadow: 0 0 0 1px var(--color-highlight);
        }
      }
    }
  }

  .modal-actions {
    margin-top: 1rem;
    display: flex;
    justify-content: flex-end;
    gap: 0.6rem;

    .ghost-btn,
    .save-btn {
      border-radius: 0.68rem;
      padding: 0.5rem 0.92rem;
      border: 1px solid transparent;
      font-weight: 600;
      cursor: pointer;
    }

    .ghost-btn {
      border-color: var(--color-border);
      background: transparent;
      color: var(--color-complement-text);
    }

    .save-btn {
      border-color: var(--color-highlight);
      background: rgba(90, 156, 248, 0.16);
      color: var(--color-normal-text);
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
      justify-content: stretch;

      .ghost-btn,
      .save-btn {
        width: 100%;
      }
    }
  }
}
</style>
