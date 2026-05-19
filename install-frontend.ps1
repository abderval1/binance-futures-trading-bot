$nodeDir = "C:\Users\agostinho.rosario\Downloads\bot\nodejs\node-v20.11.0-win-x64"
$env:Path = $env:Path + ";" + $nodeDir
Set-Location "C:\Users\agostinho.rosario\Downloads\bot\frontend"
& npm install
