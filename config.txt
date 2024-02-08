# config.ps1

$environments = @{
    PreProd = @{
        FolderPath = "C:\Path\to\PreProd\ServiceFolder"
    }
    Prod = @{
        FolderPath = "C:\Path\to\Prod\ServiceFolder"
    }
}

$OutputPath = "C:\Path\to\output.txt"
$HTMLReportPath = "C:\Path\to\ComparisonReport.html"
