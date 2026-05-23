# plot_charts.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re  # Thư viện Regular Expression giúp bốc tách số từ chuỗi text

def draw_sokoban_charts(csv_file='performance_report.csv'):
    # 1. Đọc dữ liệu từ file dữ liệu thực nghiệm CSV
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"❌ Không tìm thấy file {csv_file}! Hãy chắc chắn rằng bạn đã chạy benchmark.py trước.")
        return
    
    # 2. Xử lý dữ liệu: Loại bỏ các dòng trống hoặc bị Timeout để tránh lỗi khi dựng đồ thị
    df_clean = df.dropna(subset=['Thời gian xử lý (ms)', 'Số nút đã duyệt (States Generated)']).copy()

    if df_clean.empty:
        print("⚠️ Không có dữ liệu hợp lệ (hoặc tất cả đều bị Timeout) để vẽ biểu đồ!")
        return

    # --- THUẬT TOÁN CHUẨN HÓA TÊN MÀN CHƠI THÀNH SỐ ID (1, 2, 3...) ---
    def extract_map_number(name):
        if not isinstance(name, str):
            return "ERR"
        # Tìm kiếm chuỗi số tự nhiên đầu tiên xuất hiện (ví dụ: 'level32.txt' -> '32')
        match = re.search(r'\d+', name)
        if match:
            return match.group(0)
        return name

    # Tạo một cột mới có tên là 'Map ID' chỉ chứa số thứ tự thu gọn
    df_clean['Map ID'] = df_clean['Màn chơi (Map)'].apply(extract_map_number)

    # Chuyển đổi kiểu dữ liệu sang số nguyên (int) để sắp xếp trục X theo đúng thứ tự 1, 2, 3... thay vì thứ tự chữ (1, 10, 2...)
    df_clean['Sort ID'] = df_clean['Map ID'].astype(int)
    df_clean = df_clean.sort_values(by=['Sort ID', 'Thuật toán (Algorithm)'])
    # ------------------------------------------------------------------

    # Thiết lập giao diện hiển thị cho Matplotlib và Seaborn
    sns.set_theme(style="whitegrid")
    plt.rcParams['font.family'] = 'sans-serif'
    
    # =============================================================
    # BIỂU ĐỒ 1: SO SÁNH THỜI GIAN XỬ LÝ (PROCESSING TIME)
    # =============================================================
    plt.figure(figsize=(12, 6))
    
    ax1 = sns.barplot(
        data=df_clean, 
        x="Map ID",                   # Sử dụng tên trục X đã rút gọn
        y="Thời gian xử lý (ms)", 
        hue="Thuật toán (Algorithm)",
        palette="muted"
    )
    
    plt.xticks(rotation=0, fontsize=10)  # Giữ chữ nằm ngang (0 độ) giúp thoáng mắt, không bị lệch chữ
    plt.yticks(fontsize=10)
    plt.yscale("log")                 # Sử dụng thang đo log để phân tách rõ mili-giây và micro-giây
    
    plt.title("Biểu đồ so sánh Thời gian xử lý giữa các Thuật toán AI (ms)", fontsize=14, fontweight='bold')
    plt.xlabel("Danh sách Màn chơi (Map ID)", fontsize=12)
    plt.ylabel("Thời gian thực thi (mili-giây - Thang Log)", fontsize=12)
    plt.legend(title="Thuật toán (Algorithm)", loc='upper left', fontsize=10)
    plt.tight_layout()
    
    plt.savefig("chart_processing_time.png", dpi=300)
    print("🎉 Đã xuất biểu đồ thời gian xử lý ngắn gọn: chart_processing_time.png")
    plt.close()

    # =============================================================
    # BIỂU ĐỒ 2: SO SÁNH SỐ NÚT DUYỆT (STATES GENERATED)
    # =============================================================
    plt.figure(figsize=(12, 6))
    
    ax2 = sns.barplot(
        data=df_clean, 
        x="Map ID",                   # Sử dụng tên trục X đã rút gọn
        y="Số nút đã duyệt (States Generated)", 
        hue="Thuật toán (Algorithm)",
        palette="muted"               # Giữ màu dịu giống hệt hình ảnh mẫu
    )
    
    plt.xticks(rotation=0, fontsize=10)  # Để nhãn Map nằm ngang phẳng lặng như ảnh mẫu
    plt.yticks(fontsize=10)
    plt.yscale("log")                 # Dùng thang đo Logarithm bắt buộc cho số lượng nút cây trạng thái
    
    plt.title("Biểu đồ so sánh Không gian Trạng thái bung ra (States Generated)", fontsize=14, fontweight='bold')
    plt.xlabel("Danh sách Màn chơi (Map ID)", fontsize=12)
    plt.ylabel("Số lượng trạng thái (Nút cây - Thang Log)", fontsize=12)
    plt.legend(title="Thuật toán (Algorithm)", loc='upper left', fontsize=10)
    plt.tight_layout()
    
    plt.savefig("chart_states_generated.png", dpi=300)
    print("🎉 Đã xuất biểu đồ số lượng nút cây ngắn gọn: chart_states_generated.png")
    plt.close()

if __name__ == "__main__":
    # Kích hoạt hàm xử lý vẽ biểu đồ
    draw_sokoban_charts()