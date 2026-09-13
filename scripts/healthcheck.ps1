$ErrorActionPreference = 'Stop'

$edge = Invoke-RestMethod 'http://127.0.0.1:8080/health'
$agent = Invoke-RestMethod 'http://127.0.0.1:8000/ready'

if ($edge.status -ne 'ok') { throw 'edge health check failed' }
if ($agent.status -ne 'ready') { throw 'agent readiness check failed' }

Write-Host "edge=$($edge.status) agent=$($agent.status) provider=$($agent.provider)"
