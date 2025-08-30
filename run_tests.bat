@echo off
echo ================================================
echo WhisperWriter - Regex Engine Test Suite Runner
echo ================================================
echo.

cd /d "%~dp0"

echo [1/4] Running basic regex engine tests...
echo ----------------------------------------
python tests\test_regex_engine.py
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Basic regex tests failed!
    pause
    exit /b 1
)
echo [PASS] Basic regex tests completed successfully
echo.

echo [2/4] Running advanced regex feature tests...
echo ----------------------------------------------
python tests\test_regex_advanced.py
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Advanced regex tests failed!
    pause
    exit /b 1
)
echo [PASS] Advanced regex tests completed successfully
echo.

echo [3/4] Running text replacement tests...
echo --------------------------------------
python tests\test_text_replacement.py
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Text replacement tests failed!
    pause
    exit /b 1
)
echo [PASS] Text replacement tests completed successfully
echo.

echo [4/4] Running configuration management tests...
echo -----------------------------------------------
python tests\test_regex_config.py
if %ERRORLEVEL% neq 0 (
    echo [FAIL] Configuration tests failed!
    pause
    exit /b 1
)
echo [PASS] Configuration tests completed successfully
echo.

echo ================================================
echo [SUCCESS] ALL TESTS PASSED!
echo ================================================
echo Total: 92 tests across 4 files
echo - test_regex_engine.py: 23 tests
echo - test_regex_advanced.py: 25 tests  
echo - test_text_replacement.py: 19 tests
echo - test_regex_config.py: 25 tests
echo.
echo The regex system with UI integration is working perfectly!
echo ================================================
pause