# ==============================================================
#  test_html_css_js_in_judge0.ps1
#  Sends a language_id=89 (Multi-file Program) submission to
#  your Judge0 instance and prints the full request + response.
# ==============================================================

# ------------------- CONFIGURATION (edit here) -------------------
# $BaseUrl = "https://ce.judge0.com"      # Judge0 API endpoint
$BaseUrl = "http://10.10.142.96:2360"   # Judge0 API endpoint (local testing)
$Wait    = $false                        # $true = synchronous, $false = async + poll
$PollIntervalSeconds = 1                 # polling interval (ignored if $Wait = $true)
$MaxPollAttempts     = 20                # max polling attempts (ignored if $Wait = $true)
# -----------------------------------------------------------------

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Helper: decode base64 string if valid, otherwise return original
function Decode-Base64IfNeeded {
    param([string]$InputString)
    if ([string]::IsNullOrEmpty($InputString)) {
        return $InputString
    }
    # Judge0 returns base64 when base64_encoded=true
    # Try to decode; if it fails, assume it's plain text
    try {
        $bytes = [System.Convert]::FromBase64String($InputString)
        return [System.Text.Encoding]::UTF8.GetString($bytes)
    } catch {
        # Not base64 or malformed – return original
        return $InputString
    }
}

# Helper: remove carriage returns for clean console output
function Remove-CarriageReturns {
    param([string]$InputString)
    if ($InputString) {
        return $InputString -replace "`r", ""
    }
    return $InputString
}

# ── 1. Embedded file contents ───────────────────────────────────
$indexHtml = @'
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="styles.css">
    <title>Test Page</title>
</head>
<body>
    <h1 id="greeting">Hello</h1>
    <button id="btn">Click me</button>
    <script src="script.js"></script>
</body>
</html>
'@

$stylesCss = @'
body {
    font-family: Arial, sans-serif;
    text-align: center;
    margin-top: 50px;
}
h1 {
    color: #2c3e50;
}
button {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
}
button:hover {
    background-color: #2980b9;
}
'@

$scriptJs = @'
document.getElementById('btn').addEventListener('click', function() {
    const heading = document.getElementById('greeting');
    heading.textContent = 'Welcome, Judge0!';
    heading.style.color = '#e74c3c';
});
'@

$testJs = @'
const fs = require('fs');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;
const assert = require('assert');

// Load files
const html = fs.readFileSync('index.html', 'utf8');
const css = fs.readFileSync('styles.css', 'utf8');
const jsCode = fs.readFileSync('script.js', 'utf8');

// Create DOM from HTML
const dom = new JSDOM(html, {
    runScripts: 'dangerously',
    resources: 'usable'
});

// Inject CSS (optional - for style testing if needed)
const styleElement = dom.window.document.createElement('style');
styleElement.textContent = css;
dom.window.document.head.appendChild(styleElement);

// Inject and execute the script
const scriptElement = dom.window.document.createElement('script');
scriptElement.textContent = jsCode;
dom.window.document.body.appendChild(scriptElement);

// Short delay to allow event listeners to attach
setTimeout(() => {
    try {
        // Test initial state
        const heading = dom.window.document.getElementById('greeting');
        assert.strictEqual(heading.textContent, 'Hello', 'Initial heading text is not "Hello"');

        // Simulate click on button
        const button = dom.window.document.getElementById('btn');
        button.click();

        // Test updated state
        assert.strictEqual(heading.textContent, 'Welcome, Judge0!', 'Heading did not update after click');

        console.log('All tests passed!');
        process.exit(0);
    } catch (err) {
        console.error('Test failed:', err.message);
        process.exit(1);
    }
}, 100);
'@

$runScript = @'
#!/usr/bin/env bash
set -e
export NODE_PATH=$(npm root -g)
node test.js
'@

# ── 2. Build in-memory ZIP → base64 ────────────────────────────
Add-Type -AssemblyName System.IO.Compression

$memStream = [System.IO.MemoryStream]::new()
$zipArchive = [System.IO.Compression.ZipArchive]::new(
    $memStream,
    [System.IO.Compression.ZipArchiveMode]::Create,
    $true
)

foreach ($item in @(
    [pscustomobject]@{ Name = "run";          Content = $runScript    }
    [pscustomobject]@{ Name = "index.html";   Content = $indexHtml    }
    [pscustomobject]@{ Name = "styles.css";   Content = $stylesCss    }
    [pscustomobject]@{ Name = "script.js";    Content = $scriptJs     }
    [pscustomobject]@{ Name = "test.js";      Content = $testJs       }
)) {
    $entry = $zipArchive.CreateEntry($item.Name)
    $writer = [System.IO.StreamWriter]::new($entry.Open())
    $contentLF = $item.Content -replace "`r`n", "`n"
    $writer.Write($contentLF)
    $writer.Dispose()
}
$zipArchive.Dispose()

$zipBytes = $memStream.ToArray()
$memStream.Dispose()
$b64Archive = [Convert]::ToBase64String($zipBytes)

# ── 3. Build URL + JSON body ───────────────────────────────────
$waitFlag   = if ($Wait) { "true" } else { "false" }
$url        = "$BaseUrl/submissions?base64_encoded=true&wait=$waitFlag"

$body = @{
    language_id      = 89
    additional_files = $b64Archive
} | ConvertTo-Json -Compress

