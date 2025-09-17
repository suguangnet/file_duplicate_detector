import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import hashlib
import shutil
import threading
import time

class FileDuplicateDetector:
    def __init__(self, root):
        self.root = root
        self.root.title("文件重复检测清理")
        # 调整窗体大小，按100%比例稍调小一点
        self.root.geometry("900x650")
        
        # 居中显示窗口
        self.center_window()
        
        # 存储文件信息
        self.file_list = []
        self.duplicate_groups = []
        
        # 文件扩展名过滤器（支持多个后缀）
        self.extension_filters = [".rar"]
        
        # 控制扫描和检测的标志
        self.is_scanning = False
        
        self.create_widgets()
        
    def center_window(self):
        """将窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # 标题
        #title_label = ttk.Label(main_frame, text="文件重复检测工具", font=("Arial", 16, "bold"))
        #title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        file_frame.columnconfigure(2, weight=1)
        
        ttk.Label(file_frame, text="目录路径:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.file_path_var = tk.StringVar()
        # 增加输入框宽度
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=60)
        file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        browse_btn = ttk.Button(file_frame, text="浏览目录", command=self.browse_directory)
        browse_btn.grid(row=0, column=2, padx=(0, 5))
        
        # 扫描按钮（合并了扫描和检测功能）
        self.scan_detect_btn = ttk.Button(file_frame, text="扫描检测重复文件", command=self.scan_and_detect)
        self.scan_detect_btn.grid(row=0, column=3, padx=(0, 5))
        
        # 扩展名筛选
        ttk.Label(file_frame, text="文件扩展名:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.extension_var = tk.StringVar(value=".rar")
        # 增加扩展名输入框宽度，支持多个后缀输入
        extension_entry = ttk.Entry(file_frame, textvariable=self.extension_var, width=50)
        extension_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(0, 5), pady=(5, 0))
        ttk.Label(file_frame, text="多个后缀用逗号分隔，如: .rar,.zip,.7z").grid(row=1, column=3, sticky=tk.W, padx=(5, 0), pady=(5, 0))
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(file_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.progress_label = ttk.Label(file_frame, text="就绪")
        self.progress_label.grid(row=3, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
        
        # 文件列表区域
        list_frame = ttk.LabelFrame(main_frame, text="文件列表", padding="10")
        list_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 创建Treeview来显示文件列表
        columns = ("文件名", "路径", "大小", "修改时间")
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        # 设置列标题
        for col in columns:
            self.file_tree.heading(col, text=col)
            self.file_tree.column(col, width=180)
        
        # 添加滚动条
        file_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=file_scrollbar.set)
        
        self.file_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        file_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 删除选中文件按钮
        remove_btn = ttk.Button(list_frame, text="删除选中文件", command=self.remove_selected_file)
        remove_btn.grid(row=1, column=0, pady=(10, 0), sticky=tk.W)
        
        # 清理重复文件按钮
        clear_btn = ttk.Button(list_frame, text="清理重复文件", command=self.clear_duplicates)
        clear_btn.grid(row=1, column=0, pady=(10, 0), sticky=tk.E)
        
        # 重复文件结果显示区域
        result_frame = ttk.LabelFrame(main_frame, text="重复文件结果", padding="10")
        result_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # 创建Treeview来显示重复文件
        result_columns = ("组号", "文件名", "路径", "大小")
        self.result_tree = ttk.Treeview(result_frame, columns=result_columns, show="headings", height=8)
        
        # 设置列标题
        for col in result_columns:
            self.result_tree.heading(col, text=col)
            self.result_tree.column(col, width=180)
        
        # 添加滚动条
        result_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=result_scrollbar.set)
        
        self.result_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def browse_directory(self):
        """浏览目录"""
        dir_path = filedialog.askdirectory(title="选择目录")
        if dir_path:
            self.file_path_var.set(dir_path)
    
    def parse_extensions(self, extension_str):
        """解析扩展名字符串，支持多个后缀"""
        if not extension_str.strip():
            return []
        
        extensions = []
        for ext in extension_str.split(','):
            ext = ext.strip()
            if ext:
                if not ext.startswith('.'):
                    ext = '.' + ext
                extensions.append(ext.lower())
        return extensions
    
    def scan_and_detect(self):
        """扫描目录并检测重复文件（合并功能）"""
        if self.is_scanning:
            messagebox.showwarning("警告", "正在扫描中，请稍后再试")
            return
            
        dir_path = self.file_path_var.get()
        if not dir_path:
            messagebox.showwarning("警告", "请先选择目录")
            return
            
        if not os.path.exists(dir_path):
            messagebox.showerror("错误", "目录不存在")
            return
            
        # 获取扩展名过滤器（支持多个后缀）
        extension_str = self.extension_var.get()
        self.extension_filters = self.parse_extensions(extension_str)
        
        # 如果没有输入扩展名，则扫描所有文件
        if not self.extension_filters:
            if not messagebox.askyesno("确认", "未指定文件扩展名，将扫描所有文件，可能需要较长时间，是否继续？"):
                return
        
        # 在新线程中执行扫描和检测，避免界面卡死
        self.is_scanning = True
        self.scan_detect_btn.config(state="disabled", text="扫描中...")
        scan_thread = threading.Thread(target=self._scan_and_detect_thread, args=(dir_path,))
        scan_thread.daemon = True
        scan_thread.start()
    
    def _scan_and_detect_thread(self, dir_path):
        """在后台线程中执行扫描和检测"""
        try:
            # 扫描文件
            self._scan_files(dir_path)
            
            # 如果扫描成功且有文件，则检测重复文件
            if self.file_list and self.is_scanning:
                self.root.after(100, self._detect_duplicates_after_scan)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"扫描过程中出错: {str(e)}"))
            self.root.after(0, self._reset_scan_state)
    
    def _scan_files(self, dir_path):
        """扫描目录中的文件"""
        self.root.after(0, lambda: self.progress_label.config(text="正在扫描目录..."))
        
        # 清空之前的文件列表
        self.file_list = []
        self.root.after(0, self._clear_file_tree)
        
        file_count = 0
        total_files = self._count_files(dir_path)
        
        if total_files == 0:
            self.root.after(0, lambda: self.progress_label.config(text="目录中没有符合条件的文件"))
            self.root.after(0, self._reset_scan_state)
            return
            
        try:
            for root, dirs, files in os.walk(dir_path):
                # 包括隐藏目录
                # dirs[:] = [d for d in dirs if not d.startswith('.')]  # 可选：排除隐藏目录
                for file in files:
                    if not self.is_scanning:  # 如果用户取消了扫描
                        return
                        
                    if file.startswith('.'):  # 跳过隐藏文件
                        continue
                    
                    # 支持多个后缀过滤
                    if self.extension_filters:
                        matched = False
                        for ext in self.extension_filters:
                            if file.lower().endswith(ext):
                                matched = True
                                break
                        if not matched:
                            continue
                    
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        # 检查是否已添加
                        if file_path not in [f['path'] for f in self.file_list]:
                            # 获取文件信息
                            file_info = self.get_file_info(file_path)
                            self.file_list.append(file_info)
                            file_count += 1
                            
                            # 添加到Treeview
                            self.root.after(0, self._add_file_to_tree, file_info)
                            
                            # 更新进度（每扫描10个文件更新一次进度条）
                            if file_count % 10 == 0 or file_count == total_files:
                                progress = (file_count / total_files) * 100
                                self.root.after(0, lambda p=progress: self.progress_var.set(p))
                                self.root.after(0, lambda c=file_count, t=total_files: self.progress_label.config(text=f"已扫描 {c}/{t} 个文件"))
                                
                                # 添加短暂延迟以减少CPU占用
                                time.sleep(0.01)
            
            self.root.after(0, lambda: self.progress_label.config(text=f"扫描完成，共找到 {file_count} 个文件"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"扫描目录时出错: {str(e)}"))
    
    def _count_files(self, dir_path):
        """预估目录中的文件数量"""
        count = 0
        try:
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    if file.startswith('.'):  # 跳过隐藏文件
                        continue
                    
                    # 支持多个后缀过滤
                    if self.extension_filters:
                        matched = False
                        for ext in self.extension_filters:
                            if file.lower().endswith(ext):
                                matched = True
                                break
                        if not matched:
                            continue
                    
                    count += 1
        except:
            pass
        return count
    
    def _clear_file_tree(self):
        """清空文件列表显示"""
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
    
    def _add_file_to_tree(self, file_info):
        """添加文件到Treeview"""
        self.file_tree.insert("", tk.END, values=(
            file_info['name'],
            file_info['path'],
            file_info['size'],
            file_info['modified']
        ))
    
    def _detect_duplicates_after_scan(self):
        """扫描完成后检测重复文件"""
        if not self.is_scanning:
            return
            
        self.root.after(0, lambda: self.progress_label.config(text="正在检测重复文件..."))
        self.root.after(0, lambda: self.progress_var.set(0))
        
        # 检测重复文件
        if len(self.file_list) < 2:
            self.root.after(0, lambda: messagebox.showwarning("警告", "至少需要两个文件才能检测重复"))
            self.root.after(0, self._reset_scan_state)
            return
        
        # 清空之前的结果
        self.root.after(0, self._clear_result_tree)
        
        # 计算每个文件的哈希值
        file_hashes = {}
        total_files = len(self.file_list)
        
        for i, file_info in enumerate(self.file_list):
            if not self.is_scanning:  # 如果用户取消了操作
                return
                
            file_hash = self.calculate_file_hash(file_info['path'])
            if file_hash:
                if file_hash not in file_hashes:
                    file_hashes[file_hash] = []
                file_hashes[file_hash].append(file_info)
            
            # 更新进度
            progress = ((i + 1) / total_files) * 100
            self.root.after(0, lambda p=progress: self.progress_var.set(p))
            self.root.after(0, lambda i=i, t=total_files: self.progress_label.config(text=f"正在检测重复文件 {i+1}/{t}"))
            
            # 添加短暂延迟以减少CPU占用
            time.sleep(0.01)
        
        # 找出重复的文件组
        self.duplicate_groups = []
        group_id = 1
        for file_hash, files in file_hashes.items():
            if len(files) > 1:  # 重复文件
                self.duplicate_groups.append({
                    'group_id': group_id,
                    'hash': file_hash,
                    'files': files
                })
                group_id += 1
        
        # 显示重复文件
        total_duplicates = 0
        for group in self.duplicate_groups:
            for file_info in group['files']:
                self.root.after(0, self._add_duplicate_to_tree, group['group_id'], file_info)
                total_duplicates += 1
        
        self.root.after(0, lambda: self.status_var.set(f"检测完成，发现 {len(self.duplicate_groups)} 组重复文件，共 {total_duplicates} 个重复文件"))
        self.root.after(0, lambda: self.progress_label.config(text=f"检测完成，发现 {len(self.duplicate_groups)} 组重复文件"))
        
        if len(self.duplicate_groups) == 0:
            self.root.after(0, lambda: messagebox.showinfo("结果", "未发现重复文件"))
        
        self.root.after(0, self._reset_scan_state)
    
    def _clear_result_tree(self):
        """清空重复文件结果显示"""
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
    
    def _add_duplicate_to_tree(self, group_id, file_info):
        """添加重复文件到Treeview"""
        self.result_tree.insert("", tk.END, values=(
            group_id,
            file_info['name'],
            file_info['path'],
            file_info['size']
        ))
    
    def _reset_scan_state(self):
        """重置扫描状态"""
        self.is_scanning = False
        self.scan_detect_btn.config(state="normal", text="扫描并检测重复文件")
        self.progress_var.set(0)
    
    def get_file_info(self, file_path):
        """获取文件信息"""
        stat = os.stat(file_path)
        return {
            'name': os.path.basename(file_path),
            'path': file_path,
            'size': self.format_size(stat.st_size),
            'bytes': stat.st_size,
            'modified': self.format_time(stat.st_mtime)
        }
    
    def format_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def format_time(self, timestamp):
        """格式化时间"""
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
    
    def remove_selected_file(self):
        """删除选中的文件"""
        selected_items = self.file_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择要删除的文件")
            return
            
        # 确认删除
        if not messagebox.askyesno("确认", "确定要删除选中的文件吗？"):
            return
            
        # 删除选中的文件
        for item in selected_items:
            # 获取文件路径
            item_values = self.file_tree.item(item, 'values')
            file_path = item_values[1]
            
            # 从列表中移除
            self.file_list = [f for f in self.file_list if f['path'] != file_path]
            
            # 从Treeview中移除
            self.file_tree.delete(item)
        
        self.status_var.set(f"已删除 {len(selected_items)} 个文件")
    
    def calculate_file_hash(self, file_path):
        """计算文件的MD5哈希值"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                # 分块读取文件以避免大文件占用过多内存
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"计算文件哈希时出错: {e}")
            return None
    
    def clear_duplicates(self):
        """清理重复文件"""
        if not self.duplicate_groups:
            messagebox.showwarning("警告", "请先检测重复文件")
            return
            
        # 确认清理
        if not messagebox.askyesno("确认", f"确定要清理重复文件吗？将保留每组中的第一个文件，删除其余文件。"):
            return
            
        deleted_count = 0
        error_count = 0
        
        self.status_var.set("正在清理重复文件...")
        
        # 对于每组重复文件，保留第一个，删除其余的
        for group in self.duplicate_groups:
            files = group['files']
            # 保留第一个文件，删除其余文件
            for file_info in files[1:]:
                try:
                    os.remove(file_info['path'])
                    deleted_count += 1
                    # 从文件列表中移除
                    self.file_list = [f for f in self.file_list if f['path'] != file_info['path']]
                except Exception as e:
                    print(f"删除文件时出错: {e}")
                    error_count += 1
        
        # 更新文件列表显示
        self._clear_file_tree()
        for file_info in self.file_list:
            self.file_tree.insert("", tk.END, values=(
                file_info['name'],
                file_info['path'],
                file_info['size'],
                file_info['modified']
            ))
        
        # 清空重复文件结果
        self._clear_result_tree()
        
        self.duplicate_groups = []
        
        if error_count == 0:
            messagebox.showinfo("完成", f"清理完成，成功删除 {deleted_count} 个重复文件")
            self.status_var.set(f"清理完成，成功删除 {deleted_count} 个重复文件")
        else:
            messagebox.showwarning("完成", f"清理完成，成功删除 {deleted_count} 个重复文件，{error_count} 个文件删除失败")
            self.status_var.set(f"清理完成，成功删除 {deleted_count} 个重复文件，{error_count} 个文件删除失败")

def main():
    root = tk.Tk()
    app = FileDuplicateDetector(root)
    root.mainloop()

if __name__ == "__main__":
    main()