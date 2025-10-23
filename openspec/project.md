# Project Context

## Purpose

這是一個綜合性的 SEO 優化工具套件，提供兩大核心功能：

### 1. Google 搜尋自動化
- **自動化搜尋**：使用 Selenium 自動執行 Google 搜尋
- **關鍵字管理**：支援多個搜尋關鍵字和目標網址的自動化搜尋
- **智能點擊**：自動點擊包含特定關鍵字的搜尋結果網頁
- **真人行為模擬**：透過隨機延遲、頁面滾動、逐字輸入等模擬真實使用者行為
- **排名提升**：透過自動化搜尋和點擊提升網站搜尋排名

### 2. SEO 網頁分析工具（規劃中）
- **網頁 SEO 診斷**：分析網頁的 SEO 問題並提供改善建議
- **多面向檢測**：檢查程式碼、關鍵字、排版、圖片、標題、meta、XML 等
- **優化建議**：針對發現的問題提供具體的修改建議
- **網頁輸入**：使用者可輸入任意網址進行分析

## Tech Stack

### 搜尋自動化
- **自動化工具**: Selenium WebDriver
- **程式語言**: Python 3.9+
- **瀏覽器**: Chrome WebDriver
- **配置管理**: YAML 配置檔案（PyYAML）
- **日誌系統**: Python logging 模組

### SEO 分析工具（規劃中）
- **後端框架**: Flask 或 FastAPI
- **前端框架**: React 或 Vue.js
- **HTML 解析**: BeautifulSoup4
- **SEO 分析**: 自訂分析引擎
- **圖片分析**: Pillow (PIL)
- **XML 解析**: lxml

### 共用工具
- **版本控制**: Git & GitHub
- **開發流程**: OpenSpec 規格驅動開發
- **依賴管理**: requirements.txt
- **測試框架**: pytest

## Project Conventions

### Code Style

- **Python**: 使用 PEP 8 標準，4 空格縮排
- **檔案命名**: 使用小寫字母和底線 (snake_case)
- **註解**: 中文註解，詳細說明複雜邏輯
- **函數命名**: 動詞開頭，清楚描述功能
- **類別命名**: 使用 PascalCase

### Architecture Patterns

- **模組化設計**: 按功能分離不同模組
- **策略模式**: 支援不同的搜尋策略
- **配置分離**: 使用 YAML 檔案管理配置
- **單一職責**: 每個類別和函數只負責一個功能

### Testing Strategy

- **單元測試**: 使用 pytest 測試個別函數和類別
- **整合測試**: 測試完整的搜尋和點擊流程
- **端到端測試**: 使用 Selenium 測試真實的 Google 搜尋場景

### Git Workflow

- **分支策略**: feature/功能名稱 分支
- **提交訊息**: 使用中文描述，格式：類型: 簡短描述
- **主要分支**: main 分支保護，需要 PR 審查

## Domain Context

### 搜尋引擎優化 (SEO)
- **搜尋排名**: 提升網站在 Google 搜尋結果中的排名
- **關鍵字策略**: 管理和優化搜尋關鍵字
- **點擊率優化**: 透過自動化增加目標網站的點擊率
- **競爭分析**: 了解關鍵字搜尋結果的競爭狀況

### 自動化技術
- **瀏覽器自動化**: 使用 Selenium 控制 Chrome 瀏覽器
- **反檢測機制**: 模擬真人行為避免被 Google 偵測為機器人
- **智能等待**: 動態調整等待時間以配合網頁載入
- **錯誤處理**: 處理網路問題和頁面載入失敗

### 網頁分析
- **SEO 最佳實踐**: 遵循 Google SEO 指南
- **技術 SEO**: 檢查網頁結構、meta 標籤、標題設定
- **內容 SEO**: 分析關鍵字密度、內容品質
- **效能 SEO**: 評估圖片大小、載入速度

## Important Constraints

- **法律合規**: 遵守 Google 使用條款和 robots.txt
- **速率限制**: 避免過於頻繁的請求導致 IP 被封鎖
- **隨機延遲**: 模擬人類行為，避免被偵測為機器人
- **資源使用**: 控制記憶體和 CPU 使用量
- **錯誤處理**: 妥善處理網路錯誤和頁面載入失敗

## External Dependencies

- **Google Search**: 主要搜尋目標平台
- **Selenium WebDriver**: 瀏覽器自動化框架
- **Chrome 瀏覽器**: 自動化執行環境
- **Python 標準庫**: logging, time, random, yaml 等
