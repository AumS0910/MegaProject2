$url = "https://get.enterprisedb.com/postgresql/postgresql-16.1-1-windows-x64.exe"
$outFile = "postgresql_installer.exe"

Write-Host "Downloading PostgreSQL installer..."
Invoke-WebRequest -Uri $url -OutFile $outFile

Write-Host "Installing PostgreSQL..."
Start-Process -FilePath ".\$outFile" -ArgumentList "--mode unattended --unattendedmodeui minimal --superpassword kitcoek --servicename PostgreSQL --servicepassword kitcoek --serverport 5432" -Wait

Write-Host "Creating database..."
$env:PGPASSWORD = "kitcoek"
& "C:\Program Files\PostgreSQL\16\bin\createdb.exe" -h localhost -p 5432 -U postgres brochure_db

Write-Host "Installation complete!"
