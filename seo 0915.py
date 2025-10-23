# 導入必要模組 - 反檢測加強版
import time
import random
import requests
import platform
import os
import zipfile
import stat
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains

print("🔧 反檢測加強版 - 包含多項防護機制")

# ==========================================
# 進階設定區域
# ==========================================

# 搜尋關鍵字清單
search_keywords = [
    "花蓮鐵工",
    "花蓮 專業鐵工", 
    "花蓮鐵工廠",
    "花蓮鋼構",
    "花蓮 採光罩",
    "花蓮 太陽能鋼構"
]

# 目標網站關鍵字
target_domain_keyword = "yksc"

# 執行設定 - 降低頻率避免檢測
total_runs = 50  # 減少總執行次數
min_stay_time = 8
max_stay_time = 20

# 搜尋引擎設定
search_engine = "https://www.google.com.tw"

# 間隔時間設定 - 大幅增加
min_delay_between_runs = 30  # 增加到30秒
max_delay_between_runs = 90  # 增加到90秒

# 長時間休息設定
long_break_interval = 3  # 每3次就休息
long_break_min = 120  # 2分鐘
long_break_max = 300  # 5分鐘

# 每日執行限制
daily_search_limit = 20  # 每日最多執行20次
hourly_search_limit = 5   # 每小時最多執行5次

# 統計追蹤
stats = {
    'successful_searches': 0,
    'failed_searches': 0,
    'target_found': 0,
    'target_clicked': 0,
    'total_time': 0,
    'start_time': time.time(),
    'search_keywords_used': [],
    'keyword_stats': {},
    'error_types': {},
    'captcha_detected': 0,
    'hourly_searches': []
}

# 初始化關鍵字統計
for keyword in search_keywords:
    stats['keyword_stats'][keyword] = {
        'used_count': 0,
        'found_count': 0,
        'clicked_count': 0
    }

# ==========================================
# ChromeDriver 自動下載函數
# ==========================================

