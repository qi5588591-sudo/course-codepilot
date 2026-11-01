$ErrorActionPreference = 'Stop'
$projectRoot=Split-Path -Parent $PSScriptRoot
Add-Type -AssemblyName System.Speech
$speaker=New-Object System.Speech.Synthesis.SpeechSynthesizer
$speaker.SelectVoice('Microsoft Huihui Desktop')
$speaker.Rate=1
$audioFolder=Join-Path $projectRoot 'build/audio'
New-Item -ItemType Directory -Force -Path $audioFolder | Out-Null
try {
    $slides=Get-Content -Raw -Encoding utf8 -LiteralPath (Join-Path $projectRoot 'build/narration.json') | ConvertFrom-Json
    $number=0
    foreach ($slide in $slides) {
        $number++
        $speechText=$slide.notes -replace '(参考|来源)：.*$',''
        $target=Join-Path $audioFolder ('speech-{0:D2}.wav' -f $number)
        $speaker.SetOutputToWaveFile($target)
        $speaker.Speak($speechText)
        $speaker.SetOutputToNull()
    }
} finally { $speaker.Dispose() }
