No-IP 自動更新工具
一個基於 Python 的桌面應用程式，用於自動更新 No-IP 的動態域名，支持多域名管理和運行日誌記錄。


(建議將程式截圖上傳到 GitHub 並提供鏈接)

功能特性
自動更新 No-IP 動態域名
定時向 No-IP 伺服器發送更新請求，保持動態域名指向的 IP 為最新。
多域名支持
添加、刪除多個域名，並定時更新。
運行日誌
實時顯示更新日誌，包括成功、失敗或異常的詳細信息。
所有日誌包含 PST 時區的時間戳。
簡潔的 GUI 界面
支持視窗縮放和動態背景調整。
可最小化到系統托盤，並支持從托盤恢復或退出應用。
獨立執行
支持打包成 .exe 文件，無需安裝 Python 環境即可運行。
使用方法
1. 下載專案
克隆此儲存庫到本地：

bash
複製程式碼
git clone https://github.com/your-username/no-ip-updater.git
cd no-ip-updater
2. 安裝依賴
確保您已安裝 Python（3.8~3.10），然後執行以下命令安裝必要的依賴：

bash
複製程式碼
pip install -r requirements.txt
3. 運行程式
直接執行主程式：

bash
複製程式碼
python main.py
4. 打包成 .exe 文件
如果您需要在沒有 Python 環境的電腦上運行程式，請執行以下指令將程式打包成 .exe 文件：

bash
複製程式碼
pyinstaller --noconfirm --onefile --windowed --icon=icon.ico --add-data "icon.png;." --add-data "background.png;." main.py
打包完成後，dist 資料夾中將生成 main.exe 文件。

文件結構
以下是專案目錄的主要結構：

perl
複製程式碼
no-ip-updater/
│
├── main.py              # 主程式代碼
├── requirements.txt     # 依賴模組列表
├── icon.png             # 應用圖示
├── background.png       # 背景圖片
├── README.md            # 專案說明文件
└── dist/                # 打包後生成的執行檔案
界面截圖
主應用程式

系統需求
作業系統：Windows 10 或以上版本。
Python 版本：3.8 ~ 3.10。
依賴模組：
tkinter（標準庫，無需手動安裝）
requests
pystray
pytz
Pillow
日誌文件
程式將運行日誌記錄到 noip_updater.log 文件，以下是日誌格式的示例：

less
複製程式碼
2024-12-14 12:00:00 PST - INFO - [yue.hopto.org] 更新成功: nochg 123.45.67.89
2024-12-14 12:05:00 PST - ERROR - [yue.hopto.org] 更新錯誤: Timeout
注意事項
如果使用打包後的 .exe 文件，請確保目標電腦運行 Windows 10 或以上。
如果程式無法加載資源文件（如 icon.png 或 background.png），請確認這些文件是否正確包含在打包命令中。
