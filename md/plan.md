# Plan: 實策 Tab 新增

## TL;DR
在 NavBar 新增「實策」Tab（路由 `/value-added`），頁面上半部顯示可設定的用戶輪廓欄位，下半部以「營運管理」、「政策分析」、「生活指南」三個 Tab 呈現加值功能（呼叫現有 component API + 新增 LLM API 串接）。所有擁有實策的用戶均可見全部三個功能分頁。

---

## Phase 1：基礎路由與 Layout

### Step 1 — 新增路由
- 檔案：`Taipei-City-Dashboard-FE/src/router/index.js`
- 在 `/mapview` 之後新增：
  ```
  { path: '/value-added', name: 'ValueAdded', component: ValueAddedView }
  ```
- router guard 無需特別處理（所有人可進入，未登入者不顯示角色功能）

### Step 2 — NavBar 新增 Tab
- 檔案：`Taipei-City-Dashboard-FE/src/components/utilities/bars/NavBar.vue`
- 在「地圖交叉比對」router-link 之後，加入「實策」tab
- 不需傳 linkQuery（實策不依賴 dashboard index）

### Step 3 — App.vue Layout 分支
- 檔案：`Taipei-City-Dashboard-FE/src/App.vue`
- 在現有 v-if/else-if 鏈中新增 `value-added` 分支
- 不需 SideBar/SettingsBar，直接 RouterView 全版面

---

## Phase 2：狀態管理

### Step 4 — 新增 valueAddedStore.js
- 位置：`Taipei-City-Dashboard-FE/src/store/valueAddedStore.js`
- 責任：
  - `userProfile`: 物件，儲存用戶輪廓欄位（姓名/職稱/關注區域/關注類型等通用欄位）
  - `componentCache`: Map<componentId, data>，快取已抓的組件資料
  - `llmResult`: Map<featureKey, string>，LLM 回傳建議文字
  - action: `fetchComponentData(id)` — 呼叫 `/component/{id}/chart`
  - action: `fetchLLMSuggestion(featureKey, prompt)` — 呼叫 LLM API（端點：`/llm/suggest`）
  - action: `saveProfile(profile)` — 儲存輪廓並 localStorage 持久化

### 用戶輪廓欄位（通用，不分角色）：
- `name`（姓名/稱呼）
- `focusDistricts`（關注行政區，多選）
- `focusCategories`（關注食安類型，多選：餐廳/市場/農產/水質/…）
- `notes`（其他備註/自由輸入）

---

## Phase 3：主 View 與共用 UI

### Step 5 — ValueAddedView.vue
- 位置：`Taipei-City-Dashboard-FE/src/views/ValueAddedView.vue`
- 結構：
  ```
  <UserProfilePanel />      ← 用戶輪廓輸入欄位（通用，可摺疊）
  <FeatureMetricsBar />     ← 上方：儀表指標（KPI卡）
  [ 營運管理 | 政策分析 | 生活指南 ]  ← 三個功能 Tab
  ```

### Step 6 — UserProfilePanel.vue
- 位置：`Taipei-City-Dashboard-FE/src/components/value-added/UserProfilePanel.vue`
- 可摺疊面板；通用輪廓欄位（關注行政區、關注類型、備註）
- 輸入後按「更新」觸發相關功能重新計算

### Step 7 — FeatureMetricsBar.vue
- 位置：`Taipei-City-Dashboard-FE/src/components/value-added/FeatureMetricsBar.vue`
- 顯示通用 KPI 卡（2-4 張）：
  - 全臺違規總數（組件7+8）
  - 本週高風險區域數（組件7）
  - 優良農場供應商數（組件11）
  - 近期腹瀉就診趨勢（組件4）

---

## Phase 4：加值功能分頁

### 功能分頁結構
`ValueAddedView.vue` 下半部為三個固定 Tab，所有用戶皆可見：「營運管理」、「政策分析」、「生活指南」。

### Step 8 — 營運管理分頁（OperationsView.vue）
位置：`Taipei-City-Dashboard-FE/src/components/value-added/tabs/OperationsView.vue`

子組件（各為獨立卡片）：
1. `OpsSupplierRecommend.vue`：安全供應來源推薦 → 組件11（food_source, ID 307）
2. `OpsDangerSourceAlert.vue`：危險來源迴避 → 組件11，處理類型統計
3. `OpsAuditRiskPrediction.vue`：稽查風險預測 → 組件7（health_audit_violation, ID 309）+ 組件8（food_audit_violation, ID 308）
4. `OpsInsuranceEstimate.vue`：保險精算 → 組件5（water_quality, ID 306）+ 組件6（health_office, ID 305）
5. `OpsImproveSuggestion.vue`：LLM 改善建議 → 組件11 + 呼叫 `/llm/suggest`

