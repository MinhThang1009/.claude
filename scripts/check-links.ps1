$dst = Join-Path $env:USERPROFILE ".claude"

Write-Host "`n=== ~/.claude symlink status ===" -ForegroundColor Cyan
Get-ChildItem $dst | ForEach-Object {
    if ($_.LinkType) {
        Write-Host ("  " + $_.Name.PadRight(25) + $_.LinkType.PadRight(14) + "-> " + $_.Target) -ForegroundColor Green
    } else {
        Write-Host ("  " + $_.Name.PadRight(25) + "[local]") -ForegroundColor Gray
    }
}
Write-Host ""
