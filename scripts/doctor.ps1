$ErrorActionPreference = "Stop"

Write-Output "=== Ableton MCP Doctor (Windows) ==="

function Test-CommandExists {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$remoteScriptSource = Join-Path $repoRoot "AbletonMCP_Remote_Script\__init__.py"
$abletonHost = $env:ABLETON_MCP_HOST
if (-not $abletonHost) { $abletonHost = "localhost" }

$port = 9877
if ($env:ABLETON_MCP_PORT) {
    $parsedPort = 0
    if ([int]::TryParse($env:ABLETON_MCP_PORT, [ref]$parsedPort)) {
        $port = $parsedPort
    } else {
        Write-Warning "ABLETON_MCP_PORT is set but invalid. Falling back to $port."
    }
}

Write-Output ""
Write-Output "Tools"
if (Test-CommandExists "uv") {
    Write-Output ("- uv: " + (uv --version))
} else {
    Write-Warning "- uv not found on PATH"
}

if (Test-CommandExists "uvx") {
    Write-Output ("- uvx: " + (uvx --version))
} else {
    Write-Warning "- uvx not found on PATH"
}

$pythonVersion = $null
foreach ($candidate in @("python", "py")) {
    $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($cmd) {
        $pythonVersion = & $cmd --version
        break
    }
}
if ($pythonVersion) {
    Write-Output "- Python: $pythonVersion"
} else {
    Write-Warning "- Python not detected on PATH (3.10+ required)"
}

Write-Output ""
Write-Output "Repository"
Write-Output "- Repo root: $repoRoot"
Write-Output "- Remote Script source: $remoteScriptSource"

Write-Output ""
Write-Output "Ableton Remote Script install locations to check:"
$targets = @(
    @{ Name = "User Remote Scripts"; Path = "$env:APPDATA\Ableton\Live*\Preferences\User Remote Scripts\AbletonMCP" },
    @{ Name = "ProgramData Remote Scripts"; Path = "C:\ProgramData\Ableton\Live*\Resources\MIDI Remote Scripts\AbletonMCP" }
)

foreach ($target in $targets) {
    $found = Get-ChildItem -Path $target.Path -Directory -ErrorAction SilentlyContinue
    if ($found) {
        foreach ($dir in $found) {
            $status = if (Test-Path (Join-Path $dir.FullName "__init__.py")) { "contains __init__.py" } else { "missing __init__.py" }
            Write-Output ("- {0}: {1} ({2})" -f $target.Name, $dir.FullName, $status)
        }
    } else {
        Write-Output ("- {0}: not found (expected pattern: {1})" -f $target.Name, $target.Path)
    }
}

Write-Output ""
Write-Output "Port check (Remote Script socket)"
try {
    $portResult = Test-NetConnection -ComputerName $abletonHost -Port $port -WarningAction SilentlyContinue
    if ($portResult.TcpTestSucceeded) {
        Write-Output ("- {0}:{1} is accepting TCP connections" -f $abletonHost, $port)
    } else {
        Write-Output ("- {0}:{1} is not open yet (start Ableton with the AbletonMCP control surface)" -f $abletonHost, $port)
    }
} catch {
    Write-Warning "- Unable to run Test-NetConnection: $_"
}

Write-Output ""
Write-Output "Next steps"
Write-Output ("1) Copy Remote Script: copy '{0}' into one of the paths above as 'AbletonMCP\\__init__.py'" -f $remoteScriptSource)
Write-Output "2) In Ableton Live > Preferences > Link, Tempo & MIDI, set Control Surface to 'AbletonMCP' and Input/Output to 'None'"
Write-Output ("3) Start the MCP server from this repo: uvx --from `"$repoRoot`" ableton-mcp")
Write-Output "4) Reload the Codex/Claude MCP config so it uses the same command"
Write-Output "5) Trigger a tool (e.g., 'get_session_info') to confirm the connection"
