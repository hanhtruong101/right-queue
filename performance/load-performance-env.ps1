$ErrorActionPreference = "Stop"

$environmentFile = Join-Path $PSScriptRoot ".env"

if (-not (Test-Path -LiteralPath $environmentFile)) {
    throw "The performance/.env file was not found."
}

foreach ($line in Get-Content -LiteralPath $environmentFile) {
    $line = $line.Trim()

    if ([string]::IsNullOrWhiteSpace($line) -or $line.StartsWith("#")) {
        continue
    }

    $name, $value = $line.Split("=", 2)

    [Environment]::SetEnvironmentVariable(
        $name.Trim(),
        $value.Trim(),
        "Process"
    )
}

$requiredVariables = @(
    "DATABASE_URL",
    "LOAD_TEST_USERNAME",
    "LOAD_TEST_PASSWORD",
    "ORGANIZATION_SLUG",
    "LOCUST_HOST"
)

foreach ($name in $requiredVariables) {
    if ([string]::IsNullOrWhiteSpace(
        [Environment]::GetEnvironmentVariable($name, "Process")
    )) {
        throw "Missing variable in performance/.env: $name"
    }
}

if ($env:DATABASE_URL -notmatch "/rightqueue_performance(?:\?|$)") {
    throw "The configured database is not rightqueue_performance."
}

Write-Host "Performance environment loaded."
Write-Host "Database: rightqueue_performance"
Write-Host "Test user: $env:LOAD_TEST_USERNAME"
Write-Host "Organization: $env:ORGANIZATION_SLUG"
Write-Host "Target: $env:LOCUST_HOST"
Write-Host "Passwords are loaded but are not displayed."