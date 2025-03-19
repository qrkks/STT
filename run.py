#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简化的运行脚本，可以直接运行此文件启动转录
"""

import os
import sys
import argparse
from src.transcribe import main as transcribe_main

def parse_args():
    """解析简化的命令行参数"""
    parser = argparse.ArgumentParser(description="课堂录音转文字工具")
    parser.add_argument("input", nargs="?", help="输入音频文件的路径，可放在audio文件夹中")
    parser.add_argument("output", nargs="?", help="输出文本文件的路径，默认放在output文件夹中")
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    # 如果没有提供参数，进入交互模式
    if args.input is None:
        print("=" * 60)
        print("课堂录音转文字工具")
        print("=" * 60)
        print("\n请提供以下信息:")
        
        input_path = input("输入音频文件路径 (可放在audio文件夹中): ").strip()
        if not input_path:
            print("错误: 必须提供输入文件路径")
            return
        
        # 先尝试直接访问
        if not os.path.exists(input_path):
            # 尝试在audio目录中查找
            audio_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio')
            potential_path = os.path.join(audio_dir, input_path)
            if os.path.exists(potential_path):
                input_path = potential_path
                print(f"在audio文件夹中找到文件: {input_path}")
        
        if not os.path.exists(input_path):
            print(f"错误: 文件不存在: {input_path}")
            print(f"请确保文件存在，或将文件放在 'audio' 文件夹中")
            return
        
        output_path = input("输出文本文件名 (将保存在output文件夹): ").strip()
        if not output_path:
            # 默认输出路径
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = f"{base_name}.txt"
            print(f"将使用默认输出文件名: {output_path}")
        
        # 确保输出路径在output目录
        if not os.path.isabs(output_path):
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, output_path)
        
        # 构建参数
        sys.argv = [
            sys.argv[0],
            "--input", input_path,
            "--output", output_path
        ]
        
        # 询问模型大小
        model_size = input("选择模型大小 (tiny/base/small/medium/large, 默认为自动选择): ").strip().lower()
        if model_size in ["tiny", "base", "small", "medium", "large"]:
            sys.argv.extend(["--model_size", model_size])
        
        # 询问语言
        language = input("指定语言 (默认为中文zh): ").strip()
        if language and language != "zh":
            sys.argv.extend(["--language", language])
        
        # 询问是否强制使用CPU
        force_cpu = input("是否强制使用CPU? (y/N): ").strip().lower()
        if force_cpu == "y":
            sys.argv.append("--force_cpu")
        
        # 询问是否清理临时文件
        clean_temp = input("转录后是否清理临时文件? (Y/n): ").strip().lower()
        if clean_temp != "n":
            sys.argv.append("--clean_temp")
    else:
        # 如果提供了输入但没有输出，使用默认输出路径
        if args.output is None:
            base_name = os.path.splitext(os.path.basename(args.input))[0]
            output_path = f"{base_name}.txt"
            sys.argv.append("--output")
            sys.argv.append(output_path)
            
        # 添加前缀，使其与transcribe.py中的参数解析兼容
        new_argv = [sys.argv[0]]
        
        if args.input:
            new_argv.extend(["--input", args.input])
        if args.output:
            new_argv.extend(["--output", args.output])
            
        sys.argv = new_argv
    
    # 运行转录
    transcribe_main()

if __name__ == "__main__":
    main() 