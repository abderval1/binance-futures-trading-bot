$nodePath = 'C:\Users\agostinho.rosario\Downloads\bot\nodejs'
$currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if ($currentPath -notlike "*$nodePath*") {
    [Environment]::SetEnvironmentVariable('Path', "$currentPath;$nodePath", 'User')
    Write-Host 'Node.js added to user PATH permanently'
} else {
    Write-Host 'Node.js already in PATH'
}
