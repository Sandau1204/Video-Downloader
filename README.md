📺 Universal Video Downloader - Ultimate Pro
Phần mềm tải video đa nền tảng mạnh mẽ, hỗ trợ tải xuống chất lượng cao (lên đến 4K) từ YouTube, Facebook, TikTok, Vimeo và hàng ngàn trang web khác. Được tích hợp công cụ chuyển đổi định dạng và giao diện trực quan dễ sử dụng.

✨ Tính năng nổi bật
Đa nền tảng: Hỗ trợ tải video từ Youtube, Facebook, TikTok (không logo), Vimeo, Dailymotion...

Chất lượng tùy chọn: Tải video sắc nét từ 4K, 2K, 1080p xuống đến 360p.

Chuyển đổi định dạng:

🎬 Video: MP4 (H.264/H.265) tương thích mọi thiết bị.

🎵 Âm thanh: Tách nhạc MP3 chất lượng cao (192kbps) từ video.

Thông tin chi tiết: Xem trước ảnh bìa (Thumbnail), tiêu đề, thời lượng trước khi tải.

Theo dõi thời gian thực: Hiển thị tốc độ tải (MB/s), thời gian dự kiến (ETA), và dung lượng file.

Giao diện: Thiết kế hiện đại, dễ sử dụng với Tkinter.

📥 Hướng dẫn cài đặt & Sử dụng (Cho người dùng)
Yêu cầu bắt buộc
Để phần mềm hoạt động 100% tính năng (ghép nhạc vào video HD, tách file MP3), máy tính cần có FFmpeg.

Bước 1: Chuẩn bị
Tải file phần mềm VideoDownloader.py.

Tải FFmpeg (file ffmpeg.exe).

Quan trọng: Đặt file ffmpeg.exe vào CÙNG THƯ MỤC với file phần mềm.

Cấu trúc thư mục chuẩn:

Plaintext

Thu_Muc_Phan_Mem/
├── VideoDownloader.py  <-- Chạy file này
└── ffmpeg.exe               <-- Để yên file này ở đây
Bước 2: Cách sử dụng
Mở phần mềm.

Copy đường link video (Youtube, Facebook...).

Bấm nút "Dán Link" hoặc dán thủ công vào ô nhập liệu.

Bấm nút "🔍 Kiểm tra" để xem thông tin video (tiêu đề, ảnh).

Chọn Định dạng (Video hoặc Âm thanh) và Chất lượng mong muốn.

Bấm "BẮT ĐẦU TẢI NGAY" và chờ đợi.

💻 Hướng dẫn dành cho Lập trình viên (Development)
Nếu bạn muốn phát triển thêm hoặc chạy từ mã nguồn Python.

1. Cài đặt môi trường
Đảm bảo máy đã cài Python 3.x và Git.

Bash

# Clone dự án về máy
```git clone https://github.com/Sandau1204/Video-Downloader.git```

# Di chuyển vào thư mục
```cd Universal-Downloader```

# Cài đặt các thư viện cần thiết
```pip install yt-dlp pillow```

2. Khắc phục lỗi Warning YouTube
Để tránh lỗi cảnh báo và giảm tốc độ tải từ Youtube, khuyến khích cài đặt Node.js:

Tải tại: nodejs.org

Sau khi cài, khởi động lại VS Code/Terminal.

3. Chạy phần mềm
Bash

```python VideoDownloader.py```

❓ Câu hỏi thường gặp (Troubleshooting)
Q: Tại sao tôi tải video về nhưng không có tiếng? A: Bạn chưa đặt file ffmpeg.exe cùng chỗ với phần mềm. Youtube tách riêng hình và tiếng ở chất lượng cao, cần FFmpeg để ghép lại.

Q: Tại sao tốc độ tải bị chậm? A: Có thể do mạng internet hoặc server của Youtube đang bóp băng thông. Hãy thử cài thêm Node.js nếu bạn đang chạy bằng source code.

Q: Phần mềm báo lỗi "Sign in to confirm you're not a bot"? A: Youtube chặn IP của bạn. Hãy thử đổi mạng Wifi hoặc dùng VPN/4G.

👨‍💻 Thông tin tác giả
Dự án được phát triển và duy trì bởi:

Developer: Sand

Role: Fullstack Developer

Contact: [Uông Sỹ Thắng Anh](https://www.facebook.com/Sandau1204)

© 2025 Sand. All rights reserved
