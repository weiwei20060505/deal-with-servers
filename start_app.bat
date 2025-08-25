@echo off
REM 切換命令提示字元的編碼為 UTF-8
chcp 65001 >nul

REM 設定視窗標題
title 遠端批次指令工具 - 後端伺服器 (終極偵錯模式)

REM --- 【新增】啟用命令擴充功能，讓錯誤捕捉更可靠 ---
setlocal enabledelayedexpansion

REM --- 步驟 1: 檢查 Python 環境 ---
echo 正在檢查 Python 環境...
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo ==================== 錯誤! ====================
    echo  找不到 Python! 請重新安裝並勾選 "Add Python to PATH"。
    echo =============================================
    goto :error
)
echo Python 環境檢查通過！
echo.

REM --- 步驟 2: 建立並啟用虛擬環境 ---
if not exist "venv" (
    echo 正在建立新的 Python 虛擬環境...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo 建立虛擬環境失敗!
        goto :error
    )
)

echo 正在啟用虛擬環境...
call venv\Scripts\activate

REM --- 步驟 3: 安裝所有必要的 Python 套件 ---
echo 正在安裝/更新必要的 Python 套件 (請稍候)...
pip install -r requirements.txt
if !errorlevel! neq 0 (
    echo.
    echo ==================== 錯誤! ====================
    echo  安裝 Python 套件失敗!
    echo  請檢查您的網路連線，或嘗試手動執行 "pip install -r requirements.txt"。
    echo =============================================
    goto :error
)
echo 套件安裝完成！
echo.

REM --- 步驟 4: 啟動後端 Flask 伺服器 ---
echo ======================================================
echo  後端伺服器準備啟動...
echo  請勿關閉此視窗，關閉視窗即代表關閉伺服器。
echo ======================================================
echo.

start "" "public\index.html"
python app.py

REM --- 【修改】無論如何都會執行到這裡 ---
:error
echo.
echo 腳本已結束執行。
pause