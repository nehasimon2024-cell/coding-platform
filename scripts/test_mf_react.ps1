# test_judge0_react.ps1 (with time limits, error logging, and base64 decoding)
param(
    [string]$BaseUrl = "http://10.10.142.96:2360",
    [bool]  $Wait    = $false
)

Set-StrictMode -Off

# Helper function to decode base64 (handles null/empty)
function Decode-Base64 {
    param([string]$Encoded)
    if ([string]::IsNullOrEmpty($Encoded)) { return $null }
    try {
        $bytes = [System.Convert]::FromBase64String($Encoded)
        return [System.Text.Encoding]::UTF8.GetString($bytes)
    } catch {
        return $Encoded  # fallback to raw if not valid base64
    }
}

# ── File contents (React test) ────────────────────────────────
$packageJson = @'
{
  "name": "react-test",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0"
  },
  "scripts": {
    "test": "react-scripts test --watchAll=false --passWithNoTests"
  }
}
'@

$solutionCode = @'
// App.jsx – user’s React component
import React from 'react';

function App(props) {
  return (
    <div>
      <h1>Welcome, {props.name || 'Guest'}!</h1>
    </div>
  );
}

export default App;
'@

$testCode = @'
// App.test.js – test suite
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders welcome message with name', () => {
  render(<App name="Aliiiice" />);
  const headingElement = screen.getByText(/Welcome, Alice!/i);
  expect(headingElement).toBeInTheDocument();
});

test('renders default welcome message when no name is provided', () => {
  render(<App />);
  const headingElement = screen.getByText(/Welcome, Guest!/i);
  expect(headingElement).toBeInTheDocument();
});
'@

$runScript = @'
#!/usr/bin/env bash
set -e


npm list
react-scripts test
exit 0
'@

# ── Build ZIP ─────────────────────────────────────────────────
Add-Type -AssemblyName System.IO.Compression

$memStream  = [System.IO.MemoryStream]::new()
$zipArchive = [System.IO.Compression.ZipArchive]::new(
    $memStream,
    [System.IO.Compression.ZipArchiveMode]::Create,
    $true
)

