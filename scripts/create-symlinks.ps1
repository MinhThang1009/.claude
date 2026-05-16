# $src = repo root (thư mục chứa script này)
$src = Split-Path -Parent $PSScriptRoot
# $dst = ~/.claude
$dst = Join-Path $env:USERPROFILE ".claude"

Write-Host "Source: $src"
Write-Host "Target: $dst"
New-Item -ItemType Directory -Force $dst | Out-Null

# --- Parse .claude-load.txt ---
# Format: "plugin" | "plugin:agents" | "plugin:skills" | "plugin:commands"
$loadFile = "$src\.claude-load.txt"
# loadMap: plugin -> set of types ("agents","skills","commands","all")
$loadMap = @{}

if (Test-Path $loadFile) {
    Get-Content $loadFile | Where-Object { $_ -notmatch '^\s*#' -and $_ -match '\S' } | ForEach-Object {
        $line = $_.Trim()
        if ($line -match '^(.+):(.+)$') {
            $plugin = $matches[1].Trim(); $type = $matches[2].Trim()
            if (-not $loadMap.ContainsKey($plugin)) { $loadMap[$plugin] = @() }
            $loadMap[$plugin] += $type
        } else {
            $loadMap[$line] = @("all")
        }
    }
}

$loadAll = $loadMap.Count -eq 0
if ($loadAll) { Write-Host "Loading ALL plugins" }
else { Write-Host "Load config: $($loadMap.Keys -join ', ')" }

function Should-Load-Type($plugin, $type) {
    if ($loadAll) { return $true }
    if (-not $loadMap.ContainsKey($plugin)) { return $false }
    $types = $loadMap[$plugin]
    return ($types -contains "all") -or ($types -contains $type)
}

# --- Dirs symlinked as whole ---
$dirs = @(".claude-plugin", "docs", "hooks", "output-styles", "rules", "templates")
foreach ($d in $dirs) {
    $dstPath = "$dst\$d"
    $srcPath = "$src\$d"
    $item = Get-Item $dstPath -ErrorAction SilentlyContinue
    if ($item) { $item.Delete() }
    & cmd.exe /c "mklink /D `"$dstPath`" `"$srcPath`"" | Out-Null
    Write-Host "OK dir: $d"
}

# --- Files symlinked individually ---
$files = @("CLAUDE.md", "README.md")
foreach ($f in $files) {
    $dstPath = "$dst\$f"
    $srcPath = "$src\$f"
    if (Test-Path $dstPath) { Remove-Item $dstPath -Force }
    & cmd.exe /c "mklink `"$dstPath`" `"$srcPath`"" | Out-Null
    Write-Host "OK file: $f"
}

# --- agents/ ---
$agentsDir = "$dst\agents"
if (Test-Path $agentsDir) { Remove-Item $agentsDir -Recurse -Force }
New-Item -ItemType Directory -Force $agentsDir | Out-Null
Get-ChildItem "$src\plugins" -Directory | Where-Object { Should-Load-Type $_.Name "agents" } | ForEach-Object {
    $pluginAgentsDir = Join-Path $_.FullName "agents"
    if (Test-Path $pluginAgentsDir) {
        Get-ChildItem $pluginAgentsDir -Filter "*.md" | ForEach-Object {
            & cmd.exe /c "mklink `"$agentsDir\$($_.Name)`" `"$($_.FullName)`"" | Out-Null
        }
    }
}
Write-Host "OK agents: $((Get-ChildItem $agentsDir).Count) files"

# --- skills/ ---
$skillsDir = "$dst\skills"
if (Test-Path $skillsDir) { Remove-Item $skillsDir -Recurse -Force }
New-Item -ItemType Directory -Force $skillsDir | Out-Null
Get-ChildItem "$src\plugins" -Directory | Where-Object { Should-Load-Type $_.Name "skills" } | ForEach-Object {
    $d = "$($_.FullName)\skills"
    if (Test-Path $d) {
        Get-ChildItem $d -Directory | ForEach-Object {
            & cmd.exe /c "mklink /D `"$skillsDir\$($_.Name)`" `"$($_.FullName)`"" | Out-Null
        }
    }
}
Write-Host "OK skills: $((Get-ChildItem $skillsDir).Count) dirs"

# --- commands/ ---
$commandsDir = "$dst\commands"
if (Test-Path $commandsDir) { Remove-Item $commandsDir -Recurse -Force }
New-Item -ItemType Directory -Force $commandsDir | Out-Null
Get-ChildItem "$src\plugins" -Directory | Where-Object { Should-Load-Type $_.Name "commands" } | ForEach-Object {
    $d = "$($_.FullName)\commands"
    if (Test-Path $d) {
        Get-ChildItem $d -Filter "*.md" | ForEach-Object {
            & cmd.exe /c "mklink `"$commandsDir\$($_.Name)`" `"$($_.FullName)`"" | Out-Null
        }
    }
}
Write-Host "OK commands: $((Get-ChildItem $commandsDir -Filter '*.md').Count) files"

# --- settings.json (copy nếu chưa có) ---
$settingsDst = Join-Path $dst "settings.json"
if (-not (Test-Path $settingsDst)) {
    Copy-Item (Join-Path $src "settings.example.json") $settingsDst
    Write-Host "OK settings: copied settings.example.json -> settings.json"
} else {
    Write-Host "SKIP settings: settings.json da ton tai (giu nguyen config hien tai)"
}

Write-Host ""
Write-Host "Done! Restart Claude Code de apply changes."