### Step 9 — 政策分析分頁（PolicyView.vue）
位置：`Taipei-City-Dashboard-FE/src/components/value-added/tabs/PolicyView.vue`

子組件：
1. `PolRiskHeatmap.vue`：食安風險熱區地圖 → 組件7；可選色階方式（行政區/時段）
2. `PolRootCauseAnalysis.vue`：風險根源與影響 → 組件7 + 組件10
3. `PolAuditPriority.vue`：稽查優先排序 → 組件7 + 組件1
4. `PolTrendAnalysis.vue`：趨勢分析（標出劇烈變化） → 組件7
5. `PolEventScope.vue`：食安事件範圍推斷（物流/市場/水源）→ 組件3 + 組件5
6. `PolImproveSuggestion.vue`：LLM 改善建議 → 組件11 + 呼叫 `/llm/suggest`

### Step 10 — 生活指南分頁（LifeGuideView.vue）
位置：`Taipei-City-Dashboard-FE/src/components/value-added/tabs/LifeGuideView.vue`

子組件：
1. `LifeFoodSpin.vue`：今天吃什麼？食物轉盤 → 組件1（優良餐廳）+ LLM 偏好理解
2. `LifeRestaurantSafety.vue`：餐廳食安評估 → 組件7 + 組件4（cdc_infectious, ID 502）+ 組件5
3. `LifeQuickHelp.vue`：快速求助 → 組件10（醫療/申訴）
4. `LifeFoodIdentity.vue`：食物身分證 → 組件11 + 組件3（market, ID 303）

---

## Phase 5：LLM 整合

### Step 11 — LLM Service
- 位置：`Taipei-City-Dashboard-FE/src/store/valueAddedStore.js`（整合於 store 的 action）
- 端點：`POST /llm/suggest`，request body：`{ role, profile, context, feature }`
- 回傳：串流或一次性文字（先做一次性，同 chatStore pattern）
- 各 LLM 功能卡片 mounted 時，如有用戶輪廓則自動觸發

---

## 關鍵檔案清單

| 動作 | 檔案路徑 |
|------|---------|
| 修改 | `Taipei-City-Dashboard-FE/src/router/index.js` |
| 修改 | `Taipei-City-Dashboard-FE/src/components/utilities/bars/NavBar.vue` |
| 修改 | `Taipei-City-Dashboard-FE/src/App.vue` |
| 新增 | `Taipei-City-Dashboard-FE/src/store/valueAddedStore.js` |
| 新增 | `Taipei-City-Dashboard-FE/src/views/ValueAddedView.vue` |
| 新增 | `Taipei-City-Dashboard-FE/src/components/value-added/UserProfilePanel.vue` |
| 新增 | `Taipei-City-Dashboard-FE/src/components/value-added/FeatureMetricsBar.vue` |
| 新增 | `Taipei-City-Dashboard-FE/src/components/value-added/tabs/OperationsView.vue` + 5個子組件 |
| 新增 | `Taipei-City-Dashboard-FE/src/components/value-added/tabs/PolicyView.vue` + 6個子組件 |
| 新增 | `Taipei-City-Dashboard-FE/src/components/value-added/tabs/LifeGuideView.vue` + 4個子組件 |

---

## 組件 ID 對照表
| 組件編號（需求文件） | index | ID | 名稱 |
|---|---|---|---|
| 組件1 | food_safety_good_restaurant | 待確認 | 優良餐廳 |
| 組件3 | food_safety_market | 303 | 食物來源（市場） |
| 組件4 | cdc_infectious_disease | 502 | 腹瀉就診數量 |
| 組件5 | water_quality | 306 | 淨水場水質 |
| 組件6 | food_safety_health_office | 305 | 衛生局據點 |
| 組件7 | health_audit_violation | 309 | 衛生稽核違規 |
| 組件8 | food_audit_violation | 308 | 食品稽核違規 |
| 組件10 | (待確認) | 待確認 | 醫療/申訴 |
| 組件11 | food_source | 307 | 有機農場 |

---

## Verification
1. `/value-added` 路由能正確導航，NavBar active 狀態正確
2. 用戶輪廓資料存於 localStorage（`valueAdded_profile`），重新整理後保留
3. 三個功能 Tab（營運管理/政策分析/生活指南）切換正常，不依賴任何角色判斷
4. 功能卡片呼叫 `/component/{id}/chart` 能成功取得資料
5. LLM 功能卡片呼叫 `/llm/suggest` 並顯示回傳文字

## Decisions
- 角色 B/G/C 概念已完全移除，不存於 localStorage，不影響任何功能顯示
- LLM 端點暫定 `/llm/suggest`，待實際 key 到位後確認路由
- 實策頁面不共用 SideBar/SettingsBar，全版面自行配置
- 組件1（優良餐廳）ID 待確認，不阻擋實作，可用 index 查詢
