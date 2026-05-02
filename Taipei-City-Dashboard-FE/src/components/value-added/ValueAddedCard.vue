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
  min-height: 188px;
  padding: 1rem;
  border: solid 1px var(--color-border);
  border-radius: 5px;
  background: var(--color-component-background);
  color: var(--color-normal-text);
  display: flex;
  flex-direction: column;

  &.wide {
    grid-column: 1 / -1;
  }

  .card-head {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 0.75rem;
    margin-bottom: 0.85rem;

    h3 {
      margin: 0;
      color: var(--color-normal-text);
      font-size: 1rem;
      font-weight: 700;
    }

    p {
      margin: 0.32rem 0 0;
      color: var(--color-complement-text);
      font-size: 0.82rem;
      line-height: 1.45;
    }
  }

  .state {
    flex-grow: 1;
    display: grid;
    place-items: center;
    color: var(--color-complement-text);
    font-size: 0.95rem;

    &.error {
      color: #E86F51;
      background: rgba(232, 111, 81, 0.05);
      border-radius: 5px;
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
  gap: 0.6rem;
}

:slotted(.summary-item) {
  min-width: 0;
  padding: 0.72rem;
  border: solid 1px var(--color-border);
  border-radius: 5px;
  background: var(--color-background);
}

:slotted(.summary-label) {
  color: var(--color-complement-text);
  font-size: 0.78rem;
  line-height: 1.4;
  margin-bottom: 0.3rem;
}

:slotted(.summary-value) {
  color: var(--color-normal-text);
  font-size: 1.18rem;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: 0.01em;
}

:slotted(.rank-list) {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

:slotted(.rank-row) {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 0.75rem;
  align-items: center;
  color: var(--color-normal-text);
  font-size: 0.9rem;
}

:slotted(.bar-track) {
  grid-column: 1 / -1;
  height: 5px;
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
  padding-top: 0.5rem;
}

:slotted(.suggestion) {
  white-space: pre-line;
  color: var(--color-normal-text);
  font-size: 0.92rem;
  line-height: 1.7;
  padding: 0.45rem 0;
  border-left: 3px solid #1E88E5;
  padding-left: 0.8rem;
  background: rgba(30, 136, 229, 0.05);
  border-radius: 0 4px 4px 0;
}

:slotted(.action-btn) {
  border: solid 1px #1E88E5;
  border-radius: 5px;
  background: rgba(30, 136, 229, 0.1);
  color: var(--color-normal-text);
  font-weight: 600;
  padding: 0.55rem 0.8rem;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s ease;

  &:hover {
    background: rgba(30, 136, 229, 0.2);
  }
}

@media (max-width: 640px) {
  :slotted(.summary-grid) {
    grid-template-columns: 1fr;
  }
}
</style>
