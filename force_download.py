import os
# 🚀 开启超级加速开关
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from huggingface_hub import snapshot_download

local_dir = "/root/autodl-tmp/IDM-VTON/ckpt"
repo_id = "yisol/IDM-VTON"

print(f"🔥 正在使用 hf_transfer 超级加速下载...")

try:
    snapshot_download(
        repo_id=repo_id,
        local_dir=local_dir,
        local_dir_use_symlinks=False,
        resume_download=True,
        endpoint="https://hf-mirror.com"
    )
    print("✅ 权重已满速下载完成！")
except Exception as e:
    print(f"❌ 还是不行: {e}")