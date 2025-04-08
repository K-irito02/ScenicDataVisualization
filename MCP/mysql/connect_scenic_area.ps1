 # 连接到 scenic_area 数据库
Write-Host "正在连接到 scenic_area 数据库..." -ForegroundColor Green
$config = @{
    mysqlHost = "localhost"
    mysqlPort = 3306
    mysqlUser = "root"
    mysqlPassword = "3143285505"
    mysqlDatabase = "scenic_area"
} | ConvertTo-Json -Compress

npx -y @smithery/cli@latest run mysql-mcp-server --client cursor --config $config