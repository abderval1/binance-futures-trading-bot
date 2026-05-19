$nodeDir = "C:\Users\agostinho.rosario\Downloads\bot\nodejs\node-v20.11.0-win-x64"
$env:Path = $nodeDir + ";" + $env:Path
Set-Location "C:\Users\agostinho.rosario\Downloads\bot\frontend"
Write-Host "Starting frontend dev server..."
Write-Host "URL: http://localhost:5173"
npm run dev