# ── 4. Print outgoing request info ─────────────────────────────
Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  JUDGE0 REQUEST  (language_id = 89)"              -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Method  : POST"
Write-Host "  URL     : $url"
Write-Host "  Headers : Content-Type: application/json"
Write-Host "  Body:"
Write-Host "    language_id      = 89"
Write-Host "    additional_files = [base64 $($b64Archive.Length) chars]"
Write-Host "  Zip entries:"
Write-Host "    run          ($($runScript.Length) bytes)"
Write-Host "    index.html   ($($indexHtml.Length) bytes)"
Write-Host "    styles.css   ($($stylesCss.Length) bytes)"
Write-Host "    script.js    ($($scriptJs.Length) bytes)"
Write-Host "    test.js      ($($testJs.Length) bytes)"
Write-Host ""

# ── 5. Send request ──────────────────────
try {
    $response = Invoke-RestMethod -Uri $url -Method Post -Body $body -ContentType "application/json"
}
catch {
    Write-Host "==================================================" -ForegroundColor Red
    Write-Host "  SUBMISSION FAILED"                               -ForegroundColor Red
    Write-Host "==================================================" -ForegroundColor Red
    Write-Host $_.Exception.Message
    if ($_.Exception.Response) {
        $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
        $errorBody = $reader.ReadToEnd() -replace "`n", "`n  "
        Write-Host "Response body:`n  $errorBody" -ForegroundColor Red
    }
    exit 1
}

# ── 6. Handle synchronous vs asynchronous ─────────────────────
if ($Wait) {
    $submission = $response
}
else {
    $token = $response.token
    Write-Host "[async] Got token: $token - polling every ${PollIntervalSeconds}s (max $MaxPollAttempts attempts)" -ForegroundColor Cyan

    $submission = $null
    $terminalStates = @(3,4,5,6,7,8,9,10,11,12,13,14)
    for ($i = 0; $i -lt $MaxPollAttempts; $i++) {
        Start-Sleep -Seconds $PollIntervalSeconds
        $pollUrl = "$BaseUrl/submissions/$($token)?base64_encoded=true"
        try {
            $poll = Invoke-RestMethod -Uri $pollUrl -Method Get
        }
        catch {
            Write-Host "Polling error: $($_.Exception.Message)" -ForegroundColor Yellow
            continue
        }
        $statusId = $poll.status.id
        $statusDesc = $poll.status.description
        Write-Host "  poll $($i+1): status [$statusId] $statusDesc"

        if ($terminalStates -contains $statusId) {
            $submission = $poll
            break
        }
    }
    if (-not $submission) {
        Write-Host "Polling timed out after $MaxPollAttempts attempts." -ForegroundColor Red
        exit 1
    }
}

# ── 7. Decode and display final result ─────────────────────────
$statusId   = $submission.status.id
$statusDesc = $submission.status.description
$passed     = ($statusId -eq 3)
$color      = if ($passed) { "Green" } else { "Red" }

Write-Host "`n==================================================" -ForegroundColor Green
Write-Host "  JUDGE0 RESULT"                                     -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host "  status  : [$statusId] $statusDesc" -ForegroundColor $color
Write-Host "  time    : $($submission.time) s"
Write-Host "  memory  : $($submission.memory) KB"
Write-Host "  token   : $($submission.token)"

Write-Host "`n  -- stdout --"
if ($submission.stdout) {
    $decoded = Decode-Base64IfNeeded $submission.stdout
    $clean = Remove-CarriageReturns $decoded
    Write-Host $clean -ForegroundColor White
} else {
    Write-Host "  (empty)" -ForegroundColor DarkGray
}

Write-Host "`n  -- stderr --"
if ($submission.stderr) {
    $decoded = Decode-Base64IfNeeded $submission.stderr
    $clean = Remove-CarriageReturns $decoded
    Write-Host $clean -ForegroundColor Yellow
} else {
    Write-Host "  (empty)" -ForegroundColor DarkGray
}

Write-Host "`n  -- compile_output --"
if ($submission.compile_output) {
    $decoded = Decode-Base64IfNeeded $submission.compile_output
    $clean = Remove-CarriageReturns $decoded
    Write-Host $clean -ForegroundColor Yellow
} else {
    Write-Host "  (empty)" -ForegroundColor DarkGray
}

Write-Host "`n  -- message --"
if ($submission.message) {
    $decoded = Decode-Base64IfNeeded $submission.message
    $clean = Remove-CarriageReturns $decoded
    Write-Host $clean -ForegroundColor Yellow
} else {
    Write-Host "  (empty)" -ForegroundColor DarkGray
}

# Raw JSON with decoded fields
Write-Host "`n  -- raw JSON (decoded) --"
$decodedForJson = [PSCustomObject]@{
    token          = $submission.token
    status         = $submission.status
    time           = $submission.time
    memory         = $submission.memory
    stdout         = Decode-Base64IfNeeded $submission.stdout
    stderr         = Decode-Base64IfNeeded $submission.stderr
    compile_output = Decode-Base64IfNeeded $submission.compile_output
    message        = Decode-Base64IfNeeded $submission.message
}
$decodedForJson | ConvertTo-Json -Depth 5 | Write-Host -ForegroundColor DarkGray

if ($passed) {
    Write-Host "`nAll tests passed!" -ForegroundColor Green
} else {
    Write-Host "`nSubmission failed (status: $statusDesc)" -ForegroundColor Red
    exit 1
}