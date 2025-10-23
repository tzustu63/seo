# SEO Analyzer Web Application - Design Document

## Context

需要建立一個網頁應用程式，允許使用者輸入網址並獲得全面的 SEO 分析報告。這是一個新的能力，與現有的 Google 搜尋自動化功能相輔相成，共同構成完整的 SEO 工具套件。

## Goals / Non-Goals

### Goals
- 提供多面向的 SEO 分析（HTML、Meta、關鍵字、圖片、效能等）
- 產生具體、可操作的優化建議
- 創建使用者友善的網頁介面
- 支援即時分析任意網址
- 提供評分系統讓使用者了解 SEO 健康度

### Non-Goals
- 不提供即時監控功能（首版）
- 不支援批量網址分析（首版）
- 不整合第三方 SEO 工具 API（首版）
- 不提供付費進階功能（首版）

## Decisions

### 1. 架構選擇

**決定**: 採用前後端分離架構

- **後端**: FastAPI（選擇原因：高效能、自動 API 文檔、非同步支援）
- **前端**: React（選擇原因：生態系完整、元件化、易於維護）
- **通訊**: RESTful API

**替代方案**:
- Flask + Jinja2 模板（傳統 MVC）：拒絕原因 - 不夠現代化，擴展性較差
- Django：拒絕原因 - 過於笨重，不適合此專案規模

### 2. 分析器架構

**決定**: 採用插件式分析器架構

```python
class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, url: str, html: str) -> AnalysisResult:
        pass

class HTMLAnalyzer(BaseAnalyzer):
    def analyze(self, url: str, html: str) -> AnalysisResult:
        # HTML 結構分析
        pass

class MetaAnalyzer(BaseAnalyzer):
    def analyze(self, url: str, html: str) -> AnalysisResult:
        # Meta 標籤分析
        pass
```

**優點**:
- 易於擴展新的分析器
- 職責分離，便於測試
- 可獨立執行或組合執行

### 3. 評分系統

**決定**: 採用加權評分制（0-100 分）

```python
weights = {
    'html_structure': 0.20,    # HTML 結構 20%
    'meta_tags': 0.15,         # Meta 標籤 15%
    'keywords': 0.15,          # 關鍵字 15%
    'images': 0.10,            # 圖片優化 10%
    'performance': 0.15,       # 效能 15%
    'mobile_friendly': 0.10,   # 行動裝置 10%
    'sitemap': 0.08,           # Sitemap 8%
    'robots': 0.07,            # Robots.txt 7%
}
```

### 4. 資料流程

```
使用者輸入網址
    ↓
前端驗證 URL
    ↓
發送 POST /api/analyze
    ↓
後端抓取網頁內容
    ↓
執行各類分析器
    ↓
產生建議和評分
    ↓
回傳 JSON 結果
    ↓
前端顯示報告
```

### 5. 技術棧細節

**後端依賴**:
```
fastapi==0.104.0
uvicorn==0.24.0
beautifulsoup4==4.12.2
lxml==4.9.3
requests==2.31.0
pillow==10.1.0
pydantic==2.4.2
```

**前端依賴**:
```
react==18.2.0
axios==1.5.0
tailwindcss==3.3.0  # 或 Material-UI
react-router-dom==6.16.0
```

## Risks / Trade-offs

### 風險 1: 網頁抓取失敗
- **風險**: 目標網站可能阻擋爬蟲、需要 JS 渲染、或載入緩慢
- **緩解**: 
  - 設定合理的超時時間（10 秒）
  - 提供友善的錯誤訊息
  - 支援重試機制
  - 未來可考慮整合 Selenium 用於 JS 渲染網頁

### 風險 2: 分析準確度
- **風險**: SEO 規則複雜且持續演變
- **緩解**:
  - 基於 Google 官方 SEO 指南
  - 定期更新規則
  - 提供建議的優先級和信心度

### 風險 3: 效能問題
- **風險**: 大型網頁分析耗時
- **緩解**:
  - 使用非同步處理
  - 限制下載大小（最多 5MB）
  - 實作快取機制（未來）

### Trade-offs

1. **即時分析 vs 批量分析**: 首版選擇即時分析，更簡單但限制使用場景
2. **完整分析 vs 快速分析**: 選擇完整分析，更有價值但耗時較長
3. **美觀 vs 資訊密度**: 平衡兩者，關鍵資訊優先顯示

## Migration Plan

### Phase 1: MVP（最小可行產品）
- 基本的 7 種分析器
- 簡單的網頁介面
- JSON API 回傳

### Phase 2: 增強功能
- 報告匯出（PDF）
- 歷史記錄
- 批量分析

### Phase 3: 進階功能
- 競爭對手分析
- 即時監控
- SEO 改善追蹤

### 回滾計畫
- 新功能獨立於現有的 Google 搜尋自動化
- 可獨立部署或停用
- 不影響現有功能

## Open Questions

1. **是否需要使用者登入系統？**
   - 初期：不需要，允許匿名使用
   - 未來：可考慮加入以支援歷史記錄

2. **是否要限制使用頻率？**
   - 建議：每個 IP 每分鐘最多 5 次請求
   - 避免濫用和伺服器負載過高

3. **報告是否要即時產生 PDF？**
   - 建議：首版僅提供網頁顯示
   - 未來版本加入 PDF 匯出

4. **是否要整合現有的 Google 搜尋自動化數據？**
   - 建議：暫時不整合
   - 未來可以結合搜尋排名追蹤

