<script setup>
defineProps({
	title: {
		type: String,
		required: true,
	},
	subtitle: {
		type: String,
		default: "",
	},
	loading: {
		type: Boolean,
		default: false,
	},
	error: {
		type: String,
		default: "",
	},
	wide: {
		type: Boolean,
		default: false,
	},
});
</script>

<template>
  <section
    class="value-card"
    :class="{ wide }"
  >
    <header class="card-head">
      <div>
        <h3>{{ title }}</h3>
        <p v-if="subtitle">
          {{ subtitle }}
        </p>
      </div>
      <slot name="action" />
    </header>
    <div
      v-if="loading"
      class="state"
    >
      資料載入中...
    </div>
    <div
      v-else-if="error"
      class="state error"
    >
      {{ error }}
    </div>
    <div
      v-else
      class="card-body"
    >
      <slot />
    </div>
  </section>
</template>

<style scoped lang="scss">
.value-card {
  position: relative;
  min-height: 206px;
  padding: 1rem;
  border: solid 1px rgba(255, 255, 255, 0.09);
  border-radius: 8px;
  background: var(--color-component-background);
  color: var(--color-normal-text);
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.16);
  overflow: hidden;

  &.wide {
    grid-column: 1 / -1;
  }

  .card-head {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 0.75rem;
    margin-bottom: 0.95rem;
    padding-bottom: 0.75rem;
    border-bottom: solid 1px rgba(255, 255, 255, 0.07);

    h3 {
      margin: 0;
      color: var(--color-normal-text);
      font-size: 1.02rem;
      line-height: 1.35;
      font-weight: 700;
    }

    p {
      margin: 0.32rem 0 0;
      color: var(--color-complement-text);
      font-size: 0.8rem;
      line-height: 1.45;
    }
  }

  .state {
    flex-grow: 1;
    display: grid;
    place-items: center;
    color: var(--color-complement-text);
    font-size: 0.95rem;
    min-height: 130px;

    &.error {
      color: #E86F51;
      background: rgba(232, 111, 81, 0.05);
      border: solid 1px rgba(232, 111, 81, 0.18);
      border-radius: 8px;
      padding: 1rem;
    }
  }

  .card-body {
    display: flex;
    flex-direction: column;
    gap: 0.9rem;
    flex-grow: 1;
  }
}

:slotted(.summary-grid) {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.65rem;
}

:slotted(.summary-item) {
  min-width: 0;
  padding: 0.72rem 0.78rem;
  border: solid 1px rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  background: rgba(9, 9, 9, 0.32);
}

:slotted(.summary-label) {
  color: var(--color-complement-text);
  font-size: 0.78rem;
  line-height: 1.4;
  margin-bottom: 0.3rem;
}

:slotted(.summary-value) {
  color: var(--color-normal-text);
  font-size: 1.12rem;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: 0;
  overflow-wrap: anywhere;
}

:slotted(.rank-list) {
  display: flex;
  flex-direction: column;
  gap: 0.62rem;
}

:slotted(.rank-row) {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 0.75rem;
  align-items: center;
  color: var(--color-normal-text);
  font-size: 0.9rem;
  padding: 0.25rem 0;
}

:slotted(.bar-track) {
  grid-column: 1 / -1;
  height: 6px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
}

:slotted(.bar-fill) {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--color-highlight);
}

:slotted(.note) {
  color: var(--color-complement-text);
  font-size: 0.86rem;
  line-height: 1.6;
  margin-top: auto;
  padding: 0.7rem 0.75rem 0;
  border-top: solid 1px rgba(255, 255, 255, 0.07);
}

:slotted(.suggestion) {
  white-space: pre-line;
  color: var(--color-normal-text);
  font-size: 0.92rem;
  line-height: 1.7;
  padding: 0.75rem 0.85rem;
  border-left: 3px solid rgba(255, 255, 255, 0.12);
  background: rgba(90, 156, 248, 0.08);
  border-radius: 0 8px 8px 0;
}

:slotted(.action-btn) {
  min-height: 34px;
  border: solid 1px rgba(255, 255, 255, 0.14);
  border-radius: 7px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--color-normal-text);
  font-weight: 600;
  padding: 0.48rem 0.75rem;
  font-size: 0.86rem;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.18);
  }
}

@media (max-width: 640px) {
  :slotted(.summary-grid) {
    grid-template-columns: 1fr;
  }
}
</style>
