@echo off
REM 設定視窗標題，方便識別
title 遠端批次指令工具 - 後端伺服器

REM --- 步驟 1: 檢查 Python 是否已安裝並加入 PATH ---
echo 正在檢查 Python 環境...
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo 錯誤: 找不到 Python!
    echo 請確認您已安裝 Python，並且在安裝時勾選了 "Add Python to PATH" 選項。
    echo 請參考 README.md 的說明進行安裝。
    echo.
    pause
    exit
)
echo Python 環境檢查通過！

REM --- 步驟 2: 建立並啟用虛擬環境 ---
REM 檢查 venv 虛擬環境資料夾是否存在
if not exist "venv" (
    echo 正在建立新的 Python 虛擬環境 (首次執行)...
    python -m venv venv
)

echo 正在啟用虛擬環境...
call venv\Scripts\activate

REM --- 步驟 3: 安裝所有必要的 Python 套件 ---
echo 正在安裝/更新必要的 Python 套件...
pip install -r requirements.txt --quiet

REM --- 步驟 4: 啟動後端 Flask 伺服器 ---
echo.
echo ======================================================
echo  後端伺服器準備啟動...
echo  請勿關閉此視窗，關閉視窗即代表關閉伺服器。
echo ======================================================
echo.
start "" "public\index.html"
python app.py