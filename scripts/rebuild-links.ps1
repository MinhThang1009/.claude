$src = Split-Path -Parent $PSScriptRoot
$dst = Join-Path $env:USERPROFILE ".claude"

$loadMap = @{}
Get-Content "$src\.claude-load.txt" | Where-Object { $_ -notmatch '^\s*#' -and $_ -match '\S' } | ForEach-Object {
    $line = $_.Trim()
    if ($line -match '^(.+):(.+)$') {
        $plugin = $matches[1].Trim(); $type = $matches[2].Trim()
        if (-not $loadMap.ContainsKey($plugin)) { $loadMap[$plugin] = @() }
        $loadMap[$plugin] += $type
    } else {
        $loadMap[$line] = @("all")
    }
}
Write-Host "Plugins: $($loadMap.Keys -join ', ')"

function Should-Load($plugin, $type) {
    if (-not $loadMap.ContainsKey($plugin)) { return $false }
    $types = $loadMap[$plugin]
    return ($types -contains "all") -or ($types -contains $type)
}

foreach ($kind in @("skills", "agents", "commands")) {
    Remove-Item "$dst\$kind" -Recurse -Force -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Force "$dst\$kind" | Out-Null
}

$sc = 0; $ac = 0; $cc = 0
Get-ChildItem "$src\plugins" -Directory | ForEach-Object {
    $pname = $_.Name; $pfull = $_.FullName

    if (Should-Load $pname "skills") {
        $d = "$pfull\skills"
        if (Test-Path $d) {
            Get-ChildItem $d -Directory | ForEach-Object {
                cmd /c mklink /J "`"$dst\skills\$($_.Name)`"" "`"$($_.FullName)`"" 2>&1 | Out-Null
                $sc++
            }
        }
    }
    if (Should-Load $pname "agents") {
        $d = "$pfull\agents"
        if (Test-Path $d) {
            Get-ChildItem $d -Filter "*.md" | ForEach-Object {
                cmd /c mklink /H "`"$dst\agents\$($_.Name)`"" "`"$($_.FullName)`"" 2>&1 | Out-Null
                $ac++
            }
        }
    }
    if (Should-Load $pname "commands") {
        $d = "$pfull\commands"
        if (Test-Path $d) {
            Get-ChildItem $d -Filter "*.md" | ForEach-Object {
                cmd /c mklink /H "`"$dst\commands\$($_.Name)`"" "`"$($_.FullName)`"" 2>&1 | Out-Null
                $cc++
            }
        }
    }
}
Write-Host "Done: skills=$sc agents=$ac commands=$cc"
