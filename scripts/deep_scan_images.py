import psycopg2
from psycopg2.extras import RealDictCursor
import json

db_configs = {
    "WebsiteOtoHoangKim": "Host=103.82.25.58;Port=5000;Database=WebsiteOtoHoangKim;User Id=otohk_user;Password=yuweuw32f4qrryeho8y97q3greH;Timeout=15",
    "HK_OmmiService": "Host=103.179.188.97;Port=87;Database=HK_OmmiService;User Id=phong_nv;Password=8u34yjh7rMT7RnE752QAyCUhP0WyYKwg;Timeout=15",
    "erpdb": "Host=103.82.24.57;Port=5001;Database=erpdb;User Id=odoo;Password=j768945kwHTjyfth7S;Timeout=15"
}

def parse_conn_str(cs):
    parts = dict(item.split("=") for item in cs.split(";") if "=" in item)
    return {
        "host": parts.get("Host"),
        "port": parts.get("Port"),
        "dbname": parts.get("Database"),
        "user": parts.get("User Id"),
        "password": parts.get("Password"),
        "connect_timeout": int(parts.get("Timeout", 15))
    }

print("================================================================================")
print("1. CHI TIẾT DB WEBSITEOTOHOANGKIM")
print("================================================================================")
conn_web = psycopg2.connect(**parse_conn_str(db_configs["WebsiteOtoHoangKim"]))
cur_web = conn_web.cursor(cursor_factory=RealDictCursor)

tables_to_check_web = [
    ("Products", "AvatarPath"),
    ("ProductImages", "ImagePath"),
    ("ProductCategories", "AvatarPath"),
    ("ProductCategories", "SliderPath"),
    ("ProductCategories", "BannerUrl"),
    ("Posts", "AvatarPath"),
    ("Posts", "SeoOgImage"),
    ("PostImages", "ImagePath"),
    ("AutoBrands", "ImageUrl"),
    ("AutoBrands", "BackgroundImage"),
    ("AutoModels", "BannerUrl"),
    ("AutoModels", "SliderPath"),
    ("PromotionPosts", "ImageUrl"),
    ("PromotionPosts", "BannerUrl"),
    ("YoutubeShorts", "AvatarPath"),
    ("BranchPageGalleryImages", "Url"),
    ("WorkAlbumImages", "Url"),
    ("DecalStyles", "ImageNoBackground"),
    ("DecalStyles", "BackgroundImage"),
    ("HomePageFeaturedCategories", "IconUrl"),
    ("ImageTransformations", "OriginalUrl"),
    ("ImageTransformations", "OptimizedUrl")
]

web_stats = {}
for tbl, col in tables_to_check_web:
    try:
        cur_web.execute(f'''
            SELECT 
                COUNT(*) as total_rows,
                COUNT(CASE WHEN "{col}" IS NOT NULL AND "{col}" != \'\' THEN 1 END) as has_val,
                COUNT(CASE WHEN lower("{col}") LIKE \'%.webp%\' THEN 1 END) as webp_cnt,
                COUNT(CASE WHEN lower("{col}") LIKE \'%.jpg%\' OR lower("{col}") LIKE \'%.jpeg%\' THEN 1 END) as jpg_cnt,
                COUNT(CASE WHEN lower("{col}") LIKE \'%.png%\' THEN 1 END) as png_cnt,
                COUNT(CASE WHEN lower("{col}") LIKE \'%.gif%\' THEN 1 END) as gif_cnt,
                COUNT(CASE WHEN lower("{col}") LIKE \'%.svg%\' THEN 1 END) as svg_cnt
            FROM "{tbl}";
        ''')
        res = dict(cur_web.fetchone())
        web_stats[f"{tbl}.{col}"] = res
        print(f"{tbl}.{col:20} -> Total: {res['total_rows']:7} | HasVal: {res['has_val']:7} | WebP: {res['webp_cnt']:7} | JPG: {res['jpg_cnt']:7} | PNG: {res['png_cnt']:7} | GIF: {res['gif_cnt']:4} | SVG: {res['svg_cnt']:4}")
    except Exception as e:
        print(f"Error {tbl}.{col}: {e}")

# Check ProductImages distinct URLs
cur_web.execute('SELECT COUNT(DISTINCT "ImagePath") FROM "ProductImages";')
print(f"ProductImages Distinct ImagePath: {cur_web.fetchone()['count']}")

# Check ImageTransformations size
cur_web.execute('SELECT SUM("FileSize") as total_bytes, COUNT(*) as count FROM "ImageTransformations";')
it_size = cur_web.fetchone()
print(f"ImageTransformations Total FileSize: {it_size['total_bytes']} bytes (~ {it_size['total_bytes'] / (1024**3):.2f} GB) across {it_size['count']} records")

