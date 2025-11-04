@echo off
REM =========================================================================
REM run_experiment.bat
REM =========================================================================
REM Automated experiment runner for SAGIN network simulation (Windows)
REM =========================================================================

REM Configuration
set NUM_SLOTS=10
set SLOT_DURATION=60
set ALGORITHM=KMPP

REM Directories (relative to script location)
cd /d %~dp0\..
set PROJECT_ROOT=%CD%
set MATLAB_DIR=%PROJECT_ROOT%\matlab_export
set TOPO_DIR=%PROJECT_ROOT%\topology
set ORCHESTRATOR_DIR=%PROJECT_ROOT%\orchestrator
set VISUALIZATION_DIR=%PROJECT_ROOT%\visualization
set PLOTS_DIR=%PROJECT_ROOT%\plots

echo =========================================================================
echo SAGIN Network Simulation Experiment Runner
echo =========================================================================

REM Step 1: Check for topology data
echo.
echo Step 1: Checking for topology data...
echo ----------------------------------------------------------------------

set EXPORT_FILE=%TOPO_DIR%\mininet_topology_data.json
if not exist "%EXPORT_FILE%" (
    echo Warning: Topology export file not found: %EXPORT_FILE%
    echo Please run the MATLAB export script first.
    echo You can run it from MATLAB with:
    echo   cd matlab_export
    echo   export_to_mininet('%ALGORITHM%', %NUM_SLOTS%)
    echo.
    set /p continue="Continue anyway? (y/n): "
    if /i not "%continue%"=="y" exit /b 1
) else (
    echo Topology data found: %EXPORT_FILE%
)

REM Step 2: Check dependencies
echo.
echo Step 2: Checking dependencies...
echo ----------------------------------------------------------------------

where python >nul 2>nul
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.
    exit /b 1
)
echo Python found

where mn >nul 2>nul
if errorlevel 1 (
    echo Error: Mininet not found. Please install Mininet.
    exit /b 1
)
echo Mininet found

where ryu-manager >nul 2>nul
if errorlevel 1 (
    echo Error: Ryu controller not found. Please install Ryu.
    exit /b 1
)
echo Ryu found

echo All dependencies found.

REM Step 3: Create output directories
echo.
echo Step 3: Creating output directories...
echo ----------------------------------------------------------------------

if not exist "%PLOTS_DIR%" mkdir "%PLOTS_DIR%"
echo Output directory: %PLOTS_DIR%

REM Step 4: Run simulation
echo.
echo Step 4: Running Mininet simulation...
echo ----------------------------------------------------------------------

cd %ORCHESTRATOR_DIR%
python orchestrator.py --slots %NUM_SLOTS% --duration %SLOT_DURATION%

if errorlevel 1 (
    echo Error during simulation
    exit /b 1
)

echo Simulation complete.

REM Step 5: Generate visualizations
echo.
echo Step 5: Generating visualizations...
echo ----------------------------------------------------------------------

cd %VISUALIZATION_DIR%
python visualize_results.py --all --output "%PLOTS_DIR%"

if errorlevel 1 (
    echo Error during visualization
    exit /b 1
)

echo Visualizations complete.

REM Step 6: Summary
echo.
echo =========================================================================
echo Experiment Complete!
echo =========================================================================
echo.
echo Results:
echo   - Topology data: %EXPORT_FILE%
echo   - Simulation metrics: %ORCHESTRATOR_DIR%\simulation_metrics.json
echo   - Visualizations: %PLOTS_DIR%\
echo.
dir "%PLOTS_DIR%\*.png" /b
echo.
echo =========================================================================

pause

