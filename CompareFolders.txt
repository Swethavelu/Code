# CompareFolders.ps1

# Load configuration
. .\config.ps1

# Function to compare folders
function Compare-Folders {
    param (
        [string]$environment1,
        [string]$environment2
    )

    $folderPath1 = $environments[$environment1].FolderPath
    $folderPath2 = $environments[$environment2].FolderPath

    $results = Compare-Object (Get-ChildItem -Path $folderPath1 -Recurse | Select-Object FullName, Length, LastWriteTime) `
                               (Get-ChildItem -Path $folderPath2 -Recurse | Select-Object FullName, Length, LastWriteTime) `
                               -Property FullName, Length, LastWriteTime -PassThru

    $results | Export-Csv -Path $OutputPath -NoTypeInformation
}

# Compare folders
Compare-Folders -environment1 "PreProd" -environment2 "Prod"
