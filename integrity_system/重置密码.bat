@echo off
chcp 65001 >nul
echo ====================================
echo    廉政意见智答系统 - 密码重置工具
echo ====================================
echo.

:: 获取新的管理员密码
set /p NEW_PASS="请输入新的管理员密码（默认: admin123）: "
if "%NEW_PASS%"=="" set NEW_PASS=admin123

:: 计算带盐哈希并直接更新数据库
powershell -Command "$password = '%NEW_PASS%'; $salt = [guid]::NewGuid().ToString('N'); $hash = [System.Security.Cryptography.Rfc2898DeriveBytes]::HashPassword($password, $salt, 100000, 'SHA256'); $hashB64 = [Convert]::ToBase64String($hash); $storedHash = \"$salt`$$hashB64\"; Write-Host \"生成的密码哈希: $storedHash\"; Add-Type -AssemblyName 'System.Data.SQLite'; $dbPath = 'data\integrity.db'; if (!(Test-Path $dbPath)) { Write-Host '错误：数据库文件不存在，请先运行程序'; exit 1 }; [System.Data.SQLite.SQLiteConnection]::GlobalStaticFix = $null; $conn = New-Object System.Data.SQLite.SQLiteConnection(\"Data Source=$dbPath;Version=3;\"); $conn.Open(); $cmd = $conn.CreateCommand(); $cmd.CommandText = 'CREATE TABLE IF NOT EXISTS system_config (id INTEGER PRIMARY KEY AUTOINCREMENT, config_key TEXT UNIQUE, config_value TEXT, updated_at TEXT DEFAULT CURRENT_TIMESTAMP)'; $cmd.ExecuteNonQuery() | Out-Null; $cmd.CommandText = \"DELETE FROM system_config WHERE config_key = 'admin_password_hash'\"; $cmd.ExecuteNonQuery() | Out-Null; $cmd.CommandText = 'INSERT INTO system_config (config_key, config_value) VALUES (''admin_password_hash'', ''' + $storedHash + ''')'; $cmd.ExecuteNonQuery() | Out-Null; $conn.Close(); Write-Host ''; Write-Host '密码重置成功！'; Write-Host '新密码: %NEW_PASS%' "

echo.
pause
