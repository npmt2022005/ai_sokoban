# benchmark.py
import os
import glob
import time
import multiprocessing  # Sử dụng tiến trình độc lập để khống chế thời gian thực thi
import pandas as pd
from backend.core_logic import SokobanGame
from backend.solver_1 import bfs_solver, a_star_solver, a_star_push_based

# Hàm bọc để chạy thuật toán trong một tiến trình riêng biệt nhằm kiểm soát Timeout
def worker_solver(algo_func, file_path, return_dict):
    try:
        game = SokobanGame(file_path)
        start_time = time.time()
        result = algo_func(game)
        elapsed = (time.time() - start_time) * 1000 # Đổi sang ms
        
        if result and result.get("status") == "Success":
            return_dict["status"] = "Thành công"
            return_dict["exec_time"] = round(result.get("execution_time_ms", elapsed), 2)
            return_dict["nodes_gen"] = result.get("nodes_generated", 0)
            return_dict["mem_queue"] = result.get("memory_in_queue", 0)
            return_dict["steps_count"] = len(result.get("path", []))
        else:
            return_dict["status"] = "Thất bại"
    except Exception as e:
        return_dict["status"] = f"Lỗi: {str(e)}"

def run_performance_benchmark(map_dir='data/maps', output_csv='performance_report.csv', timeout_seconds=5):
    """
    Hệ thống đo đạc hiệu năng tích hợp bộ lọc ngắt Timeout tự động.
    """
    print("="*20 + " KHỞI CHẠY HỆ THỐNG ĐO ĐẠC HIỆU NĂNG THỰC NGHIỆM V2 " + "="*20)
    
    map_files = glob.glob(os.path.join(map_dir, "level*.txt"))
    # Sắp xếp tên file map theo đúng thứ tự số học tự nhiên
    map_files.sort(key=lambda f: [int(s) if s.isdigit() else s for s in glob.re.split(r'(\d+)', f)] if hasattr(glob, 're') else f)
    
    if not map_files:
        print(f"❌ Không tìm thấy file map nào tại: {map_dir}")
        return

    algorithms = [
        {"name": "BFS Solver", "func": bfs_solver},
        {"name": "A* Standard", "func": a_star_solver},
        {"name": "Push-based A*", "func": a_star_push_based}
    ]

    raw_statistics = []

    for file_path in map_files:
        map_name = os.path.basename(file_path)
        print(f"\n🎮 Đang kiểm thử hiệu năng trên: {map_name}")
        
        for algo in algorithms:
            # Khởi tạo bộ nhớ chia sẻ giữa các tiến trình
            manager = multiprocessing.Manager()
            return_dict = manager.dict()
            return_dict["status"] = "Timeout" # Mặc định nếu bị treo luồng là Timeout
            return_dict["exec_time"] = None
            return_dict["nodes_gen"] = None
            return_dict["mem_queue"] = None
            return_dict["steps_count"] = None

            # Khởi chạy bộ giải ngầm trong một Process độc lập
            p = multiprocessing.Process(target=worker_solver, args=(algo["func"], file_path, return_dict))
            p.start()
            
            # Chờ tiến trình xử lý trong giới hạn giây cho phép (Ví dụ: 5 giây)
            p.join(timeout=timeout_seconds)
            
            if p.is_alive():
                p.terminate() # Ép buộc đóng tiến trình nếu vượt quá thời gian cho phép
                p.join()
                print(f"   ⚠️  [{algo['name']}] -> 🛑 Bị ngắt do quá thời gian giới hạn ({timeout_seconds}s)!")
            else:
                if return_dict["status"] == "Thành công":
                    print(f"   🔹 [{algo['name']}] -> Thời gian: {return_dict['exec_time']} ms | Nút: {return_dict['nodes_gen']} | Bước: {return_dict['steps_count']}")
                else:
                    print(f"   🔹 [{algo['name']}] -> Trạng thái: {return_dict['status']}")

            # Lưu bản ghi dữ liệu (kể cả khi bị Timeout)
            record = {
                "Màn chơi (Map)": map_name,
                "Thuật toán (Algorithm)": algo["name"],
                "Trạng thái": "Quá tải (Timeout)" if return_dict["status"] == "Timeout" else return_dict["status"],
                "Thời gian xử lý (ms)": return_dict["exec_time"],
                "Số nút đã duyệt (States Generated)": return_dict["nodes_gen"],
                "Bộ nhớ hàng đợi (Memory In Queue)": return_dict["mem_queue"],
                "Tổng số bước giải (Steps)": return_dict["steps_count"]
            }
            raw_statistics.append(record)
            
            # Kỹ thuật an toàn: Ghi file CSV liên tục sau mỗi lượt chạy để phòng ngừa rủi ro treo máy
            df_temp = pd.DataFrame(raw_statistics)
            df_temp.to_csv(output_csv, index=False, encoding='utf-8-sig')

    print("\n" + "="*25 + " HOÀN THÀNH XUẤT DỮ LIỆU THỐNG KÊ " + "="*25)
    print(f"🎉 Báo cáo toàn diện đã được cập nhật tại: {output_csv}")

if __name__ == "__main__":
    # Đặt giới hạn 5 giây cho mỗi thuật toán trên 1 map. Có thể tăng lên 10 tùy cấu hình máy.
    run_performance_benchmark(timeout_seconds=5)