# $src = repo root (thư mục chứa script này)
$src = Split-Path -Parent $PSScriptRoot
# $dst = ~/.claude
$dst = Join-Path $env:USERPROFILE ".claude"

Write-Host "Source: $src"
Write-Host "Target: $dst"
New-Item -ItemType Directory -Force $dst | Out-Null

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
$a = Get-Item $agentsDir -ErrorAction SilentlyContinue
if ($a) { $a.Delete() }
New-Item -ItemType Directory -Force $agentsDir | Out-Null
Get-ChildItem "$src\plugins" -Recurse -Filter "agents" -Directory | ForEach-Object {
    $d = $_.FullName
    if (Test-Path $d) {
        Get-ChildItem $d -Filter "*.md" | ForEach-Object {
            $link = "$agentsDir\$($_.Name)"
            & cmd.exe /c "mklink `"$link`" `"$($_.FullName)`"" | Out-Null
        }
    }
}
Write-Host "OK agents: $((Get-ChildItem $agentsDir).Count) files"

# --- skills/: collect từ plugins/*/skills/*/ → flat dir symlinks ---
$skillsDir = "$dst\skills"
$s = Get-Item $skillsDir -ErrorAction SilentlyContinue
if ($s) { $s.Delete() }
New-Item -ItemType Directory -Force $skillsDir | Out-Null
Get-ChildItem "$src\plugins" -Directory | ForEach-Object {
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
$c = Get-Item $commandsDir -ErrorAction SilentlyContinue
if ($c) { $c.Delete() }
New-Item -ItemType Directory -Force $commandsDir | Out-Null
Get-ChildItem "$src\plugins" -Directory | ForEach-Object {
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
Write-Host "Done! Restart Claude Code để apply changes."
