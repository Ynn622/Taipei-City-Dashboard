<script setup>
import { ref } from "vue";
import { useValueAddedStore } from "../store/valueAddedStore";
import UserProfilePanel from "../components/value-added/UserProfilePanel.vue";
import FeatureMetricsBar from "../components/value-added/FeatureMetricsBar.vue";
import OperationsView from "../components/value-added/tabs/OperationsView.vue";
import PolicyView from "../components/value-added/tabs/PolicyView.vue";
import LifeGuideView from "../components/value-added/tabs/LifeGuideView.vue";

const valueAddedStore = useValueAddedStore();
const activeTab = ref("operations");
const isProfileModalOpen = ref(false);

const tabs = [
	{ id: "operations", name: "營運管理" },
	{ id: "policy", name: "政策分析" },
	{ id: "lifeguide", name: "生活指南" },
];

const openProfileModal = () => {
	isProfileModalOpen.value = true;
};

const closeProfileModal = () => {
	isProfileModalOpen.value = false;
};
</script>

<template>
  <div class="value-added-view">
    <div class="value-added-shell">
      <div class="value-added-top">
        <div class="value-added-header">
          <div class="title-area">
            <p class="eyebrow">
              VALUE-ADDED SERVICES
            </p>
            <h1>加值服務控制台</h1>
            <p class="subtitle">
              以夜間模式整合營運管理、政策分析與生活指南。
            </p>
          </div>
          <div class="profile-actions">
            <div class="profile-chip">
              <span class="chip-label">目前輪廓</span>
              <strong>{{ valueAddedStore.userProfile.name || "尚未設定" }}</strong>
            </div>
            <button
              class="open-profile-btn"
              @click="openProfileModal"
            >
              設定用戶輪廓
            </button>
          </div>
        </div>
        <FeatureMetricsBar />
      </div>
      
      <div class="value-added-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          {{ tab.name }}
        </button>
      </div>

      <div class="value-added-content">
        <OperationsView v-if="activeTab === 'operations'" />
        <PolicyView v-if="activeTab === 'policy'" />
        <LifeGuideView v-if="activeTab === 'lifeguide'" />
      </div>
    </div>

    <UserProfilePanel
      :open="isProfileModalOpen"
      @close="closeProfileModal"
    />
  </div>
</template>

<style scoped lang="scss">
.value-added-view {
  box-sizing: border-box;
  width: calc(100% - (var(--font-m) * 2));
  height: calc(100vh - 127px);
  height: calc(var(--vh) * 100 - 127px);
  margin: var(--font-m) var(--font-m);
  overflow-y: auto;
  overflow-x: hidden;

  .value-added-shell {
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
  }

  .value-added-top {
    display: grid;
    grid-template-columns: minmax(260px, 1fr) minmax(0, 3fr);
    gap: 0.85rem;
    align-items: stretch;
  }

  .value-added-header {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 1rem;
    min-height: 236px;
    padding: 1rem;
    border: solid 1px var(--color-border);
    border-radius: 5px;
    background: var(--color-component-background);

    .title-area {
      .eyebrow {
        margin: 0 0 0.35rem;
        font-size: 0.72rem;
        letter-spacing: 0.12em;
        font-weight: 600;
        color: var(--color-complement-text);
        text-transform: uppercase;
      }

      h1 {
        margin: 0;
        font-size: 1.45rem;
        font-weight: 700;
        color: var(--color-normal-text);
      }

      .subtitle {
        margin: 0.45rem 0 0;
        color: var(--color-complement-text);
        line-height: 1.55;
        font-size: 0.86rem;
      }
    }

    .profile-actions {
      display: flex;
      flex-direction: column;
      align-items: stretch;
      gap: 0.6rem;

      .profile-chip {
        display: flex;
        flex-direction: column;
        padding: 0.58rem 0.7rem;
        border: solid 1px var(--color-border);
        border-radius: 5px;
        background: var(--color-background);

        .chip-label {
          font-size: 0.72rem;
          color: var(--color-complement-text);
        }

        strong {
          font-size: 0.96rem;
          color: var(--color-normal-text);
        }
      }

      .open-profile-btn {
        border: solid 1px var(--color-highlight);
        background: transparent;
        color: var(--color-highlight);
        font-weight: 600;
        padding: 0.58rem 0.8rem;
        border-radius: 5px;
        cursor: pointer;
        transition: background 0.2s ease, color 0.2s ease;

        &:hover {
          background: rgba(90, 156, 248, 0.12);
          color: var(--color-normal-text);
        }
      }
    }
  }

  .value-added-tabs {
    display: flex;
    flex-wrap: wrap;
    gap: 0;
    width: fit-content;
    max-width: 100%;
    padding: 0.25rem;
    border: solid 1px var(--color-border);
    border-radius: 5px;
    background: var(--color-component-background);

    button {
      min-width: 96px;
      padding: 0.5rem 0.9rem;
      background: transparent;
      border: solid 1px transparent;
      border-radius: 4px;
      color: var(--color-complement-text);
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.2s ease, color 0.2s ease;

      &:hover {
        background: rgba(255, 255, 255, 0.05);
        color: var(--color-normal-text);
      }

      &.active {
        color: var(--color-normal-text);
        background: rgba(90, 156, 248, 0.16);
        border-color: rgba(90, 156, 248, 0.35);
      }
    }
  }

  .value-added-content {
    flex: 1;
  }

  @media (max-width: 860px) {
    width: calc(100% - (var(--font-s) * 2));
    margin: var(--font-s) var(--font-s);

    .value-added-top {
      grid-template-columns: 1fr;
    }

    .value-added-header {
      .profile-actions {
        flex-direction: column;
      }
    }
  }

  @media (max-width: 640px) {
    .value-added-tabs {
      width: 100%;

      button {
        flex: 1 1 0;
        min-width: 0;
      }
    }
  }
}
</style>
