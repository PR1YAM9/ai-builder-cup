param([string]$Deck, [string]$OutDir)
# Export every slide of a deck to PNG using PowerPoint itself (no LibreOffice needed).
$Deck = (Resolve-Path $Deck).Path
New-Item -ItemType Directory -Force $OutDir | Out-Null
$OutDir = (Resolve-Path $OutDir).Path
Get-ChildItem $OutDir -Filter *.png | Remove-Item -Force
$app = New-Object -ComObject PowerPoint.Application
try {
  $pres = $app.Presentations.Open($Deck, $true, $false, $false)
  $i = 1
  foreach ($s in $pres.Slides) {
    $s.Export((Join-Path $OutDir ("slide-{0:D2}.png" -f $i)), "PNG", 1600, 900)
    $i++
  }
  $pres.Close()
} finally {
  $app.Quit()
}
Get-ChildItem $OutDir -Filter *.png | ForEach-Object { $_.FullName }
