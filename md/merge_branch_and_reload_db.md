# 整併其他分支組件並重新載入 Docker 資料

這份流程用在「把其他分支的新組件、新圖層或新 dashboard 合進目前分支」之後，重啟原始 Docker 環境並重新載入資料。

本專案目前統一使用 `docker/` 底下的原始 Docker compose：

- `docker-compose-db.yaml`：Postgres、Redis、pgAdmin、Qdrant
- `docker-compose-init.yaml`：FE npm install、manager DB 初始化、dashboard data DB 初始化
- `docker-compose.yaml`：nginx、FE、BE、vector upgrade

不要再使用 `*.isolated.yaml` 或 `taipei_private_*` 那套設定。

## 先確認分支內容

整併前先看對方分支改了哪些類型的檔案：

```bash
git status --short
git fetch
git diff --name-status HEAD..origin/<branch-name>
```

常見檔案分工：

- `db-sample-data/dashboardmanager-demo.sql`：sidebar、dashboard、component、map/chart config
- `db-sample-data/dashboard-demo.sql`：demo 用的 dashboard data dump；若 component 資料由 DE DAG/API 產生，不要把整包資料手動塞回這裡
- `Taipei-City-Dashboard-FE/public/mapData/*.geojson`：前端地圖圖資
- `Taipei-City-Dashboard-DE/dags/**`：ETL / Airflow DAG
- `Taipei-City-Dashboard-FE/src/**`：前端 UI 或圖表行為
- `Taipei-City-Dashboard-BE/**`：API 或資料查詢邏輯

如果新增 component，至少要確認：

- `components.id` 沒有撞號
- `components.index` 和 `component_charts.index`、`query_charts.index` 一致
- `dashboards.components` 有包含新 component id
- `dashboard_groups` 有把 dashboard 放到正確 group
- chart SQL 查到的資料表真的存在於 `postgres-data` 的 `dashboard` database
- 若 chart SQL 查的是新 DAG table，要確認 `Taipei-City-Dashboard-DE/dags/**` 已包含對應 ETL，並在重建 DB 後執行該 DAG 或匯入該 DAG 產出的資料
- map config 指到的 GeoJSON 檔案存在於 `Taipei-City-Dashboard-FE/public/mapData`

## 建議整併方式

```bash
git checkout <target-branch>
git pull
git merge <source-branch>
```

遇到 SQL conflict 時，優先檢查這幾個表段落：

- `COPY public.component_charts`
- `COPY public.component_maps`
- `COPY public.components`
- `COPY public.dashboards`
- `COPY public.query_charts`
- `COPY public.dashboard_groups`

同名 dashboard 只應該保留一個 index。若只是同一個 sidebar tab 下多個 component，應該合併在同一筆 `dashboards.components` array 裡，例如 `{303,501}`，不要另外新增一筆同名 dashboard。

## 完整重建 DB

這段會刪除本機 Docker DB volume，包含 manager DB、dashboard data DB、Redis、pgAdmin、Qdrant。適合用在合併分支後要重新載入乾淨資料。

```bash
cd docker

docker compose \
  -f docker-compose-db.yaml \
  -f docker-compose-init.yaml \
  -f docker-compose.yaml \
  down --remove-orphans

docker volume rm \
  postgres_data \
  postgres_manager_data \
  redis_data \
  pgadmin_data \
  qdrant_data
```

如果 network 不存在，建立原始 network：

```bash
docker network inspect br_dashboard >/dev/null 2>&1 || \
  docker network create --driver=bridge --subnet=192.168.128.0/24 --gateway=192.168.128.1 br_dashboard
```

## 啟動資料庫服務

```bash
cd docker

docker compose -f docker-compose-db.yaml up -d \
  postgres-data \
  postgres-manager \
  redis \
  pgadmin \
  qdrant
```

等 Postgres ready：

