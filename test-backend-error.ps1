# Test backend errors
Write-Host "Testing backend API errors..."

# Get JWT token
$tokenUrl = "http://localhost:8000/api/token/"
$credentials = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

try {
    Write-Host "Getting JWT token..."
    $tokenResponse = Invoke-RestMethod -Uri $tokenUrl -Method Post -Body $credentials -ContentType "application/json" -TimeoutSec 5
    $token = $tokenResponse.access
    Write-Host "Token obtained successfully" -ForegroundColor Green
} catch {
    Write-Host "Failed to get token: $_" -ForegroundColor Red
    Write-Host "Response status: $($_.Exception.Response.StatusCode.value__)"
    Write-Host "Response body: $($_.ErrorDetails.Message)"
    exit 1
}

# Try to create a client
$clientUrl = "http://localhost:8000/api/clientes/"
$clientData = @{
    rut = "12345678"
    digito_verificador = "9"
    nombre_cliente = "Test Client"
    ciudad = "Test City"
    direccion = "Test Address"
    telefono = "123456789"
    descuento_aplicado = 5
} | ConvertTo-Json

$headers = @{
    Authorization = "Bearer $token"
    "Content-Type" = "application/json"
}

try {
    Write-Host "Attempting to create client..."
    $clientResponse = Invoke-RestMethod -Uri $clientUrl -Method Post -Body $clientData -Headers $headers -TimeoutSec 5
    Write-Host "Client created successfully!" -ForegroundColor Green
    Write-Host "Client ID: $($clientResponse.id_cliente)"
} catch {
    Write-Host "Failed to create client: $_" -ForegroundColor Red
    Write-Host "Status code: $($_.Exception.Response.StatusCode.value__)"
    Write-Host "Status description: $($_.Exception.Response.StatusDescription)"
    Write-Host "Error details: $($_.ErrorDetails.Message)"
    
    # Try to read the response stream
    try {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $reader.BaseStream.Position = 0
        $reader.DiscardBufferedData()
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response body: $responseBody"
    } catch {
        Write-Host "Could not read response body"
    }
}