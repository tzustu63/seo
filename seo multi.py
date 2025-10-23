# 導入必要模組
import time
import random
import string
import requests
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# ==========================================
# 進階設定區域
# ==========================================

# 搜尋關鍵字清單 - 可自由增加或刪除關鍵字
search_keywords = [
    "花蓮鐵工",
    "花蓮 專業鐵工",
    "花蓮鐵工廠",
    "花蓮鋼構",
    "花蓮 採光罩",
    "花蓮 太陽能鋼構"
]

# 目標網站資訊 - 簡化為只檢查域名關鍵字
target_domain_keyword = "yksc"  # 只要網址中包含這個關鍵字就點擊

# 執行設定
total_runs = 20 # 測試用，降低執行次數
min_stay_time = 8  # 最少停留時間
max_stay_time = 18  # 最多停留時間

# 搜尋引擎設定 - 固定使用台灣版 Google
search_engine = "https://www.google.com.tw"

# 間隔時間設定
min_delay_between_runs = 3
max_delay_between_runs = 8

# 長時間休息設定
long_break_interval = 12  # 每12次搜尋休息一下
long_break_min = 15     # 最少15秒
long_break_max = 35    # 最多35秒

# 統計追蹤
stats = {
    'successful_searches': 0,
    'failed_searches': 0,
    'target_found': 0,
    'target_clicked': 0,
    'total_time': 0,
    'start_time': time.time(),
    'search_keywords_used': [],
    'keyword_stats': {},  # 記錄每個關鍵字的使用次數和成功率
    'pages_searched': [],  # 記錄搜尋了多少頁才找到
    'target_found_on_page': []  # 記錄在第幾頁找到目標
}

# 初始化關鍵字統計
for keyword in search_keywords:
    stats['keyword_stats'][keyword] = {
        'used_count': 0,
        'found_count': 0,
        'clicked_count': 0
    }

# ==========================================
# 優化的核心函數
# ==========================================

def get_enhanced_chrome_options():
    """增強版 Chrome 設定"""
    options = Options()
    
    # 基本設定
    # options.add_argument('--headless')  # 註解掉以避免被偵測為機器人
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    # 隨機視窗大小
    window_sizes = [
        '--window-size=1920,1080',
        '--window-size=1366,768',
        '--window-size=1440,900',
        '--window-size=1536,864',
        '--window-size=1280,720'
    ]
    options.add_argument(random.choice(window_sizes))
    
    # 反偵測設定
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-plugins')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # 預設 User Agent 列表
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    ]
    
    user_agent = random.choice(user_agents)
    options.add_argument(f'--user-agent={user_agent}')
    
    # 隨機語言設定
    languages = ['zh-TW,zh;q=0.9,en;q=0.8', 'zh-CN,zh;q=0.9,en;q=0.8']
    options.add_argument(f'--accept-language={random.choice(languages)}')
    
    return options, user_agent

def generate_search_query():
    """從關鍵字清單中隨機選擇一個關鍵字"""
    if not search_keywords:
        return "花蓮鐵工"  # 預設關鍵字
    
    # 隨機選擇關鍵字
    selected_keyword = random.choice(search_keywords)
    
    # 更新統計
    stats['keyword_stats'][selected_keyword]['used_count'] += 1
    
    return selected_keyword

def search_with_google(driver, query):
    """使用 Google 搜尋"""
    try:
        driver.get(search_engine)
        time.sleep(random.uniform(2, 4))
        
        # 找到搜尋框並輸入關鍵字
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        
        # 模擬真實打字
        search_box.clear()
        for char in query:
            search_box.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        
        time.sleep(random.uniform(0.5, 1.5))
        search_box.send_keys(Keys.RETURN)
        
        # 等待搜尋結果載入
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "search"))
        )
        
        return True
        
    except Exception as e:
        error_msg = str(e)[:100]  # 增加錯誤訊息長度
        print(f"   ❌ Google 搜尋失敗: {error_msg}")
        print(f"   🔍 錯誤類型: {type(e).__name__}")
        return False