def get_chrome_version():
    """獲取 Chrome 版本"""
    try:
        if platform.system() == "Darwin":  # macOS
            import subprocess
            result = subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip().split()[-1]
                return version.split('.')[0]
        elif platform.system() == "Windows":
            import subprocess
            result = subprocess.run(['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v', 'version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.split()[-1]
                return version.split('.')[0]
        else:  # Linux
            import subprocess
            result = subprocess.run(['google-chrome', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip().split()[-1]
                return version.split('.')[0]
    except:
        pass
    
    return "131"

def download_chromedriver():
    """下載對應版本的 ChromeDriver"""
    chrome_version = get_chrome_version()
    print(f"   🌐 檢測到 Chrome 主版本: {chrome_version}")
    
    try:
        driver_dir = os.path.expanduser("~/chromedriver")
        os.makedirs(driver_dir, exist_ok=True)
        
        system = platform.system()
        if system == "Darwin":
            import subprocess
            result = subprocess.run(['uname', '-m'], capture_output=True, text=True)
            if 'arm64' in result.stdout:
                platform_name = "mac-arm64"
            else:
                platform_name = "mac-x64"
            driver_name = "chromedriver"
        elif system == "Windows":
            platform_name = "win64"
            driver_name = "chromedriver.exe"
        else:
            platform_name = "linux64"
            driver_name = "chromedriver"
        
        driver_path = os.path.join(driver_dir, driver_name)
        
        if os.path.exists(driver_path):
            print(f"   ✅ ChromeDriver 已存在: {driver_path}")
            return driver_path
        
        print(f"   📥 正在下載 ChromeDriver...")
        
        version_api = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
        response = requests.get(version_api, timeout=30)
        data = response.json()
        
        driver_url = None
        for channel_data in data['channels'].values():
            if 'chromedriver' in channel_data.get('downloads', {}):
                for download in channel_data['downloads']['chromedriver']:
                    if download['platform'] == platform_name:
                        driver_url = download['url']
                        break
                if driver_url:
                    break
        
        if not driver_url:
            driver_url = f"https://storage.googleapis.com/chrome-for-testing-public/{chrome_version}.0.6778.24/{platform_name}/chromedriver-{platform_name}.zip"
        
        print(f"   📥 下載URL: {driver_url}")
        response = requests.get(driver_url, timeout=60)
        response.raise_for_status()
        
        zip_path = os.path.join(driver_dir, "chromedriver.zip")
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(driver_dir)
        
        if system != "Windows":
            for root, dirs, files in os.walk(driver_dir):
                for file in files:
                    if file == driver_name:
                        file_path = os.path.join(root, file)
                        os.chmod(file_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
                        if file_path != driver_path:
                            os.rename(file_path, driver_path)
        
        os.remove(zip_path)
        
        if os.path.exists(driver_path):
            print(f"   ✅ ChromeDriver 下載成功: {driver_path}")
            return driver_path
        else:
            raise Exception("ChromeDriver 下載後找不到執行檔")
        
    except Exception as e:
        print(f"   ❌ ChromeDriver 下載失敗: {str(e)}")
        return None

# ==========================================
# 反檢測核心函數
# ==========================================

def get_stealth_chrome_options():
    """超級隱身模式 Chrome 設定"""
    options = Options()
    
    # 隨機選擇用戶資料夾（模擬真實用戶）
    user_data_dir = f"/tmp/chrome_profile_{random.randint(1000, 9999)}"
    options.add_argument(f'--user-data-dir={user_data_dir}')
    
    # 基本設定
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # 隨機視窗大小
    window_sizes = [
        (1920, 1080), (1366, 768), (1440, 900), 
        (1536, 864), (1600, 900), (1280, 720)
    ]
    width, height = random.choice(window_sizes)
    options.add_argument(f'--window-size={width},{height}')
    
    # 隨機視窗位置
    x_pos = random.randint(0, 200)
    y_pos = random.randint(0, 200)
    options.add_argument(f'--window-position={x_pos},{y_pos}')
    
    # 停用 WebRTC（防止 IP 洩露）
    options.add_argument('--disable-webrtc')
    
    # 隨機 User Agent
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]
    
    user_agent = random.choice(user_agents)
    options.add_argument(f'--user-agent={user_agent}')
    
    # 語言設定（台灣用戶）
    options.add_argument('--accept-language=zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7')
    
    # 額外的隱私設定
    prefs = {
        "profile.default_content_setting_values": {
            "notifications": 2,
            "media_stream": 2,
            "media_stream_mic": 2,
            "media_stream_camera": 2,
            "geolocation": 2,
            "site_engagement": 2,
            "media_router": 2
        },
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "webrtc.ip_handling_policy": "disable_non_proxied_udp",
        "webrtc.multiple_routes_enabled": False,
        "webrtc.nonproxied_udp_enabled": False
    }
    options.add_experimental_option("prefs", prefs)
    
    # 加入更多真實瀏覽器的參數
    options.add_argument('--enable-features=NetworkService,NetworkServiceInProcess')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--force-color-profile=srgb')
    
    return options, user_agent

def inject_stealth_js(driver):
    """注入進階反檢測 JavaScript"""
    stealth_js = """
    // 覆蓋 webdriver 屬性
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    
    // 覆蓋 plugins 屬性
    Object.defineProperty(navigator, 'plugins', {
        get: () => [
            {0: {type: "application/x-google-chrome-pdf", suffixes: "pdf"}},
            {0: {type: "application/pdf", suffixes: "pdf"}}
        ]
    });
    
    // 覆蓋 languages 屬性
    Object.defineProperty(navigator, 'languages', {
        get: () => ['zh-TW', 'zh', 'en-US', 'en']
    });
    
    // 覆蓋 permissions 查詢
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
            Promise.resolve({ state: Notification.permission }) :
            originalQuery(parameters)
    );
    
    // 覆蓋 Chrome 屬性
    window.chrome = {
        runtime: {},
        loadTimes: function() {},
        csi: function() {},
        app: {}
    };
    
    // 模擬真實的滑鼠移動
    document.addEventListener('mousemove', function() {});
    
    // 覆蓋 canvas 指紋
    const getImageData = CanvasRenderingContext2D.prototype.getImageData;
    CanvasRenderingContext2D.prototype.getImageData = function() {
        const imageData = getImageData.apply(this, arguments);
        for (let i = 0; i < imageData.data.length; i += 4) {
            imageData.data[i] = imageData.data[i] ^ 1;
        }
        return imageData;
    };
    """
    
    driver.execute_script(stealth_js)

def simulate_human_behavior(driver):
    """模擬人類行為"""
    actions = ActionChains(driver)
    
    # 隨機移動滑鼠
    for _ in range(random.randint(2, 5)):
        x = random.randint(100, 800)
        y = random.randint(100, 600)
        actions.move_by_offset(x, y)
        actions.pause(random.uniform(0.1, 0.3))
    
    try:
        actions.perform()
    except:
        pass
    
    # 隨機滾動
    scroll_times = random.randint(1, 3)
    for _ in range(scroll_times):
        scroll_amount = random.randint(100, 300)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(random.uniform(0.5, 1.5))

def check_for_captcha(driver):
    """檢查是否出現 CAPTCHA"""
    captcha_indicators = [
        'recaptcha',
        'captcha',
        '我不是機器人',
        'unusual traffic',
        '異常流量',
        '驗證'
    ]
    
    page_source = driver.page_source.lower()
    for indicator in captcha_indicators:
        if indicator in page_source:
            return True
    
    # 檢查 iframe 中的 reCAPTCHA
    try:
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        for iframe in iframes:
            src = iframe.get_attribute('src') or ''
            if 'recaptcha' in src.lower():
                return True
    except:
        pass
    
    return False

def wait_with_random_actions(driver, min_time, max_time):
    """等待期間執行隨機動作"""
    total_wait = random.uniform(min_time, max_time)
    elapsed = 0
    
    while elapsed < total_wait:
        action_wait = random.uniform(1, 3)
        time.sleep(action_wait)
        elapsed += action_wait
        
        # 隨機執行一些動作
        if random.random() > 0.5:
            simulate_human_behavior(driver)

def create_webdriver_with_retry(max_retries=3):
    """建立 WebDriver，包含重試機制"""
    for attempt in range(max_retries):
        try:
            print(f"   🚀 嘗試啟動瀏覽器 (第 {attempt + 1} 次)")
            
            options, user_agent = get_stealth_chrome_options()
            
            driver_path = download_chromedriver()
            if not driver_path:
                raise Exception("無法下載 ChromeDriver")
            
            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=options)
            
            # 設定超時時間
            driver.set_page_load_timeout(45)
            driver.implicitly_wait(15)
            
            # 注入反檢測 JavaScript
            driver.get("about:blank")
            inject_stealth_js(driver)
            
            # 先訪問一個無害的網頁建立 session
            driver.get("https://www.google.com.tw/imghp")  # Google 圖片首頁
            wait_with_random_actions(driver, 3, 5)
            
            # 再訪問主要搜尋頁面
            driver.get("https://www.google.com.tw")
            wait_with_random_actions(driver, 2, 4)
            
            # 檢查是否有 CAPTCHA
            if check_for_captcha(driver):
                print("   ⚠️  檢測到 CAPTCHA，等待較長時間後重試")
                driver.quit()
                if attempt < max_retries - 1:
                    time.sleep(random.randint(60, 120))
                continue
            
            print("   ✅ 瀏覽器啟動成功")
            return driver, user_agent
            
        except Exception as e:
            print(f"   ❌ 瀏覽器啟動失敗 (第 {attempt + 1} 次): {str(e)[:100]}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 10
                print(f"   ⏳ 等待 {wait_time} 秒後重試...")
                time.sleep(wait_time)
            else:
                print("   💥 瀏覽器啟動完全失敗")
                return None, ""

def search_with_google(driver, query):
    """人性化 Google 搜尋"""
    try:
        print(f"   🌐 準備搜尋...")
        
        # 檢查當前頁面
        current_url = driver.current_url
        if 'google.com' not in current_url:
            driver.get("https://www.google.com.tw")
            wait_with_random_actions(driver, 3, 5)
        
        # 檢查 CAPTCHA
        if check_for_captcha(driver):
            print("   ⚠️  檢測到 CAPTCHA")
            stats['captcha_detected'] += 1
            return False
        
        # 尋找搜尋框
        search_selectors = [
            "textarea[name='q']",
            "input[name='q']",
            "textarea[title='搜尋']",
            "input[title='搜尋']"
        ]
        
        search_box = None
        for selector in search_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        search_box = element
                        print(f"   ✅ 找到搜尋框")
                        break
                if search_box:
                    break
            except:
                continue
        
        if not search_box:
            print("   ❌ 找不到搜尋框")
            return False
        
        # 點擊搜尋框（模擬真人行為）
        driver.execute_script("arguments[0].scrollIntoView(true);", search_box)
        time.sleep(random.uniform(0.5, 1))
        search_box.click()
        time.sleep(random.uniform(0.5, 1))
        
        # 清空搜尋框
        search_box.clear()
        time.sleep(random.uniform(0.3, 0.7))
        
        # 模擬真實打字（包含錯誤和修正）
        typed_text = ""
        for i, char in enumerate(query):
            # 偶爾打錯字
            if random.random() < 0.05 and i > 0:  # 5% 機率打錯
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                search_box.send_keys(wrong_char)
                typed_text += wrong_char
                time.sleep(random.uniform(0.1, 0.3))
                # 刪除錯誤的字
                search_box.send_keys(Keys.BACKSPACE)
                typed_text = typed_text[:-1]
                time.sleep(random.uniform(0.1, 0.2))
            
            # 輸入正確的字
            search_box.send_keys(char)
            typed_text += char
            
            # 隨機停頓（模擬思考）
            if char == ' ':  # 空格時停頓較長
                time.sleep(random.uniform(0.2, 0.5))
            else:
                time.sleep(random.uniform(0.05, 0.25))
        
        # 等待一下再按 Enter
        time.sleep(random.uniform(1, 2))
        
        # 隨機選擇提交方式
        if random.random() > 0.3:
            search_box.send_keys(Keys.RETURN)
        else:
            # 找搜尋按鈕並點擊
            try:
                search_button = driver.find_element(By.NAME, "btnK")
                if search_button.is_displayed():
                    search_button.click()
                else:
                    search_box.send_keys(Keys.RETURN)
            except:
                search_box.send_keys(Keys.RETURN)
        
        # 等待搜尋結果
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "search"))
            )
            
            # 額外等待確保頁面完全載入
            wait_with_random_actions(driver, 2, 4)
            
            # 再次檢查 CAPTCHA
            if check_for_captcha(driver):
                print("   ⚠️  搜尋後出現 CAPTCHA")
                stats['captcha_detected'] += 1
                return False
            
            print("   ✅ 搜尋完成")
            return True
            
        except TimeoutException:
            print("   ❌ 搜尋結果載入超時")
            return False
        
    except Exception as e:
        print(f"   ❌ 搜尋失敗: {str(e)[:100]}")
        return False

def find_and_click_target(driver, max_pages=2):
    """人性化尋找並點擊目標"""
    current_page = 1
    
    while current_page <= max_pages:
        try:
            print(f"   📄 瀏覽第 {current_page} 頁...")
            
            # 模擬閱讀頁面
            simulate_human_behavior(driver)
            wait_with_random_actions(driver, 2, 4)
            
            # 收集連結
            link_info = []
            link_selectors = [
                ".yuRUbf a",
                ".g a[href]",
                "h3 a"
            ]
            
            for selector in link_selectors:
                try:
                    links = driver.find_elements(By.CSS_SELECTOR, selector)
                    for link in links:
                        try:
                            href = link.get_attribute("href")
                            text = link.text
                            if href and 'http' in href:
                                link_info.append({
                                    'href': href,
                                    'text': text,
                                    'element': link
                                })
                        except:
                            continue
                except:
                    continue
            
            # 去重
            seen_urls = set()
            unique_links = []
            for info in link_info:
                if info['href'] not in seen_urls:
                    unique_links.append(info)
                    seen_urls.add(info['href'])
            
            print(f"   🔍 找到 {len(unique_links)} 個連結")
            
            # 隨機瀏覽一些其他連結（模擬真人行為）
            if len(unique_links) > 3 and random.random() > 0.7:
                random_link = random.choice(unique_links[:5])
                if target_domain_keyword.lower() not in random_link['href'].lower():
                    print(f"   👀 隨機查看其他結果...")
                    try:
                        driver.execute_script("arguments[0].scrollIntoView(true);", random_link['element'])
                        wait_with_random_actions(driver, 1, 2)
                    except:
                        pass
            
            # 尋找目標
            for info in unique_links:
                if target_domain_keyword.lower() in info['href'].lower():
                    print(f"   🎯 找到目標: {info['text'][:50]}")
                    
                    # 滾動到連結位置
                    try:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", info['element'])
                        wait_with_random_actions(driver, 1, 2)
                    except:
                        pass
                    
                    # 使用 JavaScript 點擊（更可靠）
                    try:
                        driver.execute_script("arguments[0].click();", info['element'])
                        wait_with_random_actions(driver, 5, 8)
                        
                        current_url = driver.current_url
                        if target_domain_keyword.lower() in current_url.lower():
                            print(f"   ✅ 成功進入目標網站")
                            return True, current_url, current_page
                    except:
                        # 備用方案：直接導航
                        driver.get(info['href'])
                        wait_with_random_actions(driver, 5, 8)
                        
                        current_url = driver.current_url
                        if target_domain_keyword.lower() in current_url.lower():
                            print(f"   ✅ 成功進入目標網站（直接導航）")
                            return True, current_url, current_page
            
            # 下一頁
            if current_page < max_pages:
                try:
                    next_button = driver.find_element(By.ID, "pnnext")
                    if next_button.is_displayed():
                        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                        wait_with_random_actions(driver, 1, 2)
                        next_button.click()
                        current_page += 1
                        wait_with_random_actions(driver, 3, 5)
                    else:
                        break
                except:
                    break
            else:
                break
                
        except Exception as e:
            print(f"   ❌ 處理失敗: {str(e)[:100]}")
            break
    
    return False, None, 0

def browse_target_website(driver):
    """瀏覽目標網站"""
    try:
        print("   🤖 開始瀏覽網站...")
        
        # 初始停留
        wait_with_random_actions(driver, 2, 4)
        
        # 滾動瀏覽
        total_height = driver.execute_script("return document.body.scrollHeight")
        current_position = 0
        
        while current_position < total_height * 0.7:  # 瀏覽70%的頁面
            scroll_amount = random.randint(200, 400)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            current_position += scroll_amount
            
            # 隨機停頓閱讀
            if random.random() > 0.7:
                time.sleep(random.uniform(2, 5))
            else:
                time.sleep(random.uniform(0.5, 2))
        
        # 嘗試點擊一些內部連結
        try:
            internal_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='" + target_domain_keyword + "']")
            if internal_links and random.random() > 0.5:
                random_link = random.choice(internal_links[:5])
                if random_link.is_displayed():
                    print("   📄 訪問內部頁面...")
                    driver.execute_script("arguments[0].click();", random_link)
                    wait_with_random_actions(driver, 3, 6)
        except:
            pass
        
        print("   ✅ 網站瀏覽完成")
        
    except Exception as e:
        print(f"   ⚠️  瀏覽時發生錯誤: {str(e)[:50]}")

