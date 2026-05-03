<script setup>
import { computed, ref } from "vue";
import { useValueAddedStore } from "../store/valueAddedStore";
import UserProfilePanel from "../components/value-added/UserProfilePanel.vue";
import FeatureMetricsBar from "../components/value-added/FeatureMetricsBar.vue";
import OperationsView from "../components/value-added/tabs/OperationsView.vue";
import PolicyView from "../components/value-added/tabs/PolicyView.vue";
import LifeGuideView from "../components/value-added/tabs/LifeGuideView.vue";

const valueAddedStore = useValueAddedStore();
const activeTab = ref("policy");
const isProfileModalOpen = ref(false);

const tabs = [
	{
		id: "policy",
		name: "政策分析",
		icon: "query_stats",
		count: 6,
		description: "區域熱點、事件規模與政策優先序",
	},
	{
		id: "operations",
		name: "營運管理",
		icon: "analytics",
		count: 5,
		description: "食安營運風險、供應商與改善建議",
	},
	{
		id: "lifeguide",
		name: "生活指南",
		icon: "restaurant",
		count: 4,
		description: "飲食推薦、餐廳安全與民眾快查",
	},
];

const profileSummary = computed(() => {
	const {
		audienceType,
		focusDistricts,
		focusCategories,
		allergens,
		businessCategory,
	} = valueAddedStore.userProfile;
	const audienceLabels = {
		B: "B 端業者",
		C: "C 端民眾",
		G: "G 端治理",
	};
	const audience = audienceLabels[audienceType] || "尚未設定";
	const districts = Array.isArray(focusDistricts) && focusDistricts.length
		? focusDistricts.join("、")
		: "待補所在地";
	const categories = businessCategory ||
		(Array.isArray(focusCategories) && focusCategories.length
			? focusCategories.join("、")
			: "待補偏好");
	const allergenText = Array.isArray(allergens) && allergens.length
		? allergens.join("、")
		: "未設定";
	return { audience, districts, categories, allergenText };
});

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
      <section class="value-added-top">
        <div class="hero-panel">
          <div class="hero-main">
            <div class="service-mark">
              <span>add_chart</span>
            </div>
            <div class="title-area">
              <h1>加值服務</h1>
            </div>
          </div>

          <div class="profile-panel">
            <div class="profile-heading">
              <div class="profile-title">
                <span class="material-icon">account_circle</span>
                <div>
                  <span class="chip-label">目前輪廓</span>
                  <strong>{{ profileSummary.audience }}</strong>
                </div>
              </div>
              <button
                class="open-profile-btn"
                @click="openProfileModal"
              >
                <span>tune</span>
                設定
              </button>
            </div>
            <div class="profile-details">
              <div>
                <span>所在地</span>
                <strong>{{ profileSummary.districts }}</strong>
              </div>
              <div>
                <span>{{ valueAddedStore.userProfile.audienceType === "C" ? "過敏原" : "類型" }}</span>
                <strong>
                  {{ valueAddedStore.userProfile.audienceType === "C" ? profileSummary.allergenText : profileSummary.categories }}
                </strong>
              </div>
              <div v-if="valueAddedStore.userProfile.audienceType === 'C'">
                <span>敏感類型</span>
                <strong>{{ profileSummary.categories }}</strong>
              </div>
            </div>
          </div>
        </div>
        <FeatureMetricsBar />
      </section>
      
      <div class="value-added-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          <span class="tab-icon">{{ tab.icon }}</span>
          <span class="tab-copy">
            <strong>{{ tab.name }}</strong>
            <small>{{ tab.description }}</small>
          </span>
          <span class="tab-count">{{ tab.count }}</span>
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
  color: var(--color-normal-text);

  .value-added-shell {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    min-height: 100%;
  }

  .value-added-top {
    display: grid;
    grid-template-columns: minmax(0, 3fr) minmax(220px, 1fr);
    gap: 1rem;
    align-items: stretch;
  }

  .hero-panel {
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 1.1rem;
    min-height: 246px;
    padding: 1.15rem;
    border: solid 1px rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    background: var(--color-component-background);
    box-shadow: 0 12px 34px rgba(0, 0, 0, 0.2);

    > * {
      position: relative;
      z-index: 1;
    }

    .hero-main {
      display: flex;
      gap: 0.85rem;
      align-items: flex-start;
    }

    .service-mark {
      width: 42px;
      height: 42px;
      flex: 0 0 42px;
      display: grid;
      place-items: center;
      border-radius: 8px;
      border: solid 1px rgba(255, 255, 255, 0.12);
      background: rgba(255, 255, 255, 0.06);

      span {
        font-family: var(--font-icon);
        font-size: 1.5rem;
        color: var(--color-normal-text);
      }
    }

    .title-area {
      .eyebrow {
        margin: 0 0 0.35rem;
        font-size: 0.72rem;
        letter-spacing: 0;
        font-weight: 600;
        color: var(--color-complement-text);
        text-transform: uppercase;
      }

      h1 {
        margin: 0;
        font-size: 2rem;
        line-height: 1.08;
        font-weight: 800;
        color: var(--color-normal-text);
      }

      .subtitle {
        margin: 0.45rem 0 0;
        color: var(--color-complement-text);
        line-height: 1.55;
        font-size: 0.86rem;
      }
    }

    .profile-panel {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      padding: 0.8rem;
      border: solid 1px rgba(255, 255, 255, 0.1);
      border-radius: 8px;
      background: rgba(9, 9, 9, 0.42);

      .profile-heading {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.58rem;

        .profile-title {
          min-width: 0;
          display: flex;
          align-items: center;
          gap: 0.58rem;
        }

        .material-icon {
          width: 34px;
          height: 34px;
          flex: 0 0 34px;
          display: grid;
          place-items: center;
          border-radius: 8px;
          background: rgba(255, 255, 255, 0.07);
          color: var(--color-normal-text);
          font-family: var(--font-icon);
          font-size: 1.35rem;
        }

        .chip-label {
          display: block;
          font-size: 0.72rem;
          color: var(--color-complement-text);
        }

        strong {
          display: block;
          font-size: 0.96rem;
          color: var(--color-normal-text);
          line-height: 1.35;
          overflow-wrap: anywhere;
        }
      }

      .profile-details {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.5rem;

        div {
          min-width: 0;
          min-height: 72px;
          padding: 0.78rem 0.78rem;
          border-radius: 7px;
          background: rgba(255, 255, 255, 0.045);
          display: flex;
          flex-direction: column;
          justify-content: center;
        }

        span,
        strong {
          display: block;
        }

        span {
          margin-bottom: 0.22rem;
          color: var(--color-complement-text);
          font-size: 0.78rem;
        }

        strong {
          color: var(--color-normal-text);
          font-size: 1rem;
          line-height: 1.35;
          overflow-wrap: anywhere;
        }
      }

      .open-profile-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 0.35rem;
        flex: 0 0 auto;
        min-height: 34px;
        border: solid 1px rgba(255, 255, 255, 0.14);
        background: rgba(255, 255, 255, 0.06);
        color: var(--color-normal-text);
        font-weight: 600;
        padding: 0.45rem 0.68rem;
        border-radius: 7px;
        cursor: pointer;
        transition: background 0.2s ease, border-color 0.2s ease;

        span {
          font-family: var(--font-icon);
          font-size: 1.1rem;
          color: inherit;
        }

        &:hover {
          background: rgba(255, 255, 255, 0.08);
          border-color: rgba(255, 255, 255, 0.18);
        }
      }
    }
  }

  .value-added-tabs {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.75rem;
    max-width: 100%;
    padding: 0.75rem;
    border: solid 1px rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    background: rgba(40, 42, 44, 0.88);

    button {
      min-width: 0;
      min-height: 78px;
      display: grid;
      grid-template-columns: 34px minmax(0, 1fr) auto;
      gap: 0.65rem;
      align-items: center;
      padding: 0.72rem;
      background: rgba(255, 255, 255, 0.035);
      border: solid 1px rgba(255, 255, 255, 0.06);
      border-radius: 8px;
      color: var(--color-complement-text);
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
      text-align: left;
      transition: background 0.2s ease, border-color 0.2s ease, transform 0.2s ease;

      .tab-icon {
        width: 34px;
        height: 34px;
        display: grid;
        place-items: center;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.06);
        color: var(--color-normal-text);
        font-family: var(--font-icon);
        font-weight: normal;
        font-style: normal;
        font-size: 1.25rem;
        line-height: 1;
        font-feature-settings: "liga";
        text-transform: none;
      }

      .tab-copy {
        min-width: 0;
        display: flex;
        flex-direction: column;
        gap: 0.18rem;

        strong,
        small {
          min-width: 0;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        strong {
          color: var(--color-normal-text);
          font-size: 0.94rem;
          line-height: 1.25;
        }

        small {
          color: var(--color-complement-text);
          font-size: 0.74rem;
          line-height: 1.35;
        }
      }

      .tab-count {
        min-width: 30px;
        height: 28px;
        display: grid;
        place-items: center;
        border-radius: 7px;
        background: rgba(255, 255, 255, 0.05);
        color: var(--color-complement-text);
        font-size: 0.78rem;
      }

      &:hover {
        transform: translateY(-1px);
        background: rgba(255, 255, 255, 0.06);
        border-color: rgba(255, 255, 255, 0.12);
      }

      &.active {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(255, 255, 255, 0.18);

        .tab-count {
          color: var(--color-normal-text);
          background: rgba(255, 255, 255, 0.08);
        }
      }
    }
  }

  .value-added-content {
    flex: 1;
  }

  @media (max-width: 860px) {
    width: calc(100% - (var(--font-s) * 2));
    margin: var(--font-s) var(--font-s);

    .value-added-tabs {
      grid-template-columns: 1fr;
    }
  }

  @media (max-width: 640px) {
    .value-added-top {
      grid-template-columns: 1fr;
    }

    .hero-panel {
      .hero-main {
        flex-direction: column;
      }

      .profile-panel {
        .profile-details {
          grid-template-columns: 1fr;
        }
      }
    }

    .value-added-tabs button {
      grid-template-columns: 30px minmax(0, 1fr) auto;
      min-height: 70px;
    }
  }
}
</style>
