$Serial = Get-WmiObject -Class Win32_BIOS | Select-Object -ExpandProperty SerialNumber
