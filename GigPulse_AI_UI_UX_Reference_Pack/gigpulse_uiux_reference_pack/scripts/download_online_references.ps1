$ErrorActionPreference = 'Stop'
$Target = Join-Path $PSScriptRoot '..\online_image_references\downloaded'
New-Item -ItemType Directory -Force -Path $Target | Out-Null
$Assets = @(
    @{ Name = '01_delivery_courier_night.jpg'; Url = 'https://images.unsplash.com/photo-1758956934245-8daff43eb1e4?auto=format&fit=crop&fm=jpg&q=80&w=1800' },
    @{ Name = '02_scooter_traffic_night.jpg'; Url = 'https://images.unsplash.com/photo-1775385921269-785d23dccc0e?auto=format&fit=crop&fm=jpg&q=80&w=1800' },
    @{ Name = '03_dark_scooter_city.jpg'; Url = 'https://images.unsplash.com/photo-1762170318020-eb36a4461eab?auto=format&fit=crop&fm=jpg&q=80&w=1800' }
)
foreach ($Asset in $Assets) {
    $Out = Join-Path $Target $Asset.Name
    try {
        Invoke-WebRequest -Uri $Asset.Url -OutFile $Out -Headers @{ 'User-Agent' = 'Mozilla/5.0' } -TimeoutSec 30
        if ((Get-Item $Out).Length -lt 10000) { throw 'Downloaded file is unexpectedly small.' }
        Write-Host "DOWNLOADED $($Asset.Name)" -ForegroundColor Green
    }
    catch {
        if (Test-Path $Out) { Remove-Item $Out -Force }
        Write-Warning "Could not download $($Asset.Name): $($_.Exception.Message)"
    }
}
Write-Host "Image reference directory: $Target"
