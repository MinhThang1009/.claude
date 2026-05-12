$src = "C:\Users\Admin\dotclaude"
$dst = "C:\Users\Admin\.claude"

$dirs = @("agents","docs","hooks","output-styles","rules","skills","templates")
$files = @("CLAUDE.md","README.md")

foreach ($d in $dirs) {
    $dstPath = "$dst\$d"
    $srcPath = "$src\$d"
    if (Test-Path $dstPath) { Remove-Item $dstPath -Recurse -Force }
    $r = & cmd.exe /c "mklink /D `"$dstPath`" `"$srcPath`"" 2>&1
    Write-Host $r
}

foreach ($f in $files) {
    $dstPath = "$dst\$f"
    $srcPath = "$src\$f"
    if (Test-Path $dstPath) { Remove-Item $dstPath -Force }
    $r = & cmd.exe /c "mklink `"$dstPath`" `"$srcPath`"" 2>&1
    Write-Host $r
}
