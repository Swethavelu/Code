# GenerateReport.ps1

# Load configuration
. .\config.ps1

# Function to generate HTML report
function Generate-HTMLReport {
    param (
        [string]$outputPath,
        [string]$htmlReportPath
    )

    $htmlContent = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Folder Comparison Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <h2>Folder Comparison Report</h2>
"@

    $results = Get-Content $outputPath | ConvertFrom-Csv

    $htmlContent += @"
    <h3>Comparison Results</h3>
    <table>
        <thead>
            <tr>
                <th>File Path</th>
                <th>Size (Bytes)</th>
                <th>Last Write Time (UTC)</th>
                <th>Comparison Result</th>
            </tr>
        </thead>
        <tbody>
"@

    foreach ($result in $results) {
        $htmlContent += @"
            <tr>
                <td>$($result.FullName)</td>
                <td>$($result.Length)</td>
                <td>$($result.LastWriteTime.ToUniversalTime())</td>
                <td>$($result.SideIndicator)</td>
            </tr>
"@
    }

    $htmlContent += @"
        </tbody>
    </table>
</body>
</html>
"@

    $htmlContent | Out-File $htmlReportPath
}

# Generate HTML report
Generate-HTMLReport -outputPath $OutputPath -htmlReportPath $HTMLReportPath

# Open the HTML report in the default web browser
Start-Process $HTMLReportPath
