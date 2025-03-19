#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse
import tempfile
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union
from tqdm import tqdm

# 导入本地工具模块
from src.utils import (
    check_dependencies, 
    ensure_ffmpeg, 
    check_gpu, 
    get_temp_dir, 
    cleanup_temp_files,
    get_whisper_model_size
)

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="将录音转换为文字稿")
    parser.add_argument("--input", type=str, required=True, help="输入音频文件的路径，可以是相对于audio文件夹的路径")
    parser.add_argument("--output", type=str, required=True, help="输出文本文件的路径，可以是相对于output文件夹的路径")
    parser.add_argument(
        "--model_size", 
        type=str, 
        default=None, 
        choices=["tiny", "base", "small", "medium", "large"], 
        help="Whisper模型大小"
    )
    parser.add_argument("--force_cpu", action="store_true", help="强制使用CPU，即使有GPU可用")
    parser.add_argument("--clean_temp", action="store_true", help="完成后清理临时文件")
    parser.add_argument("--language", type=str, default="zh", help="语音语言，默认为中文(zh)")
    return parser.parse_args()

def load_audio(file_path: str) -> Tuple:
    """加载音频文件并返回numpy数组"""
    print(f"加载音频文件: {file_path}")
    
    try:
        # 确保文件路径是绝对路径
        file_path = os.path.abspath(file_path)
        print(f"完整文件路径: {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"找不到音频文件: {file_path}")
            
        # 导入依赖
        import numpy as np
        from pydub import AudioSegment
        import soundfile as sf
        
        # 尝试使用pydub加载多种格式
        audio = AudioSegment.from_file(file_path)
        
        # 将音频转换为wav格式
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_file.close()
        print(f"创建临时文件: {temp_file.name}")
        
        audio.export(temp_file.name, format="wav")
        
        # 使用soundfile读取
        audio_array, sample_rate = sf.read(temp_file.name)
        os.unlink(temp_file.name)
        
        # 如果是双声道，转为单声道
        if len(audio_array.shape) > 1:
            audio_array = audio_array.mean(axis=1)
            
        # 标准化
        audio_array = audio_array / np.max(np.abs(audio_array))
        
        return audio_array, sample_rate
    except Exception as e:
        print(f"加载音频失败: {e}")
        raise

def transcribe_audio(audio_path: str, model_size: str = "base", device: str = "cpu", language: str = "zh") -> Dict:
    """使用Whisper进行音频转录"""
    print(f"加载Whisper模型 ({model_size})...")
    
    try:
        import whisper
        model = whisper.load_model(model_size, device=device)  
        
        print("转录音频...")
        result = model.transcribe(
            audio_path,
            language=language,
            task="transcribe",
            verbose=True
        )
        
        return result
    except Exception as e:
        print(f"转录失败: {e}")
        sys.exit(1)

def format_time(seconds: float) -> str:
    """将秒数格式化为HH:MM:SS格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"

def save_transcript(result: Dict, output_path: str):
    """保存转录结果到文件"""
    try:
        import opencc
        converter = opencc.OpenCC('t2s')  # 繁体转简体
    except ImportError:
        print("未安装opencc-python-reimplemented，将保持繁体输出")
        converter = None
    
    def convert_text(text):
        if converter:
            return converter.convert(text)
        return text
    
    with open(output_path, "w", encoding="utf-8") as f:
        # 首先保存完整文本
        f.write("# 完整文本\n\n")
        f.write(convert_text(result["text"]))
        f.write("\n\n")
        
        # 然后保存带时间戳的分段文本
        f.write("# 带时间戳的分段文本\n\n")
        for segment in result["segments"]:
            start_time = format_time(segment["start"])
            end_time = format_time(segment["end"])
            time_str = f"[{start_time} --> {end_time}]"
            f.write(f"{time_str}\n{convert_text(segment['text'])}\n\n")
    
    print(f"转录完成，结果已保存到: {output_path}")

def main():
    """主函数"""
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 确保FFmpeg已安装
    if not ensure_ffmpeg():
        sys.exit(1)
    
    # 解析参数
    args = parse_args()
    
    # 处理输入路径
    input_path = args.input
    if not os.path.isabs(input_path) and not os.path.exists(input_path):
        # 如果不是绝对路径且当前目录下不存在，尝试在audio文件夹中查找
        audio_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'audio')
        potential_path = os.path.join(audio_dir, input_path)
        if os.path.exists(potential_path):
            input_path = potential_path
    
    if not os.path.exists(input_path):
        print(f"错误: 输入文件不存在: {input_path}")
        print(f"请确保文件存在，或将文件放在 'audio' 文件夹中")
        return
    
    # 处理输出路径
    output_path = args.output
    if not os.path.isabs(output_path):
        # 如果不是绝对路径，默认放在output文件夹
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_path)
    
    # 确保输出目录存在
    output_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(output_dir, exist_ok=True)
    
    # 检查GPU可用性
    device, gpu_available = check_gpu()
    if args.force_cpu:
        device = "cpu"
        print("按要求强制使用CPU")
    else:
        print(f"使用设备: {device}")
    
    # 如果未指定模型大小，根据GPU可用性选择合适的模型
    if args.model_size is None:
        args.model_size = get_whisper_model_size(device == "cuda")
        print(f"自动选择模型大小: {args.model_size}")
    
    # 进行转录
    result = transcribe_audio(input_path, args.model_size, device, args.language)
    
    # 保存结果
    save_transcript(result, output_path)
    
    # 清理临时文件
    if args.clean_temp:
        cleanup_temp_files()

if __name__ == "__main__":
    main() 