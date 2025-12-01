import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import yt_dlp
import threading
import os
import urllib.request
import io
import datetime
import webbrowser

class UniversalDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal Video Downloader - Pro Version")
        self.root.geometry("700x750") # Tăng chiều cao lên chút để chứa thêm nút chọn
        self.root.resizable(False, False)
        
        # --- THÔNG TIN TÁC GIẢ ---
        self.author_name = "Sand"
        self.app_version = "v1.0.0"
        self.contact_link = "https://www.facebook.com/Sandau1204" # Điền link của bạn vào đây

        # Biến toàn cục
        self.save_path = os.getcwd()
        self.video_info = None 

        # --- TẠO MENU BAR ---
        self.create_menu()

        # --- STYLE GIAO DIỆN ---
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Segoe UI", 10), padding=5)
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))

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

        # 3. KHUNG PREVIEW (XEM TRƯỚC)
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

        # 4. KHUNG CÀI ĐẶT (ĐÃ NÂNG CẤP)
        frame_settings = ttk.LabelFrame(root, text=" Cài đặt tải xuống ", padding=10)
        frame_settings.pack(fill="x", padx=15, pady=5)

        # Dòng 1: Chọn thư mục
        frame_path = tk.Frame(frame_settings)
        frame_path.pack(fill="x", pady=2)
        ttk.Label(frame_path, text="Lưu tại: ").pack(side="left")
        self.entry_path = ttk.Entry(frame_path)
        self.entry_path.insert(0, self.save_path)
        self.entry_path.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(frame_path, text="Chọn...", command=self.browse_folder).pack(side="left")

        # Dòng 2: Định dạng & Chất lượng
        frame_options = tk.Frame(frame_settings)
        frame_options.pack(fill="x", pady=(10, 0))

        # Radio button
        self.format_var = tk.StringVar(value="video")
        # Khi chọn Audio/Video sẽ kích hoạt hàm toggle_quality_state
        rb_video = ttk.Radiobutton(frame_options, text="Video (MP4)", variable=self.format_var, value="video", command=self.toggle_quality_state)
        rb_video.pack(side="left", padx=(0, 10))
        
        rb_audio = ttk.Radiobutton(frame_options, text="Âm thanh (MP3)", variable=self.format_var, value="audio", command=self.toggle_quality_state)
        rb_audio.pack(side="left", padx=(0, 20))

        # --- Dropdown chọn chất lượng (MỚI) ---
        ttk.Label(frame_options, text="Chất lượng:").pack(side="left")
        self.quality_var = tk.StringVar()
        self.cbo_quality = ttk.Combobox(frame_options, textvariable=self.quality_var, state="readonly", width=15)
        self.cbo_quality['values'] = ("Best (Max)", "4K (2160p)", "2K (1440p)", "Full HD (1080p)", "HD (720p)", "SD (480p)", "Low (360p)")
        self.cbo_quality.current(0) # Mặc định chọn Best
        self.cbo_quality.pack(side="left", padx=5)

        # 5. KHUNG TIẾN TRÌNH & LOG
        frame_progress = ttk.LabelFrame(root, text=" Tiến trình ", padding=10)
        frame_progress.pack(fill="both", expand=True, padx=15, pady=5)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(frame_progress, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", pady=5)

        self.lbl_status = ttk.Label(frame_progress, text="Sẵn sàng", foreground="#2ecc71")
        self.lbl_status.pack(anchor="w")

        self.log_box = scrolledtext.ScrolledText(frame_progress, height=5, font=("Consolas", 8), state='disabled', bg="#f8f9fa")
        self.log_box.pack(fill="both", expand=True, pady=5)

        # 6. NÚT TẢI
        self.btn_download = tk.Button(root, text="BẮT ĐẦU TẢI NGAY", bg="#007bff", fg="white", 
                                      font=("Segoe UI", 12, "bold"), relief="flat", 
                                      command=self.start_download_thread)
        self.btn_download.pack(fill="x", padx=30, pady=10)

        # 7. FOOTER
        self.create_footer()

    # ================= CÁC HÀM GIAO DIỆN PHỤ =================

    def toggle_quality_state(self):
        """Nếu chọn Audio thì khóa ô chọn chất lượng Video"""
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
        menubar.add_cascade(label="Thông tin & Tác giả", menu=help_menu)
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
        tk.Label(about_window, text="Pro Video Downloader", font=("Segoe UI", 16, "bold"), fg="#007bff").pack(pady=(20, 5))
        tk.Label(about_window, text=f"Phiên bản: {self.app_version}", font=("Segoe UI", 10, "italic")).pack()

        # Thông tin Dev
        tk.Label(about_window, text=f"Phát triển bởi: {self.author_name}", font=("Segoe UI", 11, "bold")).pack(pady=(20, 5))
        tk.Label(about_window, text="Chuyên cung cấp giải pháp phần mềm & Web", font=("Segoe UI", 10)).pack()

        # Nút liên hệ
        btn_contact = ttk.Button(about_window, text="Liên hệ tác giả", command=lambda: webbrowser.open(self.contact_link))
        btn_contact.pack(pady=20)

        # Nút đóng
        ttk.Button(about_window, text="Đóng", command=about_window.destroy).pack()

    # ================= LOGIC XỬ LÝ (CORE) =================

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

    # --- CHECK INFO ---
    def start_check_info_thread(self):
        url = self.entry_url.get()
        if not url: return
        self.lbl_status.config(text="Đang lấy thông tin...", foreground="orange")
        threading.Thread(target=self.check_info, args=(url,), daemon=True).start()

    def check_info(self, url):
        try:
            opts = {'quiet': True, 'extractor_args': {'youtube': {'player_client': ['android', 'web']}}}
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                self.root.after(0, self.update_info_ui, info)
        except Exception as e:
            self.root.after(0, lambda: self.log(f"Lỗi check info: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("Lỗi", "Không thể lấy thông tin video."))

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

    # --- DOWNLOAD LOGIC (NÂNG CẤP) ---
    def get_format_string(self):
        """Xác định chuỗi format dựa trên lựa chọn Combobox"""
        quality_map = {
            "Best (Max)": "bestvideo+bestaudio/best",
            "4K (2160p)": "bestvideo[height<=2160]+bestaudio/best[height<=2160]",
            "2K (1440p)": "bestvideo[height<=1440]+bestaudio/best[height<=1440]",
            "Full HD (1080p)": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "HD (720p)": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "SD (480p)": "bestvideo[height<=480]+bestaudio/best[height<=480]",
            "Low (360p)": "bestvideo[height<=360]+bestaudio/best[height<=360]"
        }
        selection = self.cbo_quality.get()
        return quality_map.get(selection, "bestvideo+bestaudio/best")

    def start_download_thread(self):
        url = self.entry_url.get()
        if not url:
            messagebox.showwarning("!", "Chưa nhập Link")
            return
        
        self.btn_download.config(state="disabled", text="ĐANG TẢI... (Vui lòng đợi)")
        self.progress_var.set(0)
        threading.Thread(target=self.download_process, args=(url,), daemon=True).start()

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%').replace('%','')
            try:
                self.progress_var.set(float(p))
                self.lbl_status.config(text=f"Đang tải: {d.get('_percent_str')} | Tốc độ: {d.get('_speed_str')}", foreground="blue")
            except: pass
        elif d['status'] == 'finished':
            self.lbl_status.config(text="Đang xử lý (Ghép file)...", foreground="#d35400")

    def download_process(self, url):
        self.log(f"Bắt đầu tải: {url}")
        
        # Lấy chuỗi format từ hàm xử lý
        if self.format_var.get() == 'audio':
            fmt_str = 'bestaudio/best'
            self.log("Mode: Audio Only (MP3)")
        else:
            fmt_str = self.get_format_string()
            self.log(f"Mode: Video | Chất lượng: {self.cbo_quality.get()}")

        opts = {
            'outtmpl': f'{self.save_path}/%(title)s.%(ext)s',
            'progress_hooks': [self.progress_hook],
            'noplaylist': True,
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
            'format': fmt_str, # <--- ĐIỂM QUAN TRỌNG: Áp dụng format động
        }

        # Cấu hình convert MP3 nếu chọn Audio
        if self.format_var.get() == 'audio':
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            
            self.root.after(0, lambda: messagebox.showinfo("Thành công", "Đã tải xong!"))
            self.root.after(0, lambda: self.lbl_status.config(text="Hoàn tất!", foreground="green"))
            self.log("Xử lý hoàn tất.")
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Lỗi", "Có lỗi xảy ra. Kiểm tra lại kết nối hoặc FFmpeg."))
            self.log(f"LỖI: {str(e)}")
        finally:
            self.root.after(0, lambda: self.btn_download.config(state="normal", text="BẮT ĐẦU TẢI NGAY"))

if __name__ == "__main__":
    root = tk.Tk()
    app = UniversalDownloaderApp(root)
    root.mainloop()