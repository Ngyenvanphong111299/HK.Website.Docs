import psycopg2
from psycopg2.extras import RealDictCursor

db_cs = "Host=103.82.25.58;Port=5000;Database=WebsiteOtoHoangKim;User Id=otohk_user;Password=yuweuw32f4qrryeho8y97q3greH;Timeout=15"
parts = dict(item.split("=") for item in db_cs.split(";") if "=" in item)
conn = psycopg2.connect(
    host=parts.get("Host"),
    port=parts.get("Port"),
    dbname=parts.get("Database"),
    user=parts.get("User Id"),
    password=parts.get("Password"),
    connect_timeout=int(parts.get("Timeout", 15))
)
cur = conn.cursor()

# Get all unique image URLs referenced across WebsiteOtoHoangKim business tables
query = """
    SELECT "AvatarPath" as url FROM "Products" WHERE "AvatarPath" IS NOT NULL AND "AvatarPath" != ''
    UNION
    SELECT "ImagePath" as url FROM "ProductImages" WHERE "ImagePath" IS NOT NULL AND "ImagePath" != ''
    UNION
    SELECT "AvatarPath" as url FROM "ProductCategories" WHERE "AvatarPath" IS NOT NULL AND "AvatarPath" != ''
    UNION
    SELECT "SliderPath" as url FROM "ProductCategories" WHERE "SliderPath" IS NOT NULL AND "SliderPath" != ''
    UNION
    SELECT "BannerUrl" as url FROM "ProductCategories" WHERE "BannerUrl" IS NOT NULL AND "BannerUrl" != ''
    UNION
    SELECT "AvatarPath" as url FROM "Posts" WHERE "AvatarPath" IS NOT NULL AND "AvatarPath" != ''
    UNION
    SELECT "ImageUrl" as url FROM "AutoBrands" WHERE "ImageUrl" IS NOT NULL AND "ImageUrl" != ''
    UNION
    SELECT "BackgroundImage" as url FROM "AutoBrands" WHERE "BackgroundImage" IS NOT NULL AND "BackgroundImage" != ''
    UNION
    SELECT "BannerUrl" as url FROM "AutoModels" WHERE "BannerUrl" IS NOT NULL AND "BannerUrl" != ''
    UNION
    SELECT "SliderPath" as url FROM "AutoModels" WHERE "SliderPath" IS NOT NULL AND "SliderPath" != ''
    UNION
    SELECT "ImageUrl" as url FROM "PromotionPosts" WHERE "ImageUrl" IS NOT NULL AND "ImageUrl" != ''
    UNION
    SELECT "Url" as url FROM "BranchPageGalleryImages" WHERE "Url" IS NOT NULL AND "Url" != ''
    UNION
    SELECT "ImageNoBackground" as url FROM "DecalStyles" WHERE "ImageNoBackground" IS NOT NULL AND "ImageNoBackground" != ''
    UNION
    SELECT "BackgroundImage" as url FROM "DecalStyles" WHERE "BackgroundImage" IS NOT NULL AND "BackgroundImage" != ''
"""

cur.execute(f"SELECT COUNT(*) FROM ({query}) AS all_urls;")
total_distinct_biz_urls = cur.fetchone()[0]

cur.execute(f"""
    SELECT 
        COUNT(CASE WHEN lower(url) LIKE '%.webp%' THEN 1 END) as webp_cnt,
        COUNT(CASE WHEN lower(url) LIKE '%.jpg%' OR lower(url) LIKE '%.jpeg%' THEN 1 END) as jpg_cnt,
        COUNT(CASE WHEN lower(url) LIKE '%.png%' THEN 1 END) as png_cnt,
        COUNT(CASE WHEN lower(url) LIKE '%.gif%' THEN 1 END) as gif_cnt,
        COUNT(CASE WHEN lower(url) LIKE '%.svg%' THEN 1 END) as svg_cnt
    FROM ({query}) AS all_urls;
""")
stats = cur.fetchone()

print(f"Total distinct business image URLs in WebsiteOtoHoangKim: {total_distinct_biz_urls}")
print(f"  - WebP: {stats[0]}")
print(f"  - JPG/JPEG: {stats[1]}")
print(f"  - PNG: {stats[2]}")
print(f"  - GIF: {stats[3]}")
print(f"  - SVG: {stats[4]}")

conn.close()