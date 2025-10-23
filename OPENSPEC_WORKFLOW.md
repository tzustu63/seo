# OpenSpec 工作流程說明

## 什麼是 OpenSpec？

OpenSpec 是一個**規格驅動開發**（Spec-Driven Development）的框架，幫助我們：
- 在開發前先規劃和設計功能
- 保持專案文檔與程式碼同步
- 追蹤功能變更和演進歷程
- 確保所有變更都有明確的需求和測試場景

## 三階段工作流程

### 📋 階段一：創建變更提案（Creating Changes）

**何時需要創建提案？**
- 新增功能或能力
- 進行重大變更（API、架構）
- 效能優化（改變行為）
- 安全性更新

**不需要提案的情況：**
- Bug 修復（恢復原有行為）
- 錯字、格式、註解修改
- 非破壞性的依賴更新
- 配置變更

**工作流程：**

1. **檢查現有工作**
   ```bash
   openspec list           # 查看進行中的變更
   openspec list --specs   # 查看現有的能力規格
   ```

2. **選擇變更 ID**
   - 使用 kebab-case
   - 動詞開頭：`add-`、`update-`、`remove-`、`refactor-`
   - 範例：`add-seo-analyzer-web-app`

3. **建立變更目錄**
   ```bash
   mkdir -p openspec/changes/[change-id]/specs/[capability]
   ```

4. **創建必要文件**
   - `proposal.md` - 說明為什麼和要改什麼
   - `tasks.md` - 實作任務清單
   - `design.md` - 技術決策（如果需要）
   - `specs/[capability]/spec.md` - 規格變更

5. **驗證提案**
   ```bash
   openspec validate [change-id] --strict
   ```

### 🔨 階段二：實作變更（Implementing Changes）

**實作流程：**

1. **閱讀 proposal.md** - 理解要建立什麼
2. **閱讀 design.md** - 了解技術決策（如果存在）
3. **閱讀 tasks.md** - 取得實作清單
4. **依序完成任務** - 按順序執行
5. **更新檢查清單** - 完成後將任務標記為 `- [x]`
6. **等待審查** - 實作前需要提案審查通過

**重要提醒：**
- 不要在提案未審查前開始實作
- 依序完成 tasks.md 中的任務
- 確保所有任務完成後再標記為完成

### 📦 階段三：歸檔變更（Archiving Changes）

變更部署後：

```bash
# 歸檔變更
openspec archive [change-id] --yes

# 這會自動：
# 1. 移動 changes/[name]/ 到 changes/archive/YYYY-MM-DD-[name]/
# 2. 更新 specs/ 目錄中的規格
# 3. 執行驗證確保一切正確
```

## 目錄結構

```
openspec/
├── project.md              # 專案慣例和技術棧
├── AGENTS.md              # AI 助手指引
├── specs/                 # 當前真相 - 已建立的功能
│   └── [capability]/      # 單一聚焦能力
│       ├── spec.md        # 需求和場景
│       └── design.md      # 技術模式（可選）
├── changes/               # 提案 - 應該變更的內容
│   ├── [change-name]/
│   │   ├── proposal.md    # 為什麼、什麼、影響
│   │   ├── tasks.md       # 實作清單
│   │   ├── design.md      # 技術決策（可選）
│   │   └── specs/         # 變更內容
│   │       └── [capability]/
│   │           └── spec.md # ADDED/MODIFIED/REMOVED
│   └── archive/           # 已完成的變更
```

## 提案結構

### proposal.md
```markdown
## Why
[1-2 句說明問題或機會]

## What Changes
- [變更項目列表]
- [標記破壞性變更為 **BREAKING**]

## Impact
- 受影響的規格: [列出能力]
- 受影響的程式碼: [關鍵檔案/系統]
```

### tasks.md
```markdown
## 1. 實作

- [ ] 1.1 創建核心類別
- [ ] 1.2 實作功能 A
- [ ] 1.3 實作功能 B
- [ ] 1.4 撰寫測試
```

