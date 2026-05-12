# $src = repo root (thư mục chứa script này)
$src = Split-Path -Parent $PSScriptRoot
# $dst = ~/.claude
$dst = Join-Path $env:USERPROFILE ".claude"

Write-Host "Source: $src"
Write-Host "Target: $dst"
New-Item -ItemType Directory -Force $dst | Out-Null

# --- Đọc .claude-load.txt để lọc plugins ---
$loadFile = "$src\.claude-load.txt"
$loadedPlugins = $null
if (Test-Path $loadFile) {
    $loadedPlugins = Get-Content $loadFile |
        Where-Object { $_ -notmatch '^\s*#' -and $_ -match '\S' } |
        ForEach-Object { $_.Trim() }
    if ($loadedPlugins.Count -gt 0) {
        Write-Host "Loading plugins: $($loadedPlugins -join ', ')"
    } else {
        $loadedPlugins = $null
    }
}
if (-not $loadedPlugins) { Write-Host "Loading ALL plugins" }

function Should-Load($pluginName) {
    if (-not $loadedPlugins) { return $true }
    return $loadedPlugins -contains $pluginName
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

# --- agents/: collect từ plugins/**/agents/*.md → flat symlinks (recursive) ---
$agentsDir = "$dst\agents"
if (Test-Path $agentsDir) { Remove-Item $agentsDir -Recurse -Force }
New-Item -ItemType Directory -Force $agentsDir | Out-Null
Get-ChildItem "$src\plugins" -Directory | Where-Object { Should-Load $_.Name } | ForEach-Object {
    Get-ChildItem $_.FullName -Recurse -Filter "agents" -Directory | ForEach-Object {
        Get-ChildItem $_.FullName -Filter "*.md" | ForEach-Object {
            $link = "$agentsDir\$($_.Name)"
            & cmd.exe /c "mklink `"$link`" `"$($_.FullName)`"" | Out-Null
        }
    }
}
Write-Host "OK agents: $((Get-ChildItem $agentsDir).Count) files"

# --- skills/: collect từ plugins/*/skills/*/ → flat dir symlinks ---
$skillsDir = "$dst\skills"
if (Test-Path $skillsDir) { Remove-Item $skillsDir -Recurse -Force }
New-Item -ItemType Directory -Force $skillsDir | Out-Null
Get-ChildItem "$src\plugins" -Directory | Where-Object { Should-Load $_.Name } | ForEach-Object {
    $d = "$($_.FullName)\skills"
    if (Test-Path $d) {
        Get-ChildItem $d -Directory | ForEach-Object {
            $link = "$skillsDir\$($_.Name)"
            & cmd.exe /c "mklink /D `"$link`" `"$($_.FullName)`"" | Out-Null
        }
    }
}
Write-Host "OK skills: $((Get-ChildItem $skillsDir).Count) dirs"

# --- commands/: collect từ plugins/*/commands/*.md → flat symlinks ---
$commandsDir = "$dst\commands"
if (Test-Path $commandsDir) { Remove-Item $commandsDir -Recurse -Force }
New-Item -ItemType Directory -Force $commandsDir | Out-Null
Get-ChildItem "$src\plugins" -Directory | Where-Object { Should-Load $_.Name } | ForEach-Object {
    $d = "$($_.FullName)\commands"
    if (Test-Path $d) {
        Get-ChildItem $d -Filter "*.md" | ForEach-Object {
            $link = "$commandsDir\$($_.Name)"
            & cmd.exe /c "mklink `"$link`" `"$($_.FullName)`"" | Out-Null
        }
    }
}
Write-Host "OK commands: $((Get-ChildItem $commandsDir -Filter '*.md').Count) files"

Write-Host ""
Write-Host "Done! Restart Claude Code de apply changes."
