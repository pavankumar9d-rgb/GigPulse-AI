param(
    [string]$Url = "http://localhost:3000",
    [string]$OutputFile = "c:\Users\saipa\OneDrive\Desktop\project sits\screenshots\overview_pass3.png",
    [int]$Width = 1440,
    [int]$Height = 900,
    [int]$DelayMs = 4000
)

$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$rnd = Get-Random
$tmp = "$env:TEMP\chrome-sc-$rnd"

Start-Process -FilePath $chrome -ArgumentList "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--window-size=$Width,$Height", "--virtual-time-budget=$DelayMs", "--user-data-dir=$tmp", "--screenshot=$OutputFile", $Url -Wait

Remove-Item -Path $tmp -Recurse -Force -ErrorAction SilentlyContinue

if (Test-Path $OutputFile) {
    Write-Output "SUCCESS: $OutputFile ($( (Get-Item $OutputFile).Length ) bytes)"
} else {
    Write-Output "FAILED: $OutputFile"
}