def check_hourly_limit():
    """檢查小時限制"""
    current_hour = datetime.now().hour
    current_time = time.time()
    
    # 清理超過一小時的記錄
    stats['hourly_searches'] = [t for t in stats['hourly_searches'] 
                                if current_time - t < 3600]
    
    # 檢查是否超過限制
    if len(stats['hourly_searches']) >= hourly_search_limit:
        print(f"   ⚠️  已達到每小時限制 ({hourly_search_limit} 次)")
        return False
    
    return True

def perform_search_and_click(search_engine_url, search_query):
    """執行完整的搜尋和點擊流程"""
    driver = None
    success = False
    target_found = False
    target_clicked = False
    final_url = ""
    found_on_page = 0
    
    try:
        # 檢查小時限制
        if not check_hourly_limit():
            wait_time = random.randint(1800, 3600)  # 30-60分鐘
            print(f"   ⏳ 等待 {wait_time//60} 分鐘後繼續...")
            time.sleep(wait_time)
        
        # 記錄搜尋時間
        stats['hourly_searches'].append(time.time())
        
        # 建立瀏覽器
        driver, user_agent = create_webdriver_with_retry()
        if not driver:
            raise Exception("無法啟動瀏覽器")
        
        # 執行搜尋
        print(f"   🔍 搜尋: {search_query}")
        if not search_with_google(driver, search_query):
            raise Exception("搜尋執行失敗")
        
        success = True
        stats['successful_searches'] += 1
        stats['keyword_stats'][search_query]['used_count'] += 1
        
        # 尋找並點擊目標
        clicked, final_url, found_on_page = find_and_click_target(driver)
        
        if found_on_page > 0:
            target_found = True
            stats['target_found'] += 1
            stats['keyword_stats'][search_query]['found_count'] += 1
            
            if clicked:
                target_clicked = True
                stats['target_clicked'] += 1
                stats['keyword_stats'][search_query]['clicked_count'] += 1
                
                # 瀏覽網站
                stay_time = random.randint(min_stay_time, max_stay_time)
                print(f"   ⏱️  停留 {stay_time} 秒")
                browse_target_website(driver)
                wait_with_random_actions(driver, stay_time/2, stay_time)
        
    except Exception as e:
        print(f"   ❌ 錯誤: {str(e)[:100]}")
        stats['failed_searches'] += 1
        
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
        'final_url': final_url,
        'query': search_query,
        'found_on_page': found_on_page
    }

