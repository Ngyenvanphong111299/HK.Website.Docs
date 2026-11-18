# BÁO CÁO TOÀN DIỆN: ĐỐI SOÁT NƠI LƯU TRỮ ẢNH GỐC SẢN PHẨM & THỐNG KÊ HÌNH ẢNH TOÀN HỆ THỐNG

**Người thực hiện:** Đạt — Data Leader (Phòng Dữ liệu & Đo lường)  
**Thời gian rà soát:** 18/11/2026  
**Môi trường xác thực:** Live Production Databases (`WebsiteOtoHoangKim`, `HK_OmmiService`, `erpdb` Odoo) & Web Server Source  

---

## PHẦN 1. NƠI LƯU TRỮ ẢNH GỐC CỦA SẢN PHẨM TRƯỚC KHI ĐỔI SANG WEBP

Qua rà soát sâu cấu trúc dữ liệu và pipeline tối ưu ảnh, ảnh gốc sản phẩm trước khi chuyển đổi sang WebP hiện đang nằm tại **4 vị trí cụ thể trong database**:

### 1. Kho ảnh gốc nguồn cốt lõi (Source of Truth) — Database ERP Odoo (`erpdb` port 5001)
* **Bảng:** `ir_attachment`
* **Số lượng ảnh gốc sản phẩm:** **122,477 bản ghi** (100% định dạng JPEG và PNG, hoàn toàn không có WebP):
  * **Model `product.template` (Ảnh đại diện sản phẩm):** **47,860 ảnh gốc** (38,511 JPEG, 9,349 PNG).
  * **Model `product.image` (Thư viện ảnh chi tiết sản phẩm):** **74,617 ảnh gốc** (49,634 JPEG, 24,973 PNG).
* **Cơ chế lưu:** Odoo lưu ảnh gốc ở độ phân giải cao nhất qua trường `image_1920` (ảnh gốc full size 1920px), kèm các bản scale `image_1024`, `image_512`, `image_256`, `image_128`.
* **Vị trí lưu trữ vật lý:** DigitalOcean Spaces S3 bucket `s3-storage-pro` qua đường dẫn `s3://odoo/<sha1_hash>` và CDN URL: `https://s3-storage-pro.sgp1.cdn.digitaloceanspaces.com/s3-storage-pro/odoo/<hash>`.

### 2. Bảng lưu vết chuyển đổi (Transformation Cache) — DB `WebsiteOtoHoangKim` (port 5000)
* **Bảng:** `ImageTransformations`
* **Cột lưu ảnh gốc:** `OriginalUrl` (đối chiếu với `OptimizedUrl` chứa link WebP).
* **Số lượng:** Đang lưu vết **376,913 bản ghi chuyển đổi**, trong đó:
  * **231,296 URL gốc là JPG/JPEG**
  * **8,001 URL gốc là PNG**
  * **36,726 URL gốc trỏ từ S3 Odoo**
* **Cơ chế:** Service `ProcessImageOptimization` của backend website đọc cột này để phục vụ WebP tương ứng khi người dùng truy cập.

### 3. Lưu trực tiếp trong bảng sản phẩm Website — DB `WebsiteOtoHoangKim`
* **Bảng `Products` (cột `AvatarPath`):** Trong tổng số 12,419 sản phẩm có ảnh, có tới **9,151 sản phẩm vẫn đang lưu trực tiếp URL ảnh gốc đuôi `.jpg/.jpeg`** và **543 sản phẩm đuôi `.png`** (chỉ có 1,516 sản phẩm lưu trực tiếp đuôi `.webp`).
* **Bảng `ProductImages` (cột `ImagePath`):** Có **24,271 ảnh gallery vẫn lưu đuôi `.jpg`** và **1,393 ảnh lưu đuôi `.png`** (44,281 ảnh đã lưu đuôi `.webp`).

### 4. Database phụ trợ — DB `HK_OmmiService` (port 87)
* **Bảng `Products` (cột `AvatarPath`):** Có **9,187 sản phẩm lưu đuôi `.jpg`** và **538 sản phẩm lưu đuôi `.png`** (chỉ 744 sản phẩm lưu đuôi `.webp`).

---

