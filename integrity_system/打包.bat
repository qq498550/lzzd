@echo off
chcp 65001 >nul
echo ====================================
echo    廉政意见智答系统 - 打包工具
echo ====================================
echo.

:: 检查 PyInstaller
where pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未安装 PyInstaller
    echo 请运行: pip install pyinstaller
    pause
    exit /b 1
)

echo 开始打包...
echo.

:: 清理旧的构建文件
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

:: 执行打包
pyinstaller app_main.spec --clean

echo.
echo ====================================
if exist "dist\廉政意见智答系统" (
    echo 打包成功！
    echo 输出目录: dist\廉政意见智答系统
    echo.
    echo 打包后的程序已包含：
    echo   - 静态文件（模板、图片等）
    echo   - 数据库存储（密码哈希）
    echo.
    set /p OPEN="是否打开输出目录？(Y/N): "
    if /i "%OPEN%"=="Y" explorer dist\廉政意见智答系统
) else (
    echo 打包失败，请检查错误信息
)
echo ====================================
pause
