# Project Context

## Purpose

這是一個專注於 Google 搜尋自動化的專案，主要功能：

- **Google 搜尋自動化**：使用 Selenium 自動執行 Google 搜尋
- **關鍵字搜尋**：支援多個搜尋關鍵字的自動化搜尋
- **智能點擊**：自動點擊包含特定關鍵字的搜尋結果網頁
- **SEO 優化**：透過自動化搜尋和點擊提升網站搜尋排名

## Tech Stack

- **自動化工具**: Selenium WebDriver
- **程式語言**: Python
- **瀏覽器**: Chrome WebDriver
- **配置管理**: YAML 配置檔案
- **日誌系統**: Python logging 模組
- **版本控制**: Git

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

- **SEO 優化**: 專注於 Google 搜尋排名提升
- **搜尋自動化**: 自動執行搜尋和點擊操作
- **關鍵字管理**: 管理多個搜尋關鍵字和目標網址
- **效能監控**: 追蹤搜尋成功率和執行統計

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
