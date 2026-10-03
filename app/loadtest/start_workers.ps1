param(
    [int]$Workers = 1
)

$ProjectRoot = "D:\AgentMesh"

Set-Location $ProjectRoot

$Python = "$ProjectRoot\venv\Scripts\python.exe"

Write-Host ""
Write-Host "============================================"
Write-Host "AgentMesh Load Test Workers"
Write-Host "============================================"
Write-Host "Workers: $Workers"
Write-Host ""

for ($i = 1; $i -le $Workers; $i++) {

    Write-Host "Starting worker $i..."

    $command = @"
`$env:AGENTMESH_LOAD_TEST='true'
`$env:AGENTMESH_LOAD_TEST_DELAY_MS='20'
& '$Python' -m app.worker
"@

    Start-Process `
        powershell.exe `
        -ArgumentList "-NoExit", "-Command", $command `
        -WorkingDirectory $ProjectRoot
}

Write-Host ""
Write-Host "$Workers worker process(es) started."
Write-Host ""