# ==============================================================
#  test_angular_in_judge0.ps1
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

function Decode-Base64IfNeeded {
    param([string]$InputString)
    if ([string]::IsNullOrEmpty($InputString)) {
        return $InputString
    }
    try {
        $bytes = [System.Convert]::FromBase64String($InputString)
        return [System.Text.Encoding]::UTF8.GetString($bytes)
    } catch {
        return $InputString
    }
}

function Remove-CarriageReturns {
    param([string]$InputString)
    if ($InputString) {
        return $InputString -replace "`r", ""
    }
    return $InputString
}

# ── 1. Embedded file contents ───────────────────────────────────
$packageJson = @'
{
  "name": "angular-judge0-test",
  "private": true,
  "scripts": {
    "test": "jest"
  },
  "devDependencies": {
    "@angular/common": "~16.2.0",
    "@angular/compiler": "~16.2.0",
    "@angular/compiler-cli": "~16.2.0",
    "@angular/core": "~16.2.0",
    "@angular/platform-browser": "~16.2.0",
    "@angular/platform-browser-dynamic": "~16.2.0",
    "@types/jest": "^29.5.0",
    "jest": "^29.0.0",
    "rxjs": "^7.8.0",
    "ts-jest": "^29.1.0",
    "typescript": "^5.4.0",
    "zone.js": "^0.13.0"
  }
}
'@

$tsConfig = @'
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "node",
    "importHelpers": true,
    "allowSyntheticDefaultImports": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "strict": false,
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true,
    "types": ["jest", "node"],
    "lib": ["ES2020", "DOM"]
  },
  "exclude": ["node_modules"]
}
'@

$jestConfig = @'
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  transform: {
    '^.+\\.tsx?$': 'ts-jest'
  },
  globals: {
    'ts-jest': {
      tsconfig: 'tsconfig.json'
    }
  },
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  testRegex: '(/__tests__/.*|(\\.|/)(test|spec))\\.tsx?$'
};
'@

$appComponent = @'
import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: '<h1>{{ title }}</h1>'
})
export class AppComponent {
  title = 'Hello Angular!';
}
'@

$testCode = @'
import 'zone.js';
import 'zone.js/testing';
import { TestBed } from '@angular/core/testing';
import { BrowserDynamicTestingModule, platformBrowserDynamicTesting } from '@angular/platform-browser-dynamic/testing';
import { AppComponent } from './app.component';

beforeAll(() => {
  TestBed.initTestEnvironment(BrowserDynamicTestingModule, platformBrowserDynamicTesting());
});

describe('AppComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [AppComponent]
    }).compileComponents();
  });

  it('renders hello angular heading', () => {
    const fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Hello Angular!');
  });

  it('has a title property', () => {
    const fixture = TestBed.createComponent(AppComponent);
    expect(fixture.componentInstance.title).toBe('Hello Angular!');
  });
});
'@

$runScript = @'
#!/usr/bin/env bash
set -e
export NODE_PATH=$(npm root -g)
npm install --silent
npx -y jest --runInBand
'@

# ── 2. Build in-memory ZIP → base64 ────────────────────────────
Add-Type -AssemblyName System.IO.Compression

$memStream = [System.IO.MemoryStream]::new()
$zipArchive = [System.IO.Compression.ZipArchive]::new(
    $memStream,
    [System.IO.Compression.ZipArchiveMode]::Create,
    $true
)

$files = @(
    [pscustomobject]@{ Name = 'run'; Content = $runScript }
    [pscustomobject]@{ Name = 'package.json'; Content = $packageJson }
    [pscustomobject]@{ Name = 'tsconfig.json'; Content = $tsConfig }
    [pscustomobject]@{ Name = 'jest.config.cjs'; Content = $jestConfig }
    [pscustomobject]@{ Name = 'src/app.component.ts'; Content = $appComponent }
    [pscustomobject]@{ Name = 'src/app.component.spec.ts'; Content = $testCode }
)

foreach ($item in $files) {
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
$waitFlag   = if ($Wait) { 'true' } else { 'false' }
$url        = "$BaseUrl/submissions?base64_encoded=true&wait=$waitFlag"

$body = @{
    language_id      = 89
    additional_files = $b64Archive
} | ConvertTo-Json -Compress

# ── 4. Print outgoing request info ─────────────────────────────
$b64Len   = $b64Archive.Length
$runLen   = $runScript.Length
$pkgLen   = $packageJson.Length
$tsLen    = $tsConfig.Length
$jestLen  = $jestConfig.Length
$compLen  = $appComponent.Length
$testLen  = $testCode.Length

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
Write-Host "    run                     ($runLen bytes)   <- install + test"
Write-Host "    package.json            ($pkgLen bytes)"
Write-Host "    tsconfig.json           ($tsLen bytes)"
Write-Host "    jest.config.cjs         ($jestLen bytes)"
Write-Host "    src/app.component.ts      ($compLen bytes)"
Write-Host "    src/app.component.spec.ts ($testLen bytes)"
Write-Host ""

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
