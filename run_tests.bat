@echo off
echo ================================================
echo WhisperWriter - Regex Engine Test Suite Runner
echo ================================================
echo.

cd /d "%~dp0"

echo [1/3] Running basic regex engine tests...
echo ----------------------------------------
python tests\test_regex_engine.py
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Basic regex tests failed!
    pause
    exit /b 1
)
echo [PASS] Basic regex tests completed successfully
echo.

echo [2/3] Running advanced regex feature tests...
echo ----------------------------------------------
python tests\test_regex_advanced.py
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Advanced regex tests failed!
    pause
    exit /b 1
)
echo [PASS] Advanced regex tests completed successfully
echo.

echo [3/3] Running text replacement tests...
echo --------------------------------------
python tests\test_text_replacement.py
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Text replacement tests failed!
    pause
    exit /b 1
)
echo [PASS] Text replacement tests completed successfully
echo.

echo ================================================
echo [SUCCESS] ALL TESTS PASSED!
echo ================================================
echo Total: 67 tests across 3 files
echo - test_regex_engine.py: 23 tests
echo - test_regex_advanced.py: 25 tests  
echo - test_text_replacement.py: 19 tests
echo.
echo The regex engine is working perfectly!
echo ================================================
pause