def find_target_in_results(driver, max_pages=10):
    """在搜尋結果中尋找目標網站，支援多頁搜尋 - 修正版：只要包含yksc即可"""
    current_page = 1
    
    while current_page <= max_pages:
        try:
            print(f"   📄 檢查第 {current_page} 頁搜尋結果...")
            
            # 等待頁面完全載入
            time.sleep(random.uniform(2, 4))
            
            # 尋找所有連結
            links = driver.find_elements(By.TAG_NAME, "a")
            
            target_links = []
            for link in links:
                try:
                    href = link.get_attribute("href")
                    # 修正：只要網址中包含 "yksc" 就加入目標連結
                    if href and target_domain_keyword.lower() in href.lower():
                        target_links.append(link)
                        print(f"   🎯 找到目標連結: {href}")
                except Exception as link_error:
                    # 忽略個別連結的錯誤，繼續檢查其他連結
                    continue
            
            if target_links:
                print(f"   ✅ 在第 {current_page} 頁找到 {len(target_links)} 個包含 '{target_domain_keyword}' 的連結")
                return target_links, current_page
            else:
                print(f"   😞 第 {current_page} 頁未找到包含 '{target_domain_keyword}' 的連結")
                
                # 如果還沒到最後一頁，嘗試點擊下一頁
                if current_page < max_pages:
                    next_page_clicked = click_next_page(driver, current_page)
                    if next_page_clicked:
                        current_page += 1
                        # 等待新頁面載入
                        time.sleep(random.uniform(3, 5))
                    else:
                        print(f"   ⚠️  無法找到下一頁按鈕，停止搜尋")
                        break
                else:
                    print(f"   ⚠️  已搜尋到第 {max_pages} 頁，停止搜尋")
                    break
        
        except Exception as e:
            print(f"   ❌ 第 {current_page} 頁搜尋結果分析失敗: {str(e)[:50]}")
            break
    
    return [], current_page

def click_next_page(driver, current_page):
    """點擊下一頁按鈕"""
    try:
        # Google 搜尋結果的下一頁按鈕可能有多種選擇器
        next_page_selectors = [
            "a[aria-label='下一頁']",
            "a[aria-label='Next']", 
            "#pnnext",
            "a#pnnext",
            "span.SJajHc:last-child a",
            "a[href*='start=']"
        ]
        
        next_button = None
        
        # 嘗試不同的選擇器找到下一頁按鈕
        for selector in next_page_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    # 檢查元素是否可見且可點擊
                    if element.is_displayed() and element.is_enabled():
                        # 檢查文字內容或屬性
                        text = element.text.lower()
                        if any(keyword in text for keyword in ['next', '下一頁', '下一個', '>']):
                            next_button = element
                            break
                        # 或者檢查 href 是否包含 start 參數
                        href = element.get_attribute('href')
                        if href and 'start=' in href:
                            next_button = element
                            break
                
                if next_button:
                    break
            except:
                continue
        
        # 如果還沒找到，嘗試通過頁碼找下一頁
        if not next_button:
            try:
                next_page_num = current_page + 1
                page_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='start=']")
                for link in page_links:
                    if str(next_page_num) in link.text:
                        next_button = link
                        break
            except:
                pass
        
        if next_button:
            print(f"   ➡️  點擊前往第 {current_page + 1} 頁")
            
            # 滾動到按鈕位置
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            time.sleep(random.uniform(1, 2))
            
            # 點擊下一頁
            next_button.click()
            
            # 等待頁面載入
            time.sleep(random.uniform(2, 4))
            
            return True
        else:
            print(f"   ❌ 找不到下一頁按鈕")
            return False
            
    except Exception as e:
        print(f"   ❌ 點擊下一頁失敗: {str(e)[:50]}")
        return False