### spec.md（變更）
```markdown
## ADDED Requirements

### Requirement: 新功能

系統應該提供...

#### Scenario: 成功案例

- **WHEN** 使用者執行動作
- **THEN** 預期結果

## MODIFIED Requirements

### Requirement: 現有功能

[完整修改後的需求]

## REMOVED Requirements

### Requirement: 舊功能

**原因**: [為什麼移除]
**遷移**: [如何處理]
```

## 常用命令

```bash
# 查看狀態
openspec list                    # 列出進行中的變更
openspec list --specs            # 列出規格
openspec show [item]             # 顯示變更或規格詳情

# 驗證
openspec validate [item]         # 驗證變更或規格
openspec validate --strict       # 完整驗證

# 歸檔
openspec archive <change-id> --yes  # 歸檔已完成的變更

# 專案管理
openspec init [path]             # 初始化 OpenSpec
openspec update [path]           # 更新指引檔案
```

## 最佳實踐

### ✅ 做這些

- **簡單優先** - 預設少於 100 行新程式碼
- **單一責任** - 每個能力只做一件事
- **明確參考** - 使用 `file.py:42` 格式
- **動詞開頭** - 能力命名使用動詞-名詞
- **場景必備** - 每個需求至少一個場景

### ❌ 避免這些

- **過度設計** - 沒有明確需求不要加複雜度
- **跳過驗證** - 每次都要執行 `--strict` 驗證
- **提前實作** - 提案未審查前不要開始寫程式
- **忘記歸檔** - 部署後要歸檔變更

## 場景格式要求

**正確** ✅
```markdown
#### Scenario: 使用者登入成功

- **WHEN** 提供有效憑證
- **THEN** 回傳 JWT token
```

**錯誤** ❌
```markdown
- **Scenario: 使用者登入**     # 不要用項目符號
**Scenario**: 使用者登入        # 不要用粗體標籤
### Scenario: 使用者登入        # 不要用三個井號
```

## 與 AI 協作

在這個專案中，您可以：

1. **請求創建提案**
   - "請幫我創建一個變更提案"
   - "我想新增 XXX 功能，請幫我規劃"

2. **請求實作**
   - "請實作 tasks.md 中的任務"
   - "請依照提案開始實作"

3. **請求審查**
   - "請檢查我的提案"
   - "請驗證規格是否正確"

4. **請求歸檔**
   - "請歸檔這個變更"
   - "功能已完成，請進行歸檔"

## 專案特定指引

### Google 搜尋自動化
- 重視 SEO 優化效果
- 強調真人行為模擬
- 注重錯誤恢復能力
- 優化長時間執行任務

### SEO 分析工具
- 遵循 Google SEO 指南
- 提供可操作的建議
- 支援多種分析面向
- 重視使用者體驗

## 範例：完整流程

```bash
# 1. 查看現有狀態
openspec list
openspec list --specs

# 2. 創建變更
mkdir -p openspec/changes/add-seo-analyzer-web-app/specs/seo-analyzer

# 3. 編寫文件
# - proposal.md
# - tasks.md
# - design.md (如需要)
# - specs/seo-analyzer/spec.md

# 4. 驗證
openspec validate add-seo-analyzer-web-app --strict

# 5. 開始實作（提案審查後）
# 依照 tasks.md 逐項完成

# 6. 歸檔（部署後）
openspec archive add-seo-analyzer-web-app --yes
```

## 疑難排解

### 常見錯誤

**"Change must have at least one delta"**
- 檢查 `changes/[name]/specs/` 是否存在 .md 檔案
- 確認檔案包含操作前綴（`## ADDED Requirements`）

**"Requirement must have at least one scenario"**
- 檢查場景使用 `#### Scenario:` 格式（4 個井號）
- 不要使用項目符號或粗體

**驗證失敗**
```bash
# 使用嚴格模式查看詳細資訊
openspec validate [change] --strict

# 檢查 JSON 輸出
openspec show [change] --json --deltas-only
```

## 總結

OpenSpec 幫助我們：
- 📝 在寫程式前先思考和設計
- 🔍 保持文檔與程式碼同步
- 📊 追蹤所有變更歷程
- ✅ 確保每個功能都有明確需求

記住：**規格是真相，變更是提案，保持它們同步！**

