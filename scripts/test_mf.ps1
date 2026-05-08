# ==============================================================
#  test_judge0_lang89.ps1
#  Sends a language_id=89 (Multi-file Program) submission to
#  your Judge0 instance and prints the full request + response.
#
#  Usage:
#    .\test_judge0_lang89.ps1
#    .\test_judge0_lang89.ps1 -BaseUrl "http://10.10.142.96:2360"
#    .\test_judge0_lang89.ps1 -Wait $false    # async + poll
# ==============================================================
param(
    [string]$BaseUrl = "http://10.10.142.96:2360",
    [bool]  $Wait    = $false
)

Set-StrictMode -Off

# ── 1. File contents ────────────────────────────────────────────
$solutionCode = @'
from fastapi import FastAPI

app = FastAPI()

@app.get("/greet")
def greet(name: str = "Guest"):
    return {"message": f"Welcome, {name}!"}
'@

$testCode = @'
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_greet_with_name():
    response = client.get('/greet?name=Alice')
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome, Alice!"}

def test_greet_default():
    response = client.get('/greet')
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome, Guest!"}
'@

$runScript = @'
#!/usr/bin/env bash
set -e
pytest
'@

# ── 2. Build in-memory ZIP → base64 ─────────────────────────────
Add-Type -AssemblyName System.IO.Compression

$memStream  = [System.IO.MemoryStream]::new()
$zipArchive = [System.IO.Compression.ZipArchive]::new(
    $memStream,
    [System.IO.Compression.ZipArchiveMode]::Create,
    $true
)

foreach ($item in @(
    [pscustomobject]@{ Name = "run";          Content = $runScript    }
    [pscustomobject]@{ Name = "main.py";      Content = $solutionCode }
    [pscustomobject]@{ Name = "test_main.py"; Content = $testCode      }
)) {
    $entry  = $zipArchive.CreateEntry($item.Name)
    $writer = [System.IO.StreamWriter]::new($entry.Open())
    $writer.Write($item.Content)
    $writer.Dispose()
}
$zipArchive.Dispose()

$zipBytes   = $memStream.ToArray()
$memStream.Dispose()
$b64Archive = [Convert]::ToBase64String($zipBytes)

# ── 3. Build URL + JSON body ─────────────────────────────────────
$waitFlag = if ($Wait) { "true" } else { "false" }
$url      = $BaseUrl + "/submissions?base64_encoded=false&wait=" + $waitFlag

$body = [ordered]@{
    language_id      = 89
    additional_files = $b64Archive
}
$bodyJson = $body | ConvertTo-Json -Compress

# ── 4. Print the full outgoing request ───────────────────────────
$b64Len     = $b64Archive.Length
$runLen     = $runScript.Length
$solLen     = $solutionCode.Length
$testLen    = $testCode.Length

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  JUDGE0 REQUEST  (language_id = 89)"              -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Method  : POST"
Write-Host "  URL     : $url"
Write-Host "  Headers : Content-Type: application/json"
Write-Host "  Body:"
Write-Host "    language_id      = 89"
Write-Host "    additional_files = [base64 $b64Len chars]"
Write-Host "  Zip entries:"
Write-Host "    run          ($runLen bytes)"
Write-Host "    main.py      ($solLen bytes)   <- solution (FastAPI app)"
Write-Host "    test_main.py ($testLen bytes)  <- test harness (TestClient)"
Write-Host ""

# ── 5. Send ──────────────────────────────────────────────────────
# Allow self-signed / corporate-proxy certs (PS5 compatible)
add-type @"
    using System.Net;
    using System.Security.Cryptography.X509Certificates;
    public class TrustAll : ICertificatePolicy {
        public bool CheckValidationResult(
            ServicePoint sp, X509Certificate cert,
            WebRequest req, int problem) { return true; }
    }
"@
[System.Net.ServicePointManager]::CertificatePolicy = [TrustAll]::new()
[System.Net.ServicePointManager]::SecurityProtocol  = [System.Net.SecurityProtocolType]::Tls12