def click_target_link(driver, target_links):
    """點擊目標連結 - 改進版，處理點擊被攔截的問題"""
    for attempt in range(len(target_links)):
        try:
            # 隨機選擇一個目標連結
            selected_link = random.choice(target_links)
            
            # 獲取連結資訊
            link_text = selected_link.text[:50] if selected_link.text else "無文字"
            link_url = selected_link.get_attribute("href")
            
            print(f"   🖱️  嘗試點擊連結: {link_text}")
            print(f"   🔗 目標URL: {link_url}")
            
            # 方法1: 滾動到連結位置並直接點擊
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", selected_link)
            time.sleep(random.uniform(1, 2))
            
            try:
                # 嘗試常規點擊
                selected_link.click()
                print(f"   ✅ 常規點擊成功")
            except Exception as click_error:
                print(f"   ⚠️  常規點擊失敗，嘗試其他方法: {str(click_error)[:50]}")
                
                # 方法2: 使用 JavaScript 點擊
                try:
                    driver.execute_script("arguments[0].click();", selected_link)
                    print(f"   ✅ JavaScript 點擊成功")
                except Exception as js_error:
                    print(f"   ⚠️  JavaScript 點擊失敗: {str(js_error)[:50]}")
                    
                    # 方法3: 直接導航到 URL
                    try:
                        print(f"   🔄 直接導航到目標網址")
                        driver.get(link_url)
                        print(f"   ✅ 直接導航成功")
                    except Exception as nav_error:
                        print(f"   ❌ 直接導航失敗: {str(nav_error)[:50]}")
                        # 如果還有其他連結可以嘗試，繼續下一個
                        if attempt < len(target_links) - 1:
                            print(f"   🔄 嘗試下一個連結...")
                            target_links.remove(selected_link)  # 移除失敗的連結
                            continue
                        else:
                            return False, None
            
            # 等待頁面載入
            time.sleep(random.uniform(3, 5))
            
            # 驗證是否成功進入目標網站
            current_url = driver.current_url
            if target_domain_keyword.lower() in current_url.lower():
                print(f"   ✅ 成功進入包含 '{target_domain_keyword}' 的網站: {current_url}")
                return True, current_url
            else:
                print(f"   ⚠️  未成功進入目標網站，當前: {current_url}")
                # 如果還有其他連結可以嘗試，繼續下一個
                if attempt < len(target_links) - 1:
                    print(f"   🔄 嘗試下一個連結...")
                    target_links.remove(selected_link)  # 移除失敗的連結
                    continue
                else:
                    return False, current_url
                    
        except Exception as e:
            print(f"   ❌ 點擊連結過程發生錯誤: {str(e)[:50]}")
            # 如果還有其他連結可以嘗試，繼續下一個
            if attempt < len(target_links) - 1:
                print(f"   🔄 嘗試下一個連結...")
                try:
                    target_links.remove(selected_link)  # 移除失敗的連結
                except:
                    pass
                continue
            else:
                return False, None
    
    # 如果所有連結都嘗試失敗了
    print(f"   ❌ 所有目標連結都無法點擊")
    return False, None

def enhanced_browse_behavior(driver):
    """在目標網站上的瀏覽行為"""
    behaviors_performed = []
    
    try:
        # 初始停頓
        initial_pause = random.uniform(2, 4)
        time.sleep(initial_pause)
        behaviors_performed.append(f"初始觀察 {initial_pause:.1f}s")
        
        # 滾動瀏覽
        scroll_times = random.randint(3, 6)
        for i in range(scroll_times):
            scroll_amount = random.randint(300, 600)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            pause_time = random.uniform(2, 4)
            time.sleep(pause_time)
            behaviors_performed.append(f"滾動瀏覽 #{i+1}")
        
        # 隨機停頓閱讀
        reading_pauses = random.randint(2, 4)
        for i in range(reading_pauses):
            pause_duration = random.uniform(3, 6)
            time.sleep(pause_duration)
            behaviors_performed.append(f"深度閱讀 #{i+1}")
        
        # 偶爾向上滾動
        if random.random() < 0.4:
            scroll_up = random.randint(200, 500)
            driver.execute_script(f"window.scrollBy(0, -{scroll_up});")
            time.sleep(random.uniform(2, 3))
            behaviors_performed.append("重新檢視內容")
        
        # 模擬檢視其他元素
        if random.random() < 0.3:
            try:
                elements = driver.find_elements(By.TAG_NAME, "a")[:5]
                if elements:
                    target_element = random.choice(elements)
                    driver.execute_script("arguments[0].scrollIntoView();", target_element)
                    time.sleep(random.uniform(1, 2))
                    behaviors_performed.append("檢視相關連結")
            except:
                pass
        
        return behaviors_performed
        
    except Exception as e:
        behaviors_performed.append(f"瀏覽行為錯誤: {str(e)[:50]}")
        return behaviors_performed

