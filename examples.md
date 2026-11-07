# Сценарии проверки

Запустите сервер по инструкции README. Выполните подготовку в другом окне PowerShell. Функция показывает статус и тело ответа, в том числе при HTTP 400 в Windows PowerShell и PowerShell 7.

```powershell
function Send-LeadTest([string]$Json) {
    try {
        $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/lead' -Method Post -ContentType 'application/json; charset=utf-8' -Body ([System.Text.Encoding]::UTF8.GetBytes($Json)) -UseBasicParsing
        Write-Host "HTTP $($r.StatusCode)"
        $r.Content
    } catch {
        if (-not $_.Exception.Response) { throw }
        Write-Host "HTTP $([int]$_.Exception.Response.StatusCode)"
        if ($_.ErrorDetails.Message) { $_.ErrorDetails.Message }
    }
}
```

1. Полная заявка — HTTP 200, возвращается ID созданной записи:
   ```powershell
   Send-LeadTest '{"name":"Ирина","contact":"+79990000000","source":"landing","comment":"Консультация"}'
   ```
2. Только контакт — HTTP 200, остальные поля сохраняются пустыми:
   ```powershell
   Send-LeadTest '{"contact":"mail@example.com"}'
   ```
3. Контакт с пробелами — HTTP 200, пробелы по краям удаляются:
   ```powershell
   Send-LeadTest '{"contact":"  example  "}'
   ```
4. Нет контакта — HTTP 400, заявка не сохраняется:
   ```powershell
   Send-LeadTest '{"name":"Ирина"}'
   ```
5. Пустой контакт — HTTP 400, заявка не сохраняется:
   ```powershell
   Send-LeadTest '{"contact":""}'
   ```
6. Контакт из пробелов — HTTP 400, заявка не сохраняется:
   ```powershell
   Send-LeadTest '{"contact":"   "}'
   ```
7. Неверный тип поля — HTTP 400, заявка не сохраняется:
   ```powershell
   Send-LeadTest '{"contact":123}'
   ```
8. Невалидный JSON — HTTP 400, заявка не сохраняется:
   ```powershell
   Send-LeadTest '{broken'
   ```
