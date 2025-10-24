# Google Search Automation（衝流量用的）

一個模組化的 Google 搜尋自動化系統，專為 SEO 優化設計，支援自動搜尋關鍵字並點擊目標網址。

## 功能特色

- 🔍 **自動化 Google 搜尋**：支援多關鍵字搜尋和智能點擊
- ⚙️ **靈活配置管理**：YAML 配置檔案，支援多種搜尋策略
- 🧠 **智能等待機制**：動態調整等待時間，模擬人類行為
- 📊 **搜尋結果分析**：詳細的統計分析和效能監控
- 🛡️ **錯誤處理**：完善的錯誤處理和重試機制
- 📝 **日誌記錄**：詳細的日誌記錄和統計報告

## 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 配置設定

編輯 `config.yaml` 檔案，設定您的搜尋關鍵字和目標網址：

```yaml
keywords:
  single_keywords:
    - keyword: "太陽能鋼構"
      enabled: true
      priority: 1

target_urls:
  - url: "https://www.yksc.com.tw/"
    enabled: true
    priority: 1
```

### 3. 執行自動化

```bash
python main.py
```

## 專案結構

```
google_automation/
├── core/                    # 核心功能模組
│   ├── google_automation.py # 主要自動化類別
│   ├── keyword_manager.py   # 關鍵字管理
│   ├── url_manager.py       # 網址管理
│   ├── search_analyzer.py   # 搜尋結果分析
│   └── wait_manager.py      # 智能等待機制
├── utils/                   # 工具模組
│   ├── config_loader.py     # 配置載入器
│   └── logger_setup.py      # 日誌設定
└── logs/                    # 日誌檔案目錄

config.yaml                  # 配置檔案
main.py                      # 主執行腳本
requirements.txt             # 依賴套件
```

## 配置說明

### 基本設定

```yaml
general:
  max_pages: 10 # 最大搜尋頁數
  wait_timeout: 10 # 等待超時時間（秒）
  min_delay: 2 # 最小延遲時間（秒）
  max_delay: 5 # 最大延遲時間（秒）
  page_delay: # 頁面停留時間
    min: 20
    max: 30
```

### 關鍵字設定

```yaml
keywords:
  single_keywords: # 單一關鍵字
    - keyword: "太陽能鋼構"
      enabled: true
      priority: 1
      max_pages: 10
  combinations: # 關鍵字組合
    - keyword: "太陽能鋼構 永康鋼構"
      enabled: true
      priority: 1
```

### 目標網址設定

```yaml
target_urls:
  - url: "https://www.yksc.com.tw/"
    enabled: true
    priority: 1
    match_type: "contains" # contains, exact, domain, regex
    keywords: ["太陽能", "鋼構"]
```

## 使用範例

### 基本使用

```python
from google_automation import GoogleSearchAutomation
from google_automation.utils import ConfigLoader

# 載入配置
config_loader = ConfigLoader("config.yaml")
config = config_loader.load_config()

# 初始化自動化系統
automation = GoogleSearchAutomation(config)

# 執行搜尋任務
results = automation.run_automation_cycle()

# 查看結果
for result in results:
    print(f"{result['keyword']} -> {result['target_url']}: {'成功' if result['success'] else '失敗'}")
```

### 進階使用

```python
# 單一搜尋任務
result = automation.execute_search_task("太陽能鋼構", "https://www.yksc.com.tw/")

# 獲取統計資料
stats = automation.get_search_statistics()
print(f"成功率: {stats['session']['overall_success_rate']:.2%}")

# 關鍵字管理
keyword_manager = automation.keyword_manager
keyword_manager.add_keyword("新關鍵字", priority=2)
keyword_manager.disable_keyword("舊關鍵字")
```

## 日誌和監控

系統會自動生成詳細的日誌檔案：

- `logs/automation.log` - 主要執行日誌
- `logs/statistics.json` - 統計資料
- `logs/errors.log` - 錯誤日誌

### 日誌等級

- `DEBUG` - 詳細的除錯資訊
- `INFO` - 一般執行資訊
- `WARNING` - 警告訊息
- `ERROR` - 錯誤訊息
- `CRITICAL` - 嚴重錯誤

## 效能優化

### 記憶體管理

```yaml
performance:
  memory_management:
    clear_cache_interval: 100 # 每100次搜尋清理快取
    max_memory_usage: 512 # 最大記憶體使用量（MB）
```

### 人性化行為

```yaml
search_strategy:
  human_like_behavior:
    enabled: true
    typing_delay_range: [0.05, 0.15] # 打字延遲範圍
    mouse_movement: true
    random_scrolling: true
```

## 錯誤處理

系統提供完善的錯誤處理機制：

- 自動重試機制
- 指數退避策略
- 詳細錯誤日誌
- 優雅降級處理

## 安全考量

- 隨機延遲模擬人類行為
- 請求間隔控制
- 每日搜尋限制
- 資源使用監控

## 開發和測試

### 執行測試

```bash
pytest tests/
```

### 程式碼格式化

```bash
black google_automation/
flake8 google_automation/
```

## 授權

本專案採用 MIT 授權條款。

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 更新日誌

### v1.0.0

- 初始版本發布
- 基本搜尋自動化功能
- 配置管理和日誌系統
- 搜尋結果分析
