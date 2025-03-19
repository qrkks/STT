#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
工具函数模块，提供音频处理的辅助功能
"""

import os
import sys
import tempfile
from typing import Optional, Tuple

def check_dependencies():
    """检查必要的依赖是否已安装"""
    missing_packages = []
    
    try:
        import torch
    except ImportError:
        missing_packages.append("torch")
    
    try:
        import whisper
    except ImportError:
        missing_packages.append("whisper")
    
    try:
        import numpy
    except ImportError:
        missing_packages.append("numpy")
    
    try:
        import soundfile
    except ImportError:
        missing_packages.append("soundfile")
    
    try:
        import pydub
    except ImportError:
        missing_packages.append("pydub")
    
    if missing_packages:
        print("缺少以下依赖包:")
        for pkg in missing_packages:
            print(f"  - {pkg}")
        print("\n请使用以下命令安装:")
        print("使用Poetry (推荐):")
        print("  poetry add " + " ".join(missing_packages))
        print("或使用pip:")
        print("  pip install " + " ".join(missing_packages))
        return False
    
    return True

def ensure_ffmpeg():
    """确保FFmpeg已安装或提供安装指南"""
    try:
        # 尝试使用pydub，它会在内部检查ffmpeg
        from pydub import AudioSegment
        # 创建一个简单的测试
        temp = AudioSegment.silent(duration=100)
        return True
    except Exception as e:
        if "ffmpeg" in str(e).lower() or "avconv" in str(e).lower():
            print("错误: 无法找到FFmpeg，这是处理音频所必需的")
            print("\n安装指南:")
            print("- Windows: 下载FFmpeg并添加到PATH环境变量")
            print("  https://ffmpeg.org/download.html")
            print("- macOS: 使用Homebrew安装: brew install ffmpeg")
            print("- Linux: 使用包管理器安装，如: apt install ffmpeg")
            return False
    return True

def check_gpu():
    """检查是否有GPU可用并返回适当的设备字符串"""
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda", True
        else:
            return "cpu", False
    except ImportError:
        return "cpu", False

def get_temp_dir() -> str:
    """获取或创建临时目录"""
    temp_dir = os.path.join(tempfile.gettempdir(), "stt_project")
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir

def get_whisper_model_size(gpu_available: bool) -> str:
    """根据是否有GPU返回推荐的模型大小"""
    if gpu_available:
        return "medium"  # GPU可用时使用更大的模型
    else:
        return "base"    # CPU时使用基础模型

def cleanup_temp_files(directory: Optional[str] = None):
    """清理临时文件"""
    if directory is None:
        directory = get_temp_dir()
    
    try:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        print(f"已清理临时文件: {directory}")
    except Exception as e:
        print(f"清理临时文件时出错: {e}") 