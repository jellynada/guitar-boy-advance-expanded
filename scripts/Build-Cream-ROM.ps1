$ErrorActionPreference = 'Stop'
try {
    $projectRoot = Split-Path -Parent $PSScriptRoot
    if (-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
        throw 'WSL is missing. Follow docs\WINDOWS_PRIVATE_BUILD.md for one-time installation.'
    }
    & wsl.exe --distribution Ubuntu --exec true
    if ($LASTEXITCODE -ne 0) { throw 'Ubuntu in WSL could not start. Open Ubuntu once and finish its setup.' }
    if (-not (Test-Path -LiteralPath (Join-Path $projectRoot 'private\Cream.zip') -PathType Leaf)) {
        throw 'Put your existing song ZIP in private\Cream.zip. Check that Windows has not named it Cream.zip.zip.'
    }
    & wsl.exe --distribution Ubuntu --exec python3 --version
    if ($LASTEXITCODE -ne 0) { throw 'Python is missing in Ubuntu. See docs\WINDOWS_PRIVATE_BUILD.md.' }
    $linuxRoot = (& wsl.exe --distribution Ubuntu --exec wslpath -a -u $projectRoot | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or -not $linuxRoot.StartsWith('/')) { throw 'Could not translate the project folder into a WSL path.' }
    & wsl.exe --distribution Ubuntu --exec python3 "$linuxRoot/tools/build_profile.py" cream --repo $linuxRoot
    if ($LASTEXITCODE -ne 0) { throw 'Build failed. Read the explanation above. No new successful ROM was delivered.' }
    Write-Host "Windows output folder: $projectRoot\builds\private" -ForegroundColor Green
    Write-Host 'Open the newly printed ROM in mGBA (File > Load ROM), or copy it to your flash cartridge.'
    exit 0
} catch {
    Write-Host "BUILD STOPPED: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
