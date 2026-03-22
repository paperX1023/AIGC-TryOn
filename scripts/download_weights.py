import os
from huggingface_hub import snapshot_download

# 使用学术加速
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

def download_model():
    print("⏳ 开始下载 IDM-VTON 核心权重 (约 20GB)...")
    # 下载 IDM-VTON 专用权重
    snapshot_download(
        repo_id="yisol/IDM-VTON",
        local_dir="./ckpt",
        local_dir_use_symlinks=False
    )
    
    # 下载预处理器权重 (Human Parsing 和 OpenPose)
    print("⏳ 下载预处理器模型...")
    # 注意：这部分通常需要手动放置，但snapshot_download会把仓库里有的都拉下来
    print("✅ 权重下载完成！")

if __name__ == "__main__":
    download_model()