## PHẦN 2. THỐNG KÊ TỔNG SỐ LƯỢNG VÀ TỔNG DUNG LƯỢNG HÌNH ẢNH

### 1. Thống kê trên Database (Live DB Query)

| Database | Bảng / Thực thể | Tổng số bản ghi ảnh | Định dạng WebP | Định dạng JPG / JPEG | Định dạng PNG | Định dạng khác (SVG, GIF) | Dung lượng ghi nhận trong DB |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **WebsiteOtoHoangKim** | `ImageTransformations` (Bản tối ưu WebP) | **376,913** | 376,913 (100%) | 0 | 0 | 0 | **16.22 GB** (16,216,841,028 B) |
| **WebsiteOtoHoangKim** | `Products` (Avatar) | **12,419** | 1,516 | 9,151 | 543 | 0 | *(Nằm trong CDN Storage)* |
| **WebsiteOtoHoangKim** | `ProductImages` (Gallery sản phẩm) | **75,348** *(69,960 URL duy nhất)* | 44,281 | 24,271 | 1,393 | 1 GIF | *(Nằm trong CDN Storage)* |
| **WebsiteOtoHoangKim** | `ProductCategories` (Avatar/Slider/Banner) | **1,251** | 1,251 (100%) | 0 | 0 | 0 | *(Nằm trong CDN Storage)* |
| **WebsiteOtoHoangKim** | `Posts` (Avatar bài viết) | **2,514** | 2,505 | 29 | 0 | 0 | *(Nằm trong CDN Storage)* |
| **WebsiteOtoHoangKim** | Các bảng khác (AutoBrands, AutoModels, Decal...) | **447** | 297 | 107 | 0 | 16 SVG | *(Nằm trong CDN Storage)* |
| **HK_OmmiService** | `Products`, `image_knowledge`, `WorkshopRealMedia` | **12,010** | 929 | 9,444 | 543 | 0 | **3.3 MB** *(Media assets)* |
| **erpdb (Odoo)** | `ir_attachment` (Kho gốc ERP toàn công ty) | **302,243** | 18 | 200,985 | 49,431 | 51,809 | **38.34 GB** (41,170,021,144 B)* |

*Tổng số URL ảnh nghiệp vụ duy nhất trên DB `WebsiteOtoHoangKim`:* **83,823 URL** (gồm 47,595 WebP, 30,546 JPG/JPEG, 1,107 PNG, 1 GIF).  
*\*Ghi chú dung lượng Odoo:* 38.34 GB là tổng dung lượng của 91,481 file có trường `file_size` được lưu trong DB; các file còn lại lưu dạng S3 object trên DigitalOcean Spaces.

---

### 2. Thống kê trên Thư mục Website (Static Files trên Server)

Quét trong thư mục mã nguồn website Ô Tô Hoàng Kim (`HK.WebsiteOtoHoangKim.src`):
* **Tổng số lượng file ảnh tĩnh:** **1,553 file** (Toàn bộ monorepo có **1,624 file**).
* **Tổng dung lượng:** **337.23 MB** (337,232,612 bytes).
* **Cơ cấu định dạng:**
  * WebP: **705 file** (45.4%)
  * SVG (Icon/Vector): **439 file** (28.3%)
  * PNG: **259 file** (16.7%)
  * JPG: **150 file** (9.6%)

---

## PHẦN 3. TỔNG HỢP TOÀN HỆ THỐNG

1. **Tổng số lượng hình ảnh:**
   * **Trên các Database:** Có **388,923 bản ghi ảnh website** (trong đó có 376,913 bản tối ưu WebP trong `ImageTransformations` và 83,823 URL ảnh nghiệp vụ duy nhất) + **302,243 bản ghi ảnh gốc trên ERP Odoo**.
   * **Trên Website tĩnh:** **1,553 file ảnh**.
2. **Tổng dung lượng:**
   * **Dung lượng ảnh tối ưu WebP ghi nhận trong DB Website:** **16.22 GB**.
   * **Dung lượng ảnh gốc ghi nhận trong DB Odoo ERP:** **38.34 GB**.
   * **Dung lượng ảnh tĩnh cục bộ website:** **0.34 GB** (337.23 MB).
   * **Tổng dung lượng ảnh đã xác thực qua DB & website:** **~54.90 GB**.
