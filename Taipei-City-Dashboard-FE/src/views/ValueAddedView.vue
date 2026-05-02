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
    gap: var(--font-m);
  }

  .value-added-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: var(--font-m);
    padding: var(--font-m);
    border: solid 1px var(--color-border);
    border-radius: 5px;
    background: var(--color-component-background);

    .title-area {
      .eyebrow {
        margin: 0 0 0.3rem;
        font-size: 0.72rem;
        letter-spacing: 0.18em;
        color: var(--color-complement-text);
      }

      h1 {
        margin: 0;
        font-size: 1.65rem;
        color: var(--color-normal-text);
      }

      .subtitle {
        margin: 0.35rem 0 0;
        color: var(--color-complement-text);
      }
    }

    .profile-actions {
      display: flex;
      align-items: center;
      gap: var(--font-s);

      .profile-chip {
        display: flex;
        flex-direction: column;
        padding: 0.5rem 0.75rem;
        border: solid 1px var(--color-border);
        border-radius: 5px;
        background: var(--color-background);

        .chip-label {
          font-size: 0.72rem;
          color: var(--color-complement-text);
        }

        strong {
          font-size: 0.92rem;
          color: var(--color-normal-text);
        }
      }

      .open-profile-btn {
        border: solid 1px var(--color-highlight);
        background: transparent;
        color: var(--color-highlight);
        font-weight: 600;
        padding: 0.55rem 0.9rem;
        border-radius: 5px;
        cursor: pointer;
        transition: all 0.2s ease;

        &:hover {
          background: rgba(90, 156, 248, 0.16);
        }
      }
    }
  }

  .value-added-tabs {
    display: flex;
    flex-wrap: wrap;
    gap: var(--font-s);

    button {
      padding: 0.48rem 0.9rem;
      background: var(--color-component-background);
      border: solid 1px var(--color-border);
      border-radius: 999px;
      color: var(--color-complement-text);
      font-size: 0.94rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;

      &.active {
        border-color: var(--color-highlight);
        color: var(--color-normal-text);
        background: rgba(90, 156, 248, 0.16);
      }

      &:hover {
        color: var(--color-normal-text);
        border-color: var(--color-highlight);
      }
    }
  }

  .value-added-content {
    flex: 1;
  }

  @media (max-width: 860px) {
    width: calc(100% - (var(--font-s) * 2));
    margin: var(--font-s) var(--font-s);

    .value-added-header {
      flex-direction: column;
      align-items: stretch;

      .profile-actions {
        justify-content: space-between;
      }
    }
  }
}
</style>