def perform_search_and_click(search_engine_url, query):
    """執行完整的搜尋和點擊流程"""
    driver = None
    success = False
    target_found = False
    target_clicked = False
    behaviors = []
    user_agent = ""
    final_url = ""
    found_on_page = 0
    
    try:
        # 設定瀏覽器
        options, user_agent = get_enhanced_chrome_options()
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # 隱藏自動化特徵
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # 執行搜尋
        print(f"   🔍 開始搜尋: {query}")
        
        search_success = search_with_google(driver, query)
        
        if not search_success:
            raise Exception("搜尋執行失敗")
        
        print("   ✅ 搜尋完成")
        success = True
        
        # 在搜尋結果中尋找目標（支援多頁搜尋）
        target_links, found_on_page = find_target_in_results(driver, max_pages=10)
        
        if target_links:
            target_found = True
            print(f"   🎯 在第 {found_on_page} 頁找到包含 '{target_domain_keyword}' 的網站")
            
            # 更新關鍵字統計
            stats['keyword_stats'][query]['found_count'] += 1
            
            # 點擊目標連結
            click_success, final_url = click_target_link(driver, target_links)
            
            if click_success:
                target_clicked = True
                
                # 更新關鍵字統計
                stats['keyword_stats'][query]['clicked_count'] += 1
                
                # 在目標網站上執行瀏覽行為
                stay_time = random.randint(min_stay_time, max_stay_time)
                print(f"   🤖 開始網站瀏覽 (預計 {stay_time} 秒)")
                
                start_time = time.time()
                behaviors = enhanced_browse_behavior(driver)
                
                # 確保達到最小停留時間
                actual_time = time.time() - start_time
                if actual_time < stay_time:
                    remaining_time = stay_time - actual_time
                    time.sleep(remaining_time)
                
                actual_total_time = time.time() - start_time
                print(f"   ✅ 瀏覽完成，實際停留 {actual_total_time:.1f} 秒")
        
    except Exception as e:
        print(f"   ❌ 執行過程發生錯誤: {str(e)}")
        
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
    
    return {
        'success': success,
        'target_found': target_found,
        'target_clicked': target_clicked,
        'user_agent': user_agent,
        'behaviors': behaviors,
        'final_url': final_url,
        'query': query,
        'found_on_page': found_on_page
    }

