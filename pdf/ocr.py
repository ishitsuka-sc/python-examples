import fitz

doc = fitz.open()
page = doc.new_page(width=595, height=842)

# 画像を貼る
rect = fitz.Rect(0, 0, 595, 842)
page.insert_image(rect, filename="scan.png")

# OCR結果を透明文字として重ねる
page.insert_text(
    (100, 120),
    "This text can be searched.",
    fontsize=18,
    fill_opacity=0.0
)

doc.save("ocr_style.pdf")
doc.close()
