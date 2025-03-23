import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import qrcode
from PIL import Image, ImageTk
import cv2
from pyzbar.pyzbar import decode
import os
import webbrowser

class QRCodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Kod Üretici ve Okuyucu")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Ana stil teması
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TButton", background="#4CAF50", foreground="black", font=("Arial", 10, "bold"), padding=10)
        self.style.configure("TLabel", background="#f0f0f0", font=("Arial", 11))
        self.style.configure("TEntry", font=("Arial", 11))
        self.style.configure("Header.TLabel", font=("Arial", 16, "bold"))
        
        # Ana notebook oluşturma
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Üretici Sekmesi
        self.generator_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.generator_frame, text="QR Kod Üret")
        self.setup_generator()
        
        # Okuyucu Sekmesi
        self.reader_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.reader_frame, text="QR Kod Oku")
        self.setup_reader()
        
        # Sonuç panosu
        self.result_frame = ttk.Frame(root)
        self.result_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.result_label = ttk.Label(self.result_frame, text="Durum:", style="TLabel")
        self.result_label.pack(side=tk.LEFT, padx=5)
        
        self.result_value = ttk.Label(self.result_frame, text="Hazır", style="TLabel")
        self.result_value.pack(side=tk.LEFT, padx=5)
        
        # Footer
        footer_frame = ttk.Frame(root)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
        footer_label = ttk.Label(footer_frame, text="© 2025 QR Kod Uygulaması", style="TLabel")
        footer_label.pack()
    
    def setup_generator(self):
        # İçerik frame'i
        content_frame = ttk.Frame(self.generator_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Başlık
        header = ttk.Label(content_frame, text="QR Kod Oluştur", style="Header.TLabel")
        header.pack(pady=10)
        
        # Giriş alanı
        input_frame = ttk.Frame(content_frame)
        input_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(input_frame, text="İçerik:").pack(side=tk.LEFT, padx=5)
        self.qr_content = tk.StringVar()
        
        entry = ttk.Entry(input_frame, textvariable=self.qr_content, width=50)
        entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        entry.focus()
        
        # QR boyut ayarı
        size_frame = ttk.Frame(content_frame)
        size_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(size_frame, text="Boyut:").pack(side=tk.LEFT, padx=5)
        self.qr_size = tk.IntVar(value=5)
        
        size_scale = ttk.Scale(size_frame, from_=1, to=10, variable=self.qr_size, 
                             orient=tk.HORIZONTAL, length=200)
        size_scale.pack(side=tk.LEFT, padx=5)
        
        size_value = ttk.Label(size_frame, textvariable=self.qr_size)
        size_value.pack(side=tk.LEFT, padx=5)
        
        # Butonlar
        btn_frame = ttk.Frame(content_frame)
        btn_frame.pack(fill=tk.X, pady=20)
        
        generate_btn = ttk.Button(btn_frame, text="QR Kod Oluştur", command=self.generate_qr)
        generate_btn.pack(side=tk.LEFT, padx=5)
        
        save_btn = ttk.Button(btn_frame, text="Kaydet", command=self.save_qr)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # QR görüntüleme alanı
        self.qr_display_frame = ttk.LabelFrame(content_frame, text="QR Kod")
        self.qr_display_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.qr_image_label = ttk.Label(self.qr_display_frame)
        self.qr_image_label.pack(pady=10, padx=10)
        
        self.current_qr_image = None
    
    def setup_reader(self):
        # İçerik frame'i
        content_frame = ttk.Frame(self.reader_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Başlık
        header = ttk.Label(content_frame, text="QR Kod Oku", style="Header.TLabel")
        header.pack(pady=10)
        
        # Butonlar
        btn_frame = ttk.Frame(content_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        browse_btn = ttk.Button(btn_frame, text="Dosya Seç", command=self.browse_qr)
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        camera_btn = ttk.Button(btn_frame, text="Kamera ile Oku", command=self.read_qr_from_camera)
        camera_btn.pack(side=tk.LEFT, padx=5)
        
        # QR görüntüleme alanı
        self.reader_display_frame = ttk.LabelFrame(content_frame, text="QR Kod Görüntüsü")
        self.reader_display_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.reader_image_label = ttk.Label(self.reader_display_frame)
        self.reader_image_label.pack(pady=10, padx=10)
        
        # QR içerik alanı
        content_display_frame = ttk.LabelFrame(content_frame, text="QR Kod İçeriği")
        content_display_frame.pack(fill=tk.X, pady=10)
        
        self.content_text = tk.Text(content_display_frame, height=5, width=50, wrap=tk.WORD)
        self.content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        action_frame = ttk.Frame(content_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        copy_btn = ttk.Button(action_frame, text="Kopyala", command=self.copy_content)
        copy_btn.pack(side=tk.LEFT, padx=5)
        
        open_url_btn = ttk.Button(action_frame, text="URL Aç", command=self.open_url)
        open_url_btn.pack(side=tk.LEFT, padx=5)
    
    def generate_qr(self):
        content = self.qr_content.get().strip()
        
        if not content:
            messagebox.showwarning("Uyarı", "QR kod için içerik girmelisiniz!")
            return
        
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=self.qr_size.get() * 10,
                border=4,
            )
            qr.add_data(content)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            
            # Görüntüyü Tkinter'a uyumlu hale getir
            self.current_qr_image = ImageTk.PhotoImage(img)
            
            # Görüntüyü göster
            self.qr_image_label.config(image=self.current_qr_image)
            
            self.result_value.config(text=f"QR Kod oluşturuldu: {content[:30]}...")
            
            # Orijinal PIL görüntüsünü kaydet
            self.pil_image = img
            
        except Exception as e:
            messagebox.showerror("Hata", f"QR kod oluşturulurken bir hata oluştu: {str(e)}")
    
    def save_qr(self):
        if not hasattr(self, 'pil_image') or self.pil_image is None:
            messagebox.showwarning("Uyarı", "Kaydedilecek bir QR kod yok!")
            return
        
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG Dosyası", "*.png"), ("JPEG Dosyası", "*.jpg"), ("Tüm Dosyalar", "*.*")]
            )
            
            if file_path:
                self.pil_image.save(file_path)
                self.result_value.config(text=f"QR Kod kaydedildi: {os.path.basename(file_path)}")
                messagebox.showinfo("Başarılı", f"QR kod {file_path} dosyasına kaydedildi.")
        
        except Exception as e:
            messagebox.showerror("Hata", f"QR kod kaydedilirken bir hata oluştu: {str(e)}")
    
    def browse_qr(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Resim Dosyaları", "*.png *.jpg *.jpeg *.bmp *.gif"), ("Tüm Dosyalar", "*.*")]
        )
        
        if file_path:
            self.read_qr_from_file(file_path)
    
    def read_qr_from_file(self, file_path):
        try:
            # Görüntüyü yükle
            image = Image.open(file_path)
            
            # Görüntüyü uygun boyuta getir
            image = self.resize_image(image, 300)
            
            # Görüntüyü Tkinter'a uygun hale getir
            tk_image = ImageTk.PhotoImage(image)
            self.reader_image_label.config(image=tk_image)
            self.reader_image_label.image = tk_image  # Referansı koru
            
            # QR kodu çöz
            cv_image = cv2.imread(file_path)
            self.decode_qr(cv_image, file_path)
            
        except Exception as e:
            messagebox.showerror("Hata", f"Görüntü işlenirken bir hata oluştu: {str(e)}")
    
    def read_qr_from_camera(self):
        try:
            # Kamera aç
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                messagebox.showerror("Hata", "Kamera açılamadı!")
                return
            
            messagebox.showinfo("Bilgi", "QR kodu kameraya gösterin ve okutmak için 'q' tuşuna basın. İptal etmek için 'ESC' tuşuna basın.")
            
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # QR kodu ara
                decoded_objects = decode(frame)
                
                # Bulunan QR kodlarını çerçeve içine al
                for obj in decoded_objects:
                    points = obj.polygon
                    if len(points) > 4:
                        hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                        cv2.polylines(frame, [hull], True, (0, 255, 0), 3)
                    else:
                        cv2.polylines(frame, [np.array(points, dtype=np.int32)], True, (0, 255, 0), 3)
                
                # Görüntüyü göster
                cv2.imshow("QR Kod Tarayıcı", frame)
                
                key = cv2.waitKey(1)
                # Q tuşuna basıldığında
                if key == ord('q') and decoded_objects:
                    # İlk QR kodu al
                    self.decode_qr_from_objects(decoded_objects, frame)
                    break
                # ESC tuşuna basıldığında
                elif key == 27:  # ESC
                    break
            
            # Kaynakları serbest bırak
            cap.release()
            cv2.destroyAllWindows()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Kamera işlenirken bir hata oluştu: {str(e)}")
    
    def decode_qr(self, cv_image, source):
        decoded_objects = decode(cv_image)
        
        if decoded_objects:
            self.decode_qr_from_objects(decoded_objects, cv_image)
        else:
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(tk.END, "QR kod bulunamadı!")
            self.result_value.config(text=f"QR kod okunamadı: {os.path.basename(source)}")
    
    def decode_qr_from_objects(self, decoded_objects, cv_image):
        qr_data = decoded_objects[0].data.decode('utf-8')
        qr_type = decoded_objects[0].type
        
        # QR içeriğini göster
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(tk.END, qr_data)
        
        # Durumu güncelle
        self.result_value.config(text=f"{qr_type} başarıyla okundu")
        
        # Görüntüyü Tkinter'a uygun hale getir
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        pil_image = self.resize_image(pil_image, 300)
        tk_image = ImageTk.PhotoImage(pil_image)
        
        # Görüntüyü göster
        self.reader_image_label.config(image=tk_image)
        self.reader_image_label.image = tk_image  # Referansı koru
    
    def resize_image(self, image, max_size):
        # En büyük boyutu max_size olacak şekilde oranı koru
        width, height = image.size
        if width > height:
            new_width = max_size
            new_height = int(height * max_size / width)
        else:
            new_height = max_size
            new_width = int(width * max_size / height)
        
        return image.resize((new_width, new_height), Image.LANCZOS)
    
    def copy_content(self):
        content = self.content_text.get(1.0, tk.END).strip()
        
        if content:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.result_value.config(text="İçerik panoya kopyalandı")
        else:
            messagebox.showwarning("Uyarı", "Kopyalanacak içerik yok!")
    
    def open_url(self):
        url = self.content_text.get(1.0, tk.END).strip()
        
        if not url:
            messagebox.showwarning("Uyarı", "Açılacak URL yok!")
            return
        
        # Basit URL kontrolü
        if not (url.startswith("http://") or url.startswith("https://")):
            url = "https://" + url
        
        try:
            webbrowser.open(url)
            self.result_value.config(text=f"URL açıldı: {url[:30]}...")
        except Exception as e:
            messagebox.showerror("Hata", f"URL açılırken bir hata oluştu: {str(e)}")

if __name__ == "__main__":
    # Eksik kütüphaneyi import et
    import numpy as np
    
    root = tk.Tk()
    app = QRCodeApp(root)
    root.mainloop()