foreach ($item in @(
    [pscustomobject]@{ Name = "run";          Content = $runScript      }
    [pscustomobject]@{ Name = "package.json"; Content = $packageJson    }
    [pscustomobject]@{ Name = "App.jsx";      Content = $solutionCode   }
    [pscustomobject]@{ Name = "App.test.js";  Content = $testCode       }
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

# ── Build request with time limits ────────────────────────────
$waitFlag = if ($Wait) { "true" } else { "false" }
$url      = $BaseUrl + "/submissions?base64_encoded=true&wait=" + $waitFlag

$body = [ordered]@{
    language_id      = 89
    additional_files = $b64Archive
    cpu_time_limit   = 15          # seconds
    wall_time_limit  = 20          # seconds
}
$bodyJson = $body | ConvertTo-Json -Compress

# ── Print request summary ─────────────────────────────────────
$b64Len = $b64Archive.Length
Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  JUDGE0 REQUEST (React test, language_id=89)"     -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Method  : POST"
Write-Host "  URL     : $url"
Write-Host "  Body (short):"
Write-Host "    language_id      = 89"
Write-Host "    additional_files = [base64 $b64Len chars]"
Write-Host "    cpu_time_limit   = 30"
Write-Host "    wall_time_limit  = 60"
Write-Host "  Zip entries: run, package.json, App.jsx, App.test.js"
Write-Host ""

# ── Send request with detailed error handling ─────────────────
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

try {
    $wc = [System.Net.WebClient]::new()
    $wc.Headers.Add("Content-Type", "application/json")
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $rawResponse = $wc.UploadString($url, "POST", $bodyJson)
    $sw.Stop()
    $resp = $rawResponse | ConvertFrom-Json

    $elapsed = $sw.ElapsedMilliseconds
    $statusId = $resp.status.id
    $statusDesc = $resp.status.description
    $passed = ($statusId -eq 3)
    $color = if ($passed) { "Green" } else { "Red" }
    $token = $resp.token
    $rtime = $resp.time
    $rmem = $resp.memory

    Write-Host "==================================================" -ForegroundColor Green
    Write-Host "  JUDGE0 RESPONSE (round-trip ${elapsed} ms)"        -ForegroundColor Green
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host "  token   : $token"
    Write-Host "  status  : [$statusId] $statusDesc" -ForegroundColor $color
    Write-Host "  time    : $rtime s"
    Write-Host "  memory  : $rmem KB"
    Write-Host "  passed  : $passed" -ForegroundColor $color

    # Decode and display base64 fields
    $stdout = Decode-Base64 $resp.stdout
    $stderr = Decode-Base64 $resp.stderr
    $compile_output = Decode-Base64 $resp.compile_output
    $message = Decode-Base64 $resp.message

    Write-Host ""
    Write-Host "  -- stdout --"
    if ($stdout) { Write-Host $stdout -ForegroundColor White }
    else { Write-Host "  (empty)" -ForegroundColor DarkGray }

    Write-Host "  -- stderr --"
    if ($stderr) { Write-Host $stderr -ForegroundColor Yellow }
    else { Write-Host "  (empty)" -ForegroundColor DarkGray }

    Write-Host "  -- compile_output --"
    if ($compile_output) { Write-Host $compile_output -ForegroundColor Yellow }
    else { Write-Host "  (empty)" -ForegroundColor DarkGray }

    Write-Host "  -- message --"
    if ($message) { Write-Host $message -ForegroundColor Yellow }
    else { Write-Host "  (empty)" -ForegroundColor DarkGray }

    Write-Host ""
    Write-Host "  -- raw JSON (original, still base64) --"
    $resp | ConvertTo-Json -Depth 5 | Write-Host -ForegroundColor DarkGray

    if ((-not $Wait) -and $token) {
        Write-Host ""
        Write-Host "  [async] Polling token $token ..." -ForegroundColor Cyan
        $terminalIds = @(3,4,5,6,7,8,9,10,11,12,13,14)
        for ($i = 0; $i -lt 20; $i++) {
            Start-Sleep -Milliseconds 500
            $pollUrl = $BaseUrl + "/submissions/" + $token + "?base64_encoded=true"
            $wc2 = [System.Net.WebClient]::new()
            $wc2.Headers.Add("Content-Type", "application/json")
            $rawPoll = $wc2.DownloadString($pollUrl)
            $poll = $rawPoll | ConvertFrom-Json
            $pid2 = $poll.status.id
            $pdesc = $poll.status.description
            Write-Host "  [poll $i] status=[$pid2] $pdesc"
            if ($terminalIds -contains $pid2) {
                # Decode fields for the final poll result
                $poll_stdout = Decode-Base64 $poll.stdout
                $poll_stderr = Decode-Base64 $poll.stderr
                $poll_compile = Decode-Base64 $poll.compile_output
                $poll_msg = Decode-Base64 $poll.message
                Write-Host "  -- Final decoded output --" -ForegroundColor Cyan
                if ($poll_stdout) { Write-Host $poll_stdout -ForegroundColor White }
                if ($poll_stderr) { Write-Host $poll_stderr -ForegroundColor Yellow }
                if ($poll_compile) { Write-Host $poll_compile -ForegroundColor Yellow }
                if ($poll_msg) { Write-Host $poll_msg -ForegroundColor Yellow }
                break
            }
        }
    }
} catch [System.Net.WebException] {
    # HTTP error (422, 400, 500, etc.)
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Red
    Write-Host "  JUDGE0 HTTP ERROR"                                 -ForegroundColor Red
    Write-Host "==================================================" -ForegroundColor Red

    $exResp = $_.Exception.Response
    if ($exResp -ne $null) {
        $statusCode = [int]$exResp.StatusCode
        Write-Host "  Status Code   : $statusCode ($($exResp.StatusDescription))" -ForegroundColor Red

        $stream = $exResp.GetResponseStream()
        $reader = [System.IO.StreamReader]::new($stream)
        $body2 = $reader.ReadToEnd()
        $reader.Dispose()

        Write-Host "  Response Body :" -ForegroundColor Yellow
        Write-Host $body2 -ForegroundColor White

        try {
            $errObj = $body2 | ConvertFrom-Json
            if ($errObj.message) {
                Write-Host "  Message       : $($errObj.message)" -ForegroundColor Yellow
            }
            if ($errObj.errors) {
                Write-Host "  Errors        : $($errObj.errors | ConvertTo-Json -Compress)" -ForegroundColor Yellow
            }
        } catch {
            # Not JSON – ignore
        }
    } else {
        Write-Host "  No response received from server." -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "  Full Exception:" -ForegroundColor DarkGray
    Write-Host $_.Exception.ToString() -ForegroundColor DarkGray
} catch {
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Red
    Write-Host "  UNEXPECTED ERROR"                                 -ForegroundColor Red
    Write-Host "==================================================" -ForegroundColor Red
    Write-Host $_.Exception.ToString() -ForegroundColor Red
}