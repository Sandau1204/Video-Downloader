import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk  # Đã có sẵn trong code của bạn
import yt_dlp
import threading
import os
import sys
import ctypes
import urllib.request
import io
import datetime
import webbrowser

# Hàm xử lý đường dẫn tài nguyên (Quan trọng cho file exe)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class UniversalDownloaderApp:
    def __init__(self, root):
        self.root = root
        
    
        myappid = 'sandau.videodownloader.pro.v1'
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass # Bỏ qua nếu không phải Windows

        self.root.title("Video Downloader")
        
        # Cách này sửa lỗi do file icon.ico thực chất là ảnh JPG/PNG
        try:
            icon_path = resource_path("icon.ico")
            # Dùng Pillow để đọc ảnh (chấp nhận cả jpg, png, ico lỗi)
            img = Image.open(icon_path)
            photo = ImageTk.PhotoImage(img)
            # True nghĩa là áp dụng icon này cho tất cả cửa sổ con sau này
            self.root.iconphoto(True, photo) 
        except Exception as e:
            print(f"Lỗi tải icon: {e}")
            # Nếu lỗi, thử dùng iconbitmap như phương án dự phòng (chỉ chạy nếu là file .ico chuẩn)
            try:
                self.root.iconbitmap(resource_path("icon.ico"))
            except:
                pass

        self.root.geometry("700x750") 
        self.root.resizable(False, False)
        
        # --- THÔNG TIN TÁC GIẢ (Giữ nguyên code cũ của bạn) ---
        self.author_name = "Sand"
        self.app_version = "v2.1.0"
        self.contact_link = "https://www.facebook.com/Sandau1204"

        # Biến toàn cục
        self.save_path = os.getcwd()
        self.video_info = None 

        self.create_menu()

        # --- STYLE ---
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Segoe UI", 10), padding=5)
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))
        # Style riêng cho thanh tiến trình dày hơn chút
        style.configure("green.Horizontal.TProgressbar", thickness=25)

        # ================= GIAO DIỆN CHÍNH =================

        # 1. HEADER
        lbl_header = ttk.Label(root, text="MULTI-PLATFORM DOWNLOADER", style="Header.TLabel", foreground="#007bff")
        lbl_header.pack(pady=(15, 5))

        # 2. KHUNG NHẬP LIỆU
        frame_input = ttk.LabelFrame(root, text=" Nhập đường dẫn (Link) ", padding=10)
        frame_input.pack(fill="x", padx=15, pady=5)

        ttk.Label(frame_input, text="URL:").pack(side="left")
        self.entry_url = ttk.Entry(frame_input, width=60)
        self.entry_url.pack(side="left", padx=5, fill="x", expand=True)
        btn_paste = ttk.Button(frame_input, text="Dán Link", command=self.paste_link)
        btn_paste.pack(side="left", padx=2)
        btn_check = ttk.Button(frame_input, text="🔍 Kiểm tra", command=self.start_check_info_thread)
        btn_check.pack(side="left", padx=2)

        # 3. KHUNG PREVIEW
        self.frame_preview = ttk.LabelFrame(root, text=" Thông tin Video ", padding=10)
        self.frame_preview.pack(fill="x", padx=15, pady=5)

        self.lbl_thumbnail = ttk.Label(self.frame_preview, text="[Chưa có dữ liệu]", anchor="center")
        self.lbl_thumbnail.pack(side="left", padx=(0, 15))

        frame_info_text = tk.Frame(self.frame_preview)
        frame_info_text.pack(side="left", fill="both", expand=True)

        self.lbl_title = ttk.Label(frame_info_text, text="Tiêu đề: ---", wraplength=380, font=("Segoe UI", 10, "bold"))
        self.lbl_title.pack(anchor="w", pady=2)
        self.lbl_duration = ttk.Label(frame_info_text, text="Thời lượng: ---")
        self.lbl_duration.pack(anchor="w", pady=2)
        self.lbl_source = ttk.Label(frame_info_text, text="Nguồn: ---")
        self.lbl_source.pack(anchor="w", pady=2)

        # 4. KHUNG CÀI ĐẶT
        frame_settings = ttk.LabelFrame(root, text=" Cài đặt tải xuống ", padding=10)
        frame_settings.pack(fill="x", padx=15, pady=5)

        frame_path = tk.Frame(frame_settings)
        frame_path.pack(fill="x", pady=2)
        ttk.Label(frame_path, text="Lưu tại: ").pack(side="left")
        self.entry_path = ttk.Entry(frame_path)
        self.entry_path.insert(0, self.save_path)
        self.entry_path.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(frame_path, text="Chọn...", command=self.browse_folder).pack(side="left")

        frame_options = tk.Frame(frame_settings)
        frame_options.pack(fill="x", pady=(10, 0))
        self.format_var = tk.StringVar(value="video")
        rb_video = ttk.Radiobutton(frame_options, text="Video (MP4)", variable=self.format_var, value="video", command=self.toggle_quality_state)
        rb_video.pack(side="left", padx=(0, 10))
        rb_audio = ttk.Radiobutton(frame_options, text="Âm thanh (MP3)", variable=self.format_var, value="audio", command=self.toggle_quality_state)
        rb_audio.pack(side="left", padx=(0, 20))

        ttk.Label(frame_options, text="Chất lượng:").pack(side="left")
        self.quality_var = tk.StringVar()
        self.cbo_quality = ttk.Combobox(frame_options, textvariable=self.quality_var, state="readonly", width=15)
        self.cbo_quality['values'] = ("Best (Max)", "4K (2160p)", "2K (1440p)", "Full HD (1080p)", "HD (720p)", "SD (480p)", "Low (360p)")
        self.cbo_quality.current(0)
        self.cbo_quality.pack(side="left", padx=5)

        # 5. KHUNG TIẾN TRÌNH & CHI TIẾT (NÂNG CẤP)
        frame_progress = ttk.LabelFrame(root, text=" Trạng thái tải xuống ", padding=10)
        frame_progress.pack(fill="both", expand=True, padx=15, pady=5)

        # Thanh %
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(frame_progress, variable=self.progress_var, maximum=100, style="green.Horizontal.TProgressbar")
        self.progress_bar.pack(fill="x", pady=(5, 10))

        # Khung thông tin chi tiết (Grid layout cho đẹp)
        frame_details = tk.Frame(frame_progress)
        frame_details.pack(fill="x")

        # Label Tốc độ
        self.lbl_speed = ttk.Label(frame_details, text="🚀 Tốc độ: 0.0 MiB/s", width=25, foreground="#2980b9")
        self.lbl_speed.grid(row=0, column=0, sticky="w")
        
        # Label Thời gian còn lại
        self.lbl_eta = ttk.Label(frame_details, text="⏳ Còn lại: --:--", width=25, foreground="#e67e22")
        self.lbl_eta.grid(row=0, column=1, sticky="w")

        # Label Dung lượng
        self.lbl_size = ttk.Label(frame_details, text="📦 Tổng: ---", width=25, foreground="#8e44ad")
        self.lbl_size.grid(row=0, column=2, sticky="w")

        # Dòng trạng thái chung
        self.lbl_status = ttk.Label(frame_progress, text="Sẵn sàng", foreground="gray", font=("Segoe UI", 9, "italic"))
        self.lbl_status.pack(anchor="w", pady=(10, 0))

        # 6. LOG BOX
        self.log_box = scrolledtext.ScrolledText(root, height=4, font=("Consolas", 8), state='disabled', bg="#f8f9fa")
        self.log_box.pack(fill="x", padx=15, pady=5)

        # 7. NÚT TẢI
        self.btn_download = tk.Button(root, text="BẮT ĐẦU TẢI NGAY", bg="#007bff", fg="white", 
                                      font=("Segoe UI", 12, "bold"), relief="flat", 
                                      command=self.start_download_thread)
        self.btn_download.pack(fill="x", padx=30, pady=10)

        self.create_footer()

    # ================= LOGIC MỚI: XỬ LÝ TIẾN TRÌNH CHI TIẾT =================
    
    def progress_hook(self, d):
        """Hàm này nhận dữ liệu real-time từ yt-dlp"""
        if d['status'] == 'downloading':
            # 1. Lấy dữ liệu thô
            p_str = d.get('_percent_str', '0%') # Ví dụ: " 45.5%"
            speed_str = d.get('_speed_str', 'N/A') # Ví dụ: " 2.5MiB/s"
            eta_str = d.get('_eta_str', 'N/A') # Ví dụ: "00:30"
            
            # Lấy tổng dung lượng (Có thể là estimated hoặc total)
            total_bytes = d.get('_total_bytes_str') or d.get('_total_bytes_estimate_str', 'Unknown')

            # 2. Xử lý số liệu phần trăm để gán vào thanh bar
            try:
                p_val = float(p_str.replace('%',''))
            except: 
                p_val = 0

            # 3. Cập nhật UI (Dùng self.root.after để đảm bảo thread-safe)
            self.root.after(0, lambda: self.update_progress_ui(p_val, p_str, speed_str, eta_str, total_bytes))

        elif d['status'] == 'finished':
            self.root.after(0, lambda: self.lbl_status.config(text="Đã tải xong dữ liệu thô. Đang ghép file (FFmpeg)...", foreground="#d35400"))
            self.root.after(0, lambda: self.progress_var.set(100))

    def update_progress_ui(self, val, p_text, speed, eta, total):
        # Cập nhật thanh trượt
        self.progress_var.set(val)
        
        # Cập nhật các Label chi tiết
        self.lbl_speed.config(text=f"🚀 Tốc độ: {speed}")
        self.lbl_eta.config(text=f"⏳ Còn lại: {eta}")
        self.lbl_size.config(text=f"📦 Tổng: {total}")
        
        # Cập nhật trạng thái text
        self.lbl_status.config(text=f"Đang tải xuống... {p_text}", foreground="blue")

    # ================= CÁC HÀM CŨ (GIỮ NGUYÊN) =================

    def toggle_quality_state(self):
        if self.format_var.get() == "audio":
            self.cbo_quality.config(state="disabled")
        else:
            self.cbo_quality.config(state="readonly")

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Hệ thống", menu=file_menu)
        file_menu.add_command(label="Thoát", command=self.root.quit)
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Trợ giúp", menu=help_menu)
        help_menu.add_command(label="Hướng dẫn", command=self.show_guide)
        help_menu.add_command(label="Về tác giả", command=self.show_about)

    def create_footer(self):
        frame_footer = tk.Frame(self.root, bg="#e9ecef", height=30)
        frame_footer.pack(side="bottom", fill="x")
        lbl_copy = tk.Label(frame_footer, 
                            text=f"© 2025 Developed by {self.author_name}. All rights reserved. | {self.app_version}",
                            font=("Segoe UI", 8), bg="#e9ecef", fg="#6c757d")
        lbl_copy.pack(pady=5)

    def show_guide(self):
        msg = """
        HƯỚNG DẪN SỬ DỤNG:
        1. Dán link video vào ô nhập liệu.
        2. Bấm 'Kiểm tra' để xem trước video.
        3. Chọn định dạng (Video MP4 hoặc Nhạc MP3).
        4. Bấm 'BẮT ĐẦU TẢI'.
        
        Lưu ý: Cần kết nối mạng ổn định.
        """
        messagebox.showinfo("Hướng dẫn", msg)

    def show_about(self):
        # Tạo một cửa sổ con (Popup) đẹp hơn messagebox thường
        about_window = tk.Toplevel(self.root)
        about_window.title("Về tác giả")
        about_window.geometry("400x250")
        about_window.resizable(False, False)

        # Tiêu đề App
        tk.Label(about_window, text="Video Downloader", font=("Segoe UI", 16, "bold"), fg="#007bff").pack(pady=(20, 5))
        tk.Label(about_window, text=f"Phiên bản: {self.app_version}", font=("Segoe UI", 10, "italic")).pack()

        # Thông tin Dev
        tk.Label(about_window, text=f"Phát triển bởi: {self.author_name}", font=("Segoe UI", 11, "bold")).pack(pady=(20, 5))
        tk.Label(about_window, text="Chuyên cung cấp giải pháp phần mềm & Web", font=("Segoe UI", 10)).pack()

        # Nút liên hệ
        btn_contact = ttk.Button(about_window, text="Liên hệ tác giả", command=lambda: webbrowser.open(self.contact_link))
        btn_contact.pack(pady=20)


    def log(self, message):
        self.log_box.config(state='normal')
        time_str = datetime.datetime.now().strftime('%H:%M:%S')
        self.log_box.insert(tk.END, f"[{time_str}] {message}\n")
        self.log_box.see(tk.END)
        self.log_box.config(state='disabled')

    def paste_link(self):
        try:
            self.entry_url.delete(0, tk.END)
            self.entry_url.insert(0, self.root.clipboard_get())
        except: pass

    def browse_folder(self):
        f = filedialog.askdirectory()
        if f:
            self.save_path = f
            self.entry_path.delete(0, tk.END)
            self.entry_path.insert(0, self.save_path)

    def start_check_info_thread(self):
        url = self.entry_url.get()
        if not url: return
        self.lbl_status.config(text="Đang lấy dữ liệu...", foreground="orange")
        threading.Thread(target=self.check_info, args=(url,), daemon=True).start()

    def check_info(self, url):
        try:
            opts = {'quiet': True, 'extractor_args': {'youtube': {'player_client': ['android', 'web']}}}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                self.root.after(0, self.update_info_ui, info)
        except Exception as e:
            self.root.after(0, lambda: self.log(f"Lỗi Info: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("Lỗi", "Không lấy được thông tin video."))

    def update_info_ui(self, info):
        self.lbl_title.config(text=f"Tiêu đề: {info.get('title', 'Unknown')}")
        self.lbl_duration.config(text=f"Thời lượng: {info.get('duration_string', 'N/A')}")
        self.lbl_source.config(text=f"Nguồn: {info.get('extractor_key', 'Web')}")
        self.log(f"Đã tìm thấy: {info.get('title')}")
        self.lbl_status.config(text="Sẵn sàng tải.", foreground="green")
        
        thumb_url = info.get('thumbnail')
        if thumb_url:
            try:
                raw = urllib.request.urlopen(thumb_url).read()
                im = Image.open(io.BytesIO(raw))
                im = im.resize((160, 90), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(im)
                self.lbl_thumbnail.config(image=photo, text="")
                self.lbl_thumbnail.image = photo
            except: pass

    def get_format_string(self):
        quality_map = {
            "Best (Max)": "bestvideo+bestaudio/best",
            "4K (2160p)": "bestvideo[height<=2160]+bestaudio/best[height<=2160]",
            "2K (1440p)": "bestvideo[height<=1440]+bestaudio/best[height<=1440]",
            "Full HD (1080p)": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "HD (720p)": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "SD (480p)": "bestvideo[height<=480]+bestaudio/best[height<=480]",
            "Low (360p)": "bestvideo[height<=360]+bestaudio/best[height<=360]"
        }
        return quality_map.get(self.cbo_quality.get(), "bestvideo+bestaudio/best")

    def start_download_thread(self):
        url = self.entry_url.get()
        if not url:
            messagebox.showwarning("!", "Chưa nhập Link")
            return
        
        self.btn_download.config(state="disabled", text="ĐANG KẾT NỐI...")
        self.progress_var.set(0)
        # Reset labels
        self.lbl_speed.config(text="🚀 Tốc độ: ...")
        self.lbl_eta.config(text="⏳ Còn lại: ...")
        
        threading.Thread(target=self.download_process, args=(url,), daemon=True).start()

    def download_process(self, url):
        self.log(f"Bắt đầu: {url}")
        
        if self.format_var.get() == 'audio':
            fmt_str = 'bestaudio/best'
            self.log("Mode: Audio MP3")
        else:
            fmt_str = self.get_format_string()
            self.log(f"Mode: Video | {self.cbo_quality.get()}")

        opts = {
            'outtmpl': f'{self.save_path}/%(title)s.%(ext)s',
            'progress_hooks': [self.progress_hook], # Gọi hàm xử lý tiến trình mới
            'noplaylist': True,
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
            'format': fmt_str,
        }

        if self.format_var.get() == 'audio':
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            
            self.root.after(0, lambda: messagebox.showinfo("Thành công", "Tải hoàn tất!"))
            self.root.after(0, lambda: self.lbl_status.config(text="Hoàn tất!", foreground="green"))
            self.log("XONG.")
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Lỗi", str(e)))
            self.log(f"ERR: {str(e)}")
        finally:
            self.root.after(0, lambda: self.btn_download.config(state="normal", text="BẮT ĐẦU TẢI NGAY"))

if __name__ == "__main__":
    
    root = tk.Tk()
    app = UniversalDownloaderApp(root)

    root.mainloop()