def print_statistics():
    """顯示統計信息"""
    elapsed_time = (time.time() - stats['start_time']) / 60
    
    print("\n" + "="*50)
    print("📊 執行統計")
    print("="*50)
    
    print(f"⏱️  總執行時間: {elapsed_time:.1f} 分鐘")
    print(f"✅ 成功搜尋: {stats['successful_searches']}")
    print(f"❌ 失敗搜尋: {stats['failed_searches']}")
    print(f"🎯 發現目標: {stats['target_found']}")
    print(f"🖱️  點擊目標: {stats['target_clicked']}")
    print(f"🚫 CAPTCHA 檢測: {stats['captcha_detected']} 次")
    
    if stats['successful_searches'] > 0:
        find_rate = (stats['target_found'] / stats['successful_searches']) * 100
        click_rate = (stats['target_clicked'] / max(stats['target_found'], 1)) * 100
        print(f"📈 發現率: {find_rate:.1f}%")
        print(f"📈 點擊率: {click_rate:.1f}%")
    
    print("\n📋 關鍵字統計:")
    for keyword, kstats in stats['keyword_stats'].items():
        if kstats['used_count'] > 0:
            print(f"  • {keyword}")
            print(f"    使用: {kstats['used_count']} | 發現: {kstats['found_count']} | 點擊: {kstats['clicked_count']}")

