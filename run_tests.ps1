# WhisperWriter - Regex Engine Test Suite Runner
# PowerShell version for better error handling and colors

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "WhisperWriter - Regex Engine Test Suite Runner" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

$testsPassed = 0
$totalTests = 3

# Function to run a test file
function Run-Test {
    param(
        [string]$TestFile,
        [string]$Description,
        [int]$TestNumber,
        [int]$ExpectedTests
    )
    
    Write-Host "[$TestNumber/3] Running $Description..." -ForegroundColor Yellow
    Write-Host ("-" * 50) -ForegroundColor Gray
    
    try {
        $result = python "tests\$TestFile" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[PASS] $Description completed successfully ($ExpectedTests tests)" -ForegroundColor Green
            return $true
        } else {
            Write-Host "[FAIL] $Description failed!" -ForegroundColor Red
            Write-Host "Error output:" -ForegroundColor Red
            Write-Host $result -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "[ERROR] Failed to run $TestFile" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        return $false
    }
    finally {
        Write-Host ""
    }
}

# Run all test files
$tests = @(
    @{File="test_regex_engine.py"; Description="basic regex engine tests"; Count=23},
    @{File="test_regex_advanced.py"; Description="advanced regex feature tests"; Count=25},
    @{File="test_text_replacement.py"; Description="text replacement tests"; Count=19}
)

foreach ($i in 0..($tests.Count-1)) {
    $test = $tests[$i]
    if (Run-Test -TestFile $test.File -Description $test.Description -TestNumber ($i+1) -ExpectedTests $test.Count) {
        $testsPassed++
    } else {
        Write-Host ""
        Write-Host "================================================" -ForegroundColor Red
        Write-Host "[FAILURE] Test suite stopped due to failures" -ForegroundColor Red
        Write-Host "================================================" -ForegroundColor Red
        Write-Host "Please check the error messages above and fix any issues." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Success summary
if ($testsPassed -eq $totalTests) {
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "[SUCCESS] ALL TESTS PASSED!" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "Total: 67 tests across 3 files" -ForegroundColor White
    Write-Host "- test_regex_engine.py: 23 tests" -ForegroundColor White
    Write-Host "- test_regex_advanced.py: 25 tests" -ForegroundColor White
    Write-Host "- test_text_replacement.py: 19 tests" -ForegroundColor White
    Write-Host ""
    Write-Host "The regex engine is working perfectly!" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
} else {
    Write-Host "================================================" -ForegroundColor Red
    Write-Host "[PARTIAL] Only $testsPassed out of $totalTests test files passed" -ForegroundColor Red
    Write-Host "================================================" -ForegroundColor Red
}

Read-Host "Press Enter to exit"