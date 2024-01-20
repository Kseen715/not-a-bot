
$flag_is_in_venv = $false
# Check if venv is active
if ($env:VIRTUAL_ENV) {
    # Deactivate venv
    $flag_is_in_venv = $true <#
    #> && (Write-Host "Deactivating venv" -ForegroundColor Cyan) <#
    #> && deactivate && <#
    #> (Write-Host "venv deactivated" <#
    #> -ForegroundColor Cyan) <#
    #> || (Write-Error "venv deactivation failed")
}

# Remove old venv folder
$delete_executed = $false
if (Test-Path venv) {
    while (-not $delete_executed) {
        try {
            (Remove-Item -Path venv -Recurse -Force) <#
            #> && (Write-Host "Old venv folder removed" -ForegroundColor Cyan) 
            $delete_executed = $true
        } catch {
            Write-Host "Waiting for venv to deactivate..." <#
            #> -ForegroundColor Cyan
            Start-Sleep -s 2
        }
    }
} else {
    (Write-Host "No old venv folder found, creating one..." <#
    #> -ForegroundColor Cyan)
} <#

Create new venv
#> (Write-Host "Creating venv..." -ForegroundColor Cyan) <#
#> && (python -m venv venv) <#
#> && (Write-Host "venv created" -ForegroundColor Cyan) <#
#> || (Write-Error "venv creation failed") <#

Activate venv
#> && (Write-Host "Activating venv..." -ForegroundColor Cyan <#
#> && (venv\Scripts\activate) <#
#> && (Write-Host "venv activated" -ForegroundColor Cyan) <#
#> || (Write-Error "venv activation failed") <#

Upgrade pip
#> && (Write-Host "Upgrading pip..." -ForegroundColor Cyan) <#
#> && ((curl -s https://bootstrap.pypa.io/get-pip.py -o get-pip.py) > $null) <#
#> && ((python get-pip.py) > $null) <#
#> && (Write-Host "pip upgraded" -ForegroundColor Cyan) <#
#> || (Write-Error "pip upgrade failed") <#

Clean up
#> && (Write-Host "Cleaning up..." -ForegroundColor Cyan) <#
#> && (Remove-Item get-pip.py) <#
#> && (Write-Host "Clean up done" -ForegroundColor Cyan) <#
#> || (Write-Error "Clean up failed") <#

Install requirements
#> && (Write-Host "Installing requirements..." -ForegroundColor Cyan) <#
#> && (pip install -r requirements.txt --no-cache-dir --quiet) <#
#> && Write-Host "Requirements installed" -ForegroundColor Cyan) <#
#> || (Write-Error "Requirements installation failed")