conn_web.close()

print("\n================================================================================")
print("2. CHI TIẾT DB HK_OMMISERVICE")
print("================================================================================")
conn_omni = psycopg2.connect(**parse_conn_str(db_configs["HK_OmmiService"]))
cur_omni = conn_omni.cursor(cursor_factory=RealDictCursor)

tables_to_check_omni = [
    ("Products", "AvatarPath"),
    ("ITResources", "FilePath"),
    ("ITTaskImages", "Url"),
    ("WorkshopRealMediaAssets", "CdnUrl"),
    ("WorkshopRealMediaAssets", "ThumbnailUrl"),
    ("image_knowledge", "ImageUrl")
]

for tbl, col in tables_to_check_omni:
    try:
        cur_omni.execute(f'''
            SELECT 
                COUNT(*) as total_rows,
                COUNT(CASE WHEN "{col}" IS NOT NULL AND "{col}" != \'\' THEN 1 END) as has_val,
                COUNT(CASE WHEN lower("{col}") LIKE \'%.webp%\' THEN 1 END) as webp_cnt,
                COUNT(CASE WHEN lower("{col}") LIKE \'%.jpg%\' OR lower("{col}") LIKE \'%.jpeg%\' THEN 1 END) as jpg_cnt,
                COUNT(CASE WHEN lower("{col}") LIKE \'%.png%\' THEN 1 END) as png_cnt
            FROM "{tbl}";
        ''')
        res = dict(cur_omni.fetchone())
        print(f"{tbl}.{col:20} -> Total: {res['total_rows']:7} | HasVal: {res['has_val']:7} | WebP: {res['webp_cnt']:7} | JPG: {res['jpg_cnt']:7} | PNG: {res['png_cnt']:7}")
    except Exception as e:
        print(f"Error {tbl}.{col}: {e}")

# Check ITResources FileSize
cur_omni.execute('SELECT SUM("FileSize") as total_bytes, COUNT(*) FROM "ITResources";')
r = cur_omni.fetchone()
print(f"ITResources Total FileSize: {r['total_bytes']} bytes across {r['count']} records")

# Check WorkshopRealMediaAssets FileSizeKb
cur_omni.execute('SELECT SUM("FileSizeKb") as total_kb, COUNT(*) FROM "WorkshopRealMediaAssets";')
r = cur_omni.fetchone()
print(f"WorkshopRealMediaAssets Total: {r['total_kb']} KB across {r['count']} records")

conn_omni.close()

print("\n================================================================================")
print("3. CHI TIẾT DB ERPDB (ODOO)")
print("================================================================================")
conn_erp = psycopg2.connect(**parse_conn_str(db_configs["erpdb"]))
cur_erp = conn_erp.cursor(cursor_factory=RealDictCursor)

cur_erp.execute("""
    SELECT 
        res_model,
        count(*) as total_count,
        sum(case when file_size is not null then file_size else 0 end) as known_bytes,
        count(case when file_size is not null then 1 end) as has_size_cnt,
        count(case when mimetype = 'image/webp' then 1 end) as webp_cnt,
        count(case when mimetype in ('image/jpeg', 'image/jpg') then 1 end) as jpg_cnt,
        count(case when mimetype = 'image/png' then 1 end) as png_cnt,
        count(case when mimetype not in ('image/webp', 'image/jpeg', 'image/jpg', 'image/png') then 1 end) as other_cnt
    FROM ir_attachment
    WHERE mimetype like 'image%'
    GROUP BY res_model
    ORDER BY total_count DESC;
""")
odoo_models = cur_erp.fetchall()
print(f"{'res_model':25} | {'total':7} | {'has_size':8} | {'known_MB':10} | {'webp':6} | {'jpg':7} | {'png':7}")
print("-" * 80)
total_odoo_imgs = 0
total_odoo_bytes = 0
for m in odoo_models:
    total_odoo_imgs += m['total_count']
    total_odoo_bytes += m['known_bytes']
    mb = m['known_bytes'] / (1024*1024)
    print(f"{str(m['res_model']):25} | {m['total_count']:7} | {m['has_size_cnt']:8} | {mb:10.2f} | {m['webp_cnt']:6} | {m['jpg_cnt']:7} | {m['png_cnt']:7}")

print("-" * 80)
print(f"Tổng ảnh Odoo ERP: {total_odoo_imgs:,} ảnh | Dung lượng ghi nhận trong DB: {total_odoo_bytes / (1024**3):.2f} GB")

conn_erp.close()