# ==========================================
# 主程式
# ==========================================

def main():
    """主程式"""
    print("🚀 Google SEO 機器人 - 反檢測加強版")
    print("="*60)
    print(f"🖥️  系統: {platform.system()}")
    print(f"🎯 目標: '{target_domain_keyword}'")
    print(f"⏱️  間隔: {min_delay_between_runs}-{max_delay_between_runs} 秒")
    print(f"🛡️  限制: 每小時最多 {hourly_search_limit} 次")
    print(f"📝 關鍵字: {len(search_keywords)} 個")
    
    # 顯示警告
    print("\n⚠️  注意事項:")
    print("  • 程式包含反檢測機制")
    print("  • 自動處理 CAPTCHA 檢測")
    print("  • 模擬真實用戶行為")
    print("  • 建議在不同時段執行")
    
    print("\n🚀 3 秒後自動開始執行...")
    time.sleep(3)
    
    consecutive_failures = 0
    captcha_wait_count = 0
    
    for run in range(1, total_runs + 1):
        print(f"\n{'='*20} 執行 {run}/{total_runs} {'='*20}")
        
        # CAPTCHA 保護
        if stats['captcha_detected'] > captcha_wait_count:
            captcha_wait_count = stats['captcha_detected']
            wait_time = min(300 * captcha_wait_count, 1800)  # 最多等30分鐘
            print(f"🚫 檢測到 CAPTCHA，等待 {wait_time//60} 分鐘...")
            time.sleep(wait_time)
        
        # 連續失敗保護
        if consecutive_failures >= 3:
            print(f"❌ 連續失敗 {consecutive_failures} 次，長時間休息...")
            time.sleep(random.randint(300, 600))
            consecutive_failures = 0
        
        # 長休息
        if run > 1 and (run - 1) % long_break_interval == 0:
            break_time = random.randint(long_break_min, long_break_max)
            print(f"🛌 休息時間 ({break_time//60} 分鐘)")
            print_statistics()
            time.sleep(break_time)
        
        # 選擇關鍵字
        keyword = random.choice(search_keywords)
        
        # 執行搜尋
        result = perform_search_and_click(search_engine, keyword)
        
        # 更新失敗計數
        if result['success']:
            consecutive_failures = 0
        else:
            consecutive_failures += 1
        
        # 記錄結果
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n📝 [{timestamp}] 結果:")
        print(f"  關鍵字: {result['query']}")
        print(f"  成功: {'✅' if result['success'] else '❌'}")
        if result['target_found']:
            print(f"  找到: 第 {result['found_on_page']} 頁")
        if result['target_clicked']:
            print(f"  點擊: ✅")
        
        # 智慧等待
        if run < total_runs:
            if result['target_clicked']:
                # 成功點擊後等待較長時間
                delay = random.randint(max_delay_between_runs, max_delay_between_runs * 2)
            elif result['success']:
                # 搜尋成功但未點擊
                delay = random.randint(min_delay_between_runs, max_delay_between_runs)
            else:
                # 失敗後等待更長
                delay = random.randint(max_delay_between_runs, max_delay_between_runs * 3)
            
            print(f"⏳ 等待 {delay} 秒...")
            time.sleep(delay)
    
    # 最終統計
    print("\n" + "="*60)
    print("🎉 執行完成！")
    print_statistics()
    
    # 建議
    if stats['captcha_detected'] > 0:
        print(f"\n💡 建議:")
        print(f"  • 檢測到 {stats['captcha_detected']} 次 CAPTCHA")
        print(f"  • 建議降低頻率或使用代理")
        print(f"  • 可以嘗試更換 IP 或等待更長時間")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⛔ 程式被中斷")
        print_statistics()
    except Exception as e:
        print(f"\n💥 程式錯誤: {str(e)}")
        print_statistics()