$reqHeaders = @{ "Content-Type" = "application/json" }

try {
    $wc             = [System.Net.WebClient]::new()
    $wc.Headers.Add("Content-Type", "application/json")
    $sw             = [System.Diagnostics.Stopwatch]::StartNew()
    $rawResponse    = $wc.UploadString($url, "POST", $bodyJson)
    $sw.Stop()
    $resp           = $rawResponse | ConvertFrom-Json

    # ── 6. Print the response ─────────────────────────────────────
    $elapsed    = $sw.ElapsedMilliseconds
    $statusId   = $resp.status.id
    $statusDesc = $resp.status.description
    $passed     = ($statusId -eq 3)
    $color      = if ($passed) { "Green" } else { "Red" }
    $token      = $resp.token
    $rtime      = $resp.time
    $rmem       = $resp.memory

    Write-Host "==================================================" -ForegroundColor Green
    Write-Host "  JUDGE0 RESPONSE  (round-trip ${elapsed} ms)"      -ForegroundColor Green
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host "  token   : $token"
    Write-Host "  status  : [$statusId] $statusDesc" -ForegroundColor $color
    Write-Host "  time    : $rtime s"
    Write-Host "  memory  : $rmem KB"
    Write-Host "  passed  : $passed"                 -ForegroundColor $color

    Write-Host ""
    Write-Host "  -- stdout --"
    if ($resp.stdout) { Write-Host $resp.stdout -ForegroundColor White }
    else              { Write-Host "  (empty)"   -ForegroundColor DarkGray }

    Write-Host "  -- stderr --"
    if ($resp.stderr) { Write-Host $resp.stderr -ForegroundColor Yellow }
    else              { Write-Host "  (empty)"   -ForegroundColor DarkGray }

    Write-Host "  -- compile_output --"
    if ($resp.compile_output) { Write-Host $resp.compile_output -ForegroundColor Yellow }
    else                      { Write-Host "  (empty)"          -ForegroundColor DarkGray }

    Write-Host "  -- message --"
    if ($resp.message) { Write-Host $resp.message -ForegroundColor Yellow }
    else               { Write-Host "  (empty)"   -ForegroundColor DarkGray }

    Write-Host ""
    Write-Host "  -- raw JSON --"
    $resp | ConvertTo-Json -Depth 5 | Write-Host -ForegroundColor DarkGray

    # ── 7. Async polling (if -Wait $false) ───────────────────────
    if ((-not $Wait) -and $token) {
        Write-Host ""
        Write-Host "  [async] Polling token $token ..." -ForegroundColor Cyan
        $terminalIds = @(3,4,5,6,7,8,9,10,11,12,13,14)
        for ($i = 0; $i -lt 20; $i++) {
            Start-Sleep -Milliseconds 500
            $pollUrl  = $BaseUrl + "/submissions/" + $token + "?base64_encoded=false"
            $wc2      = [System.Net.WebClient]::new()
            $wc2.Headers.Add("Content-Type", "application/json")
            $rawPoll  = $wc2.DownloadString($pollUrl)
            $poll     = $rawPoll | ConvertFrom-Json
            $pid2  = $poll.status.id
            $pdesc = $poll.status.description
            Write-Host "  [poll $i] status=[$pid2] $pdesc"
            if ($terminalIds -contains $pid2) {
                $poll | ConvertTo-Json -Depth 5 | Write-Host -ForegroundColor DarkGray
                break
            }
        }
    }

} catch {
    $errMsg = $_.ToString()
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Red
    Write-Host "  JUDGE0 ERROR"                                      -ForegroundColor Red
    Write-Host "==================================================" -ForegroundColor Red
    Write-Host "  $errMsg" -ForegroundColor Red

    $exResp = $_.Exception.Response
    if ($null -ne $exResp) {
        $stream = $exResp.GetResponseStream()
        $reader = [System.IO.StreamReader]::new($stream)
        $body2  = $reader.ReadToEnd()
        $reader.Dispose()
        Write-Host "  Response body: $body2" -ForegroundColor Red
    }
}