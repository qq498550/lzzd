"""
廉政意见智答系统 - 打包后入口点
"""
import sys
import os
import webbrowser
import threading
import time
import traceback
import signal

tray_icon = None

def write_log(msg):
    """写入日志"""
    try:
        from app.core.config import settings
        log_file = os.path.join(settings.data_dir, "app.log")
        os.makedirs(settings.data_dir, exist_ok=True)
        with open(log_file, "a", encoding="utf-8") as f:
            from datetime import datetime
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except:
        pass

def show_error(msg):
    """显示错误消息框"""
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, msg, "启动错误", 0x10)
    except:
        print(msg, file=sys.stderr)

def get_icon_path():
    """获取图标路径"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, 'app', 'static', 'favicon.ico')

def create_tray_icon():
    """创建系统托盘图标"""
    global tray_icon
    try:
        from pystray import Icon, Menu, MenuItem
        from PIL import Image, ImageDraw

        icon_path = get_icon_path()
        try:
            if os.path.exists(icon_path):
                icon_image = Image.open(icon_path)
            else:
                icon_image = Image.new('RGB', (64, 64), color=(102, 126, 234))
                draw = ImageDraw.Draw(icon_image)
                draw.ellipse([8, 8, 56, 56], fill=(255, 255, 255))
                draw.text((20, 22), "廉", fill=(102, 126, 234))
        except:
            icon_image = Image.new('RGB', (64, 64), color=(102, 126, 234))

        def open_page(icon=None, item=None):
            try:
                from app.core.config import settings
                url = f"http://127.0.0.1:{settings.port}"
                webbrowser.open(url)
            except:
                pass

        def exit_app(icon=None, item=None):
            write_log("用户点击退出服务")
            if tray_icon:
                tray_icon.stop()
            os._exit(0)

        menu = Menu(
            MenuItem("打开页面", open_page, default=True),
            MenuItem("退出服务", exit_app)
        )

        tray_icon = Icon("廉政意见智答系统", icon_image, "廉政意见智答系统", menu)
        write_log("系统托盘图标已创建")

    except Exception as e:
        write_log(f"创建托盘图标失败: {e}")

def main():
    global tray_icon
    try:
        write_log("程序启动")
        is_frozen = getattr(sys, 'frozen', False)

        from app.core.config import settings
        write_log(f"数据目录: {settings.data_dir}")

        create_tray_icon()
        tray_thread = threading.Thread(target=lambda: tray_icon.run() if tray_icon else None, daemon=True)
        tray_thread.start()

        if is_frozen:
            def open_browser():
                time.sleep(1.5)
                url = f"http://127.0.0.1:{settings.port}"
                try:
                    webbrowser.open(url)
                except:
                    pass
            threading.Thread(target=open_browser, daemon=True).start()

        import uvicorn
        write_log("启动服务...")

        uvicorn.run(
            "app.main:app",
            host=settings.host,
            port=settings.port,
            reload=False,
            log_config={"version": 1, "disable_existing_loggers": False}
        )

    except Exception as e:
        error_msg = f"程序启动失败:\n{str(e)}\n\n{traceback.format_exc()}"
        write_log(error_msg)
        show_error(error_msg)

if __name__ == "__main__":
    main()
