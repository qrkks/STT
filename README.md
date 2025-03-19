# 课堂录音转文字工具

这是一个将课堂录音转换为文字稿的工具。特别适合心理学等领域的课程录音转写。

## 功能特点

- 支持中文语音识别
- 生成带时间戳的文字稿
- 完全本地运行，保护隐私
- 支持多种音频格式
- 自动使用最新版本依赖

## 安装方法

### 前提条件

- Python 3.8 或更高版本
- 建议有GPU支持（可显著提高处理速度）

### 使用Poetry安装（推荐）

```bash
# 安装Poetry (如果尚未安装)
curl -sSL https://install.python-poetry.org | python3 -
# 或者如果您在Windows上
# (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# 克隆仓库
git clone [仓库地址]
cd stt-project

# 安装依赖
poetry install

# 激活环境
poetry shell
```

### 使用pip安装

```bash
# 克隆仓库
git clone [仓库地址]
cd stt-project

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -e .
```

## 使用方法

### 基本使用

```bash
# 简易交互模式
python run.py

# 或直接指定文件
python run.py 你的录音文件.mp3 输出文件.txt
```

### 使用音频和输出文件夹

项目包含两个特殊文件夹：
- `audio` 文件夹：放置需要转录的音频文件
- `output` 文件夹：存储生成的文字稿

使用这些文件夹可以简化命令：
```bash
# 将录音放在audio文件夹中，只需输入文件名
python run.py lecture.mp3

# 输出文件会自动保存在output文件夹
# output/lecture.txt 将被创建
```

### 高级选项

```bash
# 指定模型大小
python src/transcribe.py --input 录音文件路径.mp3 --output 输出文件路径.txt --model_size medium

# 强制使用CPU
python src/transcribe.py --input 录音文件路径.mp3 --output 输出文件路径.txt --force_cpu

# 指定语言（默认为中文zh）
python src/transcribe.py --input 录音文件路径.mp3 --output 输出文件路径.txt --language en
```

## 支持的音频格式

- MP3
- WAV
- M4A
- 其他FFmpeg支持的格式

## 支持的语言

工具支持多种语言，包括但不限于：
- 中文 (zh)
- 英语 (en)
- 日语 (ja)
- 韩语 (ko)
- 法语 (fr)
- 德语 (de)
等多种语言

## 注意事项

- 初次运行时会下载模型，可能需要一些时间
- 处理时间与录音长度及计算机性能有关
- 识别准确率受录音质量影响
- 确保已安装FFmpeg（用于音频处理） 