def log_search_info(run_number, search_engine, result):
    """記錄搜尋信息"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n📝 [{timestamp}] 搜尋記錄 #{run_number}")
    print(f"   🔍 搜尋引擎: {search_engine}")
    print(f"   🔑 關鍵字: {result['query']}")
    print(f"   🤖 UA: {result['user_agent'][:60]}...")
    
    if result['success']:
        print(f"   ✅ 搜尋: 成功")
        stats['successful_searches'] += 1
    else:
        print(f"   ❌ 搜尋: 失敗")
        stats['failed_searches'] += 1
    
    if result['target_found']:
        print(f"   🎯 目標發現: 是 (第 {result['found_on_page']} 頁)")
        stats['target_found'] += 1
        stats['target_found_on_page'].append(result['found_on_page'])
    else:
        print(f"   😞 目標發現: 否")
    
    stats['pages_searched'].append(result['found_on_page'] if result['target_found'] else 10)
    
    if result['target_clicked']:
        print(f"   🖱️  目標點擊: 是")
        print(f"   🌐 最終頁面: {result['final_url']}")
        stats['target_clicked'] += 1
    else:
        print(f"   🖱️  目標點擊: 否")
    
    print(f"   📋 行為數量: {len(result['behaviors'])}")

def print_statistics():
    """顯示統計信息"""
    current_time = time.time()
    elapsed_time = current_time - stats['start_time']
    
    print("\n📊 執行統計:")
    print(f"   ⏱️  總執行時間: {elapsed_time/60:.1f} 分鐘")
    print(f"   🔍 成功搜尋: {stats['successful_searches']}")
    print(f"   ❌ 失敗搜尋: {stats['failed_searches']}")
    print(f"   🎯 發現目標: {stats['target_found']}")
    print(f"   🖱️  點擊目標: {stats['target_clicked']}")
    
    if stats['successful_searches'] > 0:
        find_rate = (stats['target_found'] / stats['successful_searches']) * 100
        print(f"   📈 目標發現率: {find_rate:.1f}%")
    
    if stats['target_found'] > 0:
        click_rate = (stats['target_clicked'] / stats['target_found']) * 100
        print(f"   📈 點擊成功率: {click_rate:.1f}%")
        
        # 顯示目標發現頁數統計
        if stats['target_found_on_page']:
            avg_page = sum(stats['target_found_on_page']) / len(stats['target_found_on_page'])
            print(f"   📊 平均在第 {avg_page:.1f} 頁找到目標")
            
            page_distribution = {}
            for page in stats['target_found_on_page']:
                page_distribution[page] = page_distribution.get(page, 0) + 1
            
            print(f"   📋 目標發現頁數分布:")
            for page in sorted(page_distribution.keys()):
                count = page_distribution[page]
                print(f"      第 {page} 頁: {count} 次")

def print_keyword_statistics():
    """顯示關鍵字使用統計"""
    print("\n🔑 關鍵字詳細統計:")
    print("   " + "="*70)
    print(f"   {'關鍵字':<15} {'使用次數':<8} {'發現次數':<8} {'點擊次數':<8} {'發現率':<8} {'點擊率'}")
    print("   " + "-"*70)
    
    for keyword in search_keywords:
        used = stats['keyword_stats'][keyword]['used_count']
        found = stats['keyword_stats'][keyword]['found_count']
        clicked = stats['keyword_stats'][keyword]['clicked_count']
        
        find_rate = f"{(found/used*100):.1f}%" if used > 0 else "0.0%"
        click_rate = f"{(clicked/found*100):.1f}%" if found > 0 else "0.0%"
        
        print(f"   {keyword:<15} {used:<8} {found:<8} {clicked:<8} {find_rate:<8} {click_rate}")

# ==========================================
# 主程式執行
# ==========================================

print("🚀 開始執行 Google 搜尋點擊機器人 (修正版)")
print("=" * 60)

# 顯示設定資訊
print(f"🎯 計劃執行 {total_runs} 次搜尋")
print(f"🔑 可用關鍵字 ({len(search_keywords)} 個):")
for i, keyword in enumerate(search_keywords, 1):
    print(f"    {i}. {keyword}")

print(f"\n🌐 目標網址關鍵字: '{target_domain_keyword}' (只要網址包含此關鍵字就會點擊)")
print(f"🎲 每次隨機從關鍵字清單中選擇")

# 主要執行迴圈
for i in range(total_runs):
    print(f"\n{'='*20} 🎯 第 {i + 1} / {total_runs} 次搜尋 {'='*20}")
    
    # 檢查是否需要長時間休息
    if i > 0 and i % long_break_interval == 0:
        long_break_time = random.randint(long_break_min, long_break_max)
        print(f"🛌 達到 {long_break_interval} 次搜尋，休息 {long_break_time} 秒")
        
        print_statistics()
        print_keyword_statistics()
        
        time.sleep(long_break_time)
        print("🌟 休息結束，繼續執行")
    
    # 顯示搜尋引擎
    print(f"🔍 搜尋引擎: {search_engine}")
    
    # 生成搜尋關鍵字（隨機選擇）
    search_query = generate_search_query()
    
    # 記錄使用的關鍵字
    stats['search_keywords_used'].append(search_query)
    
    # 執行搜尋和點擊
    search_start_time = time.time()
    result = perform_search_and_click(search_engine, search_query)
    search_total_time = time.time() - search_start_time
    
    stats['total_time'] += search_total_time
    
    # 記錄結果
    log_search_info(i+1, search_engine, result)
    
    # 等待間隔
    if i < total_runs - 1:
        delay_time = random.randint(min_delay_between_runs, max_delay_between_runs)
        print(f"⏳ 等待 {delay_time} 秒後繼續...")
        time.sleep(delay_time)

print("\n🎉 所有搜尋任務執行完畢！")
print("=" * 60)

# 顯示最終統計
print_statistics()

# 顯示關鍵字詳細統計
print_keyword_statistics()

# 顯示關鍵字使用次數排行
keyword_counts = {}
for keyword in stats['search_keywords_used']:
    keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1

print(f"\n🏆 關鍵字使用排行:")
sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
for i, (keyword, count) in enumerate(sorted_keywords, 1):
    percentage = (count / len(stats['search_keywords_used'])) * 100
    print(f"   {i}. {keyword}: {count} 次 ({percentage:.1f}%)")

# 顯示最佳表現關鍵字
print(f"\n🌟 最佳表現關鍵字:")
best_find_rate = 0
best_find_keyword = ""
best_click_rate = 0
best_click_keyword = ""

for keyword in search_keywords:
    used = stats['keyword_stats'][keyword]['used_count']
    found = stats['keyword_stats'][keyword]['found_count']
    clicked = stats['keyword_stats'][keyword]['clicked_count']
    
    if used > 0:
        find_rate = (found / used) * 100
        if find_rate > best_find_rate:
            best_find_rate = find_rate
            best_find_keyword = keyword
    
    if found > 0:
        click_rate = (clicked / found) * 100
        if click_rate > best_click_rate:
            best_click_rate = click_rate
            best_click_keyword = keyword

if best_find_keyword:
    print(f"   🎯 最高發現率: {best_find_keyword} ({best_find_rate:.1f}%)")
if best_click_keyword:
    print(f"   🖱️  最高點擊率: {best_click_keyword} ({best_click_rate:.1f}%)")

print(f"\n🏁 程式結束")
print(f"📅 結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 建議改進
print(f"\n💡 改進建議:")
if stats['target_found'] < stats['successful_searches'] * 0.5:
    print("   - 考慮調整關鍵字或增加更多相關關鍵字")
if stats['target_clicked'] < stats['target_found'] * 0.8:
    print("   - 檢查目標網站連結是否正確")

print(f"\n📋 如要新增關鍵字，請修改程式開頭的 search_keywords 清單")
print(f"🎯 目標檢測：只要網址包含 '{target_domain_keyword}' 就會點擊進入")