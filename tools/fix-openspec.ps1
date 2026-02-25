param(
    [Parameter(Mandatory=$true)]
    [string]$Path
)

$lines = Get-Content -Path $Path
$lines = $lines | ForEach-Object {
    if ($_ -match '@\{Name=' -and $_.TrimEnd().EndsWith(',')) {
        $_.TrimEnd().TrimEnd(',')
    } else {
        $_
    }
}
Set-Content -Path $Path -Value $lines
