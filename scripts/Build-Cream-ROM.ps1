$ErrorActionPreference = 'Stop'
try {
    $projectRoot = Split-Path -Parent $PSScriptRoot
    $latestPath = Join-Path $projectRoot 'builds\private\LATEST.txt'
    if (Test-Path -LiteralPath $latestPath) { Remove-Item -LiteralPath $latestPath }
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
    $versionFolder = (Get-Content -LiteralPath $latestPath -Raw).Trim()
    if ($versionFolder -notmatch '^[0-9a-f]{12}-[0-9]{8}T[0-9]{6}Z-[0-9a-f]{6}$') {
        throw 'The build did not select a valid new output folder.'
    }
    $buildFolder = Join-Path (Join-Path $projectRoot 'builds\private') $versionFolder
    $manifest = Get-Content -LiteralPath (Join-Path $buildFolder 'manifest.json') -Raw | ConvertFrom-Json
    if ($manifest.status -ne 'success' -or $manifest.profile -ne 'cream' -or
        $manifest.rom -ne 'Guitar-Boy-Advance-M013-Cream-Private.gba') {
        throw 'The completed manifest does not describe the requested private ROM.'
    }
    $romPath = Join-Path $buildFolder $manifest.rom
    if ((Get-FileHash -LiteralPath $romPath -Algorithm SHA256).Hash -ne $manifest.rom_sha256) {
        throw 'The Windows ROM checksum differs from the successful build manifest.'
    }
    Write-Host "Windows ROM: $romPath" -ForegroundColor Green
    Write-Host "Build: $($manifest.build_identity) | Source: $($manifest.source_commit)"
    Write-Host "SHA-256: $($manifest.rom_sha256)"
    Write-Host 'Open the newly printed ROM in mGBA (File > Load ROM), or copy it to your flash cartridge.'
    exit 0
} catch {
    Write-Host "BUILD STOPPED: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
