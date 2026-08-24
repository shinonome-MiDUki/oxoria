from PIL import Image, ImageDraw

def convert_to_mac_icon(input_path, output_path, size=1024, radius=220):
    # 1. 白背景の正方形ベース画像を作成
    base_img = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    
    # 2. 元画像を読み込み、アスペクト比を維持したままリサイズ（収まるように調整）
    orig_img = Image.open(input_path).convert("RGBA")
    orig_img.thumbnail((size, size), Image.Resampling.LANCZOS)
    
    # 中央に配置するための座標計算
    x = (size - orig_img.width) // 2
    y = (size - orig_img.height) // 2
    
    # 白背景の中央に元画像を貼り付け
    base_img.paste(orig_img, (x, y), orig_img)
    
    # 3. Macのアイコン風の「角丸マスク」を作成
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    # macOSのアイコンの比率に近い大きめの角丸（radiusで調整可能）
    draw.rounded_rectangle([(0, 0), (size, size)], radius=radius, fill=255)
    
    # 4. 角丸の外側を白で埋めた新しい画像を作成し、マスクを適用
    final_img = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    final_img.paste(base_img, (0, 0), mask)
    
    # 5. 保存（アイコン用にPNG形式）
    final_img.save(output_path, "PNG")
    print(f"保存完了: {output_path}")

# 実行例（'icon.png' を変換して 'mac_icon.png' として保存）
convert_to_mac_icon("/Users/shiinaayame/Documents/oxoria/src/oxoria/_resources/assets/icon.jpg", "/Users/shiinaayame/Documents/oxoria/src/oxoria/_resources/assets/m_icon.png")