```bash
docker exec postgres-manager sh -lc 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
docker exec postgres-data sh -lc 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

## 載入 sample data

manager DB 會載入 `MANAGER_SAMPLE_FILE`，預設是 `dashboardmanager-demo.sql`。

```bash
docker compose -f docker-compose-init.yaml run --rm dashboard-be-init-manager
```

dashboard data DB 會載入 `DASHBOARD_SAMPLE_FILE`，預設是 `dashboard-demo.sql`。`dashboard-demo.sql` 會再 include `food-safety-dashboard-data.sql`，用來初始化食安健康頁面 501/502 需要的 demo 資料表。

```bash
docker compose -f docker-compose-init.yaml run --rm dashboard-be-init-dashboard
```

注意：`food-safety-dashboard-data.sql` 目前納入以下 DE pipeline 產出的 demo 資料，刪除 volume 後不需要先跑 DAG 才能顯示 501/502：

- `public.fda_good_restaurants`：`Taipei-City-Dashboard-DE/dags/proj_city_dashboard/fda_good_restaurants`
- `public.cdc_infectious_disease`：`Taipei-City-Dashboard-DE/dags/proj_city_dashboard/cdc_infectious_disease`

若之後新增其他只存在於 DE pipeline、但沒有納入 sample dump 的 component，仍需要執行對應 DAG 或匯入該 DAG 產出的資料，否則 manager DB 雖然有 component/query 設定，BE 執行 chart SQL 時會因為 dashboard DB 缺少資料表而回 500。

FE 依賴若有變動，再跑一次：

```bash
docker compose -f docker-compose-init.yaml run --rm dashboard-fe-init
```

## 啟動 App

```bash
docker compose -f docker-compose.yaml up -d --build \
  nginx \
  dashboard-fe \
  dashboard-be
```

常用網址：

- FE dev server：`http://localhost:8080`
- BE direct API：`http://localhost:8088/api/v1`
- nginx：`http://localhost`
- pgAdmin：`http://localhost:8889`
- Qdrant：`http://localhost:6333`

## 可選：重建向量資料

如果合併的分支有新增或修改公開 component，並且需要 AI/vector search 找得到，重新跑 Qdrant upgrade：

```bash
docker compose -f docker-compose.yaml run --rm vector-db-upgrade
```

## 驗證

確認容器狀態：

```bash
docker ps -a
```

看 BE log：

```bash
docker logs dashboard-be --tail 100
```

確認 dashboard 有被載入：

```bash
docker exec postgres-manager psql -U postgres -d dashboardmanager -P pager=off -c \
  "SELECT id, index, name, components FROM public.dashboards ORDER BY id;"
```

確認 component config 和 query city：

```bash
docker exec postgres-manager psql -U postgres -d dashboardmanager -P pager=off -c \
  "SELECT c.id, c.index, c.name, q.city, q.query_type FROM public.components c LEFT JOIN public.query_charts q ON q.index = c.index ORDER BY c.id, q.city;"
```

測試某個 component chart API：

```bash
docker exec dashboard-be sh -lc \
  "wget -qO- 'http://127.0.0.1:8080/api/v1/component/<component-id>/chart?city=metrotaipei' | head -c 1000"
```

如果 API 回 500，先看 BE log。常見原因：

- `relation "...table..." does not exist`：`dashboard-demo.sql` 沒有建立該資料表，或 ETL 還沒跑
- `column "...column..." does not exist`：query SQL 欄位和資料表 schema 不一致
- component 在 manager DB 有設定，但 dashboard data DB 缺實際資料
- dashboard 裡用了同名但不同 index 的 sidebar tab，造成前端看起來重複

## 只重載設定，不清 DB

如果只是微調 manager config，且確定 SQL 不會和既有資料衝突，可以只重跑 manager init：

```bash
cd docker
docker compose -f docker-compose-init.yaml run --rm dashboard-be-init-manager
docker compose -f docker-compose.yaml restart dashboard-be
```

如果有改 chart 查詢會用到的資料表或 sample data，建議走完整重建 DB，避免舊表、舊欄位、舊 dashboard 混在一起。

## 分支整併檢查清單

- `docker/.env` 使用原始 service name：`postgres-data`、`postgres-manager`、`redis`、`qdrant`
- `dashboardmanager-demo.sql` 沒有同名 sidebar 重複 dashboard
- `dashboardmanager-demo.sql` 的 component id、map id 沒撞號
- `dashboard-demo.sql` 有 chart SQL 會查的資料表
- `public/mapData` 有 map config 需要的 GeoJSON
- 新 DAG 的 `job_config.json` table name 和 chart SQL table name 一致
- 重新載入後 `component/<id>/chart` 回 200
- 前端 console 沒有 500 或 `Cannot read properties of undefined`
