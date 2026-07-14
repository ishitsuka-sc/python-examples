import fitz  # PyMuPDF

# 新しいPDFを作成
doc = fitz.open()

page = doc.new_page(width=595, height=842)  # A4

# 見える文字
page.insert_text(
    (50, 100),
    "You can see this text......",
    fontsize=24,
    color=(0, 0, 0)
)

# 完全に透明な文字
page.insert_text(
    (50, 150),
    "This is invisible text.",
    fontsize=8,
    color=(1, 0, 0),      # 赤（実際には見えない）
    fill_opacity=0.0       # ★透明
)

doc.save("transparent_text.pdf")
doc.close()

print("transparent_text.pdf を作成しました。")
