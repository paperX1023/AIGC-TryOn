import os
import sys
import uuid
import torch
import numpy as np
from PIL import Image
from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from torchvision import transforms
from rembg import remove

# 消除 libgomp 警告
os.environ["OMP_NUM_THREADS"] = "1"

# 路径注入
PROJECT_ROOT = "/root/autodl-tmp/IDM-VTON"
sys.path.append(PROJECT_ROOT)

from src.tryon_pipeline import StableDiffusionXLInpaintPipeline as TryonPipeline
from src.unet_hacked_garmnet import UNet2DConditionModel as Ref_UNet
from src.unet_hacked_tryon import UNet2DConditionModel as Tryon_UNet
from transformers import CLIPVisionModelWithProjection, CLIPImageProcessor
from diffusers import DDIMScheduler
from preprocess.humanparsing.run_parsing import Parsing
from preprocess.openpose.run_openpose import OpenPose

# 配置常量
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
CKPT_DIR = f"{PROJECT_ROOT}/ckpt"
OUTPUT_DIR = f"{PROJECT_ROOT}/results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

tensor_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
])

def get_mask_location(parsing_result):
    mask_array = np.array(parsing_result)
    mask_cloth = np.zeros_like(mask_array)
    # 4 是上衣，7 是连裙
    mask_cloth[(mask_array == 4) | (mask_array == 7)] = 255
    return Image.fromarray(mask_cloth.astype(np.uint8)).convert("L")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("⏳ 正在从数据盘加载 IDM-VTON 权重到 4090...")
    
    app.state.parsing_model = Parsing(0)
    app.state.openpose_model = OpenPose(0)
    
    unet = Tryon_UNet.from_pretrained(CKPT_DIR, subfolder="unet", torch_dtype=torch.float16)
    unet_encoder = Ref_UNet.from_pretrained(CKPT_DIR, subfolder="unet_encoder", torch_dtype=torch.float16)
    image_encoder = CLIPVisionModelWithProjection.from_pretrained(CKPT_DIR, subfolder="image_encoder", torch_dtype=torch.float16)
    
    feature_extractor = CLIPImageProcessor()
    
    pipe = TryonPipeline.from_pretrained(
        CKPT_DIR,
        unet=unet,
        image_encoder=image_encoder,
        feature_extractor=feature_extractor, 
        torch_dtype=torch.float16,
    ).to(DEVICE)
    
    pipe.unet_encoder = unet_encoder.to(DEVICE)
    pipe.scheduler = DDIMScheduler.from_config(pipe.scheduler.config)
    
    app.state.pipe = pipe
    print("✅ 引擎启动完毕，API 服务已就绪！")
    yield

app = FastAPI(lifespan=lifespan)
app.mount("/results", StaticFiles(directory=OUTPUT_DIR), name="results")

@app.post("/tryon")
async def tryon_endpoint(person_file: UploadFile = File(...), cloth_file: UploadFile = File(...)):
    print("📥 收到试穿请求，开始图像预处理...")
    
    # 1. 读取模特图
    p_img_pil = Image.open(person_file.file).convert("RGB").resize((768, 1024))
    
    # 🚀 2. 衣服图自动化预处理 (抠图 + 填白底)
    print("🧹 正在启动 rembg 自动剥离衣服背景...")
    raw_cloth = Image.open(cloth_file.file).convert("RGB")
    # 抠出带透明通道的衣服 (RGBA)
    cloth_rgba = remove(raw_cloth)
    # 创建一张纯白色的背景图
    white_bg = Image.new("RGB", cloth_rgba.size, (255, 255, 255))
    # 将抠好的衣服“贴”到纯白背景上 (利用 alpha 通道作为 Mask)
    white_bg.paste(cloth_rgba, mask=cloth_rgba.split()[3])
    # 统一尺寸
    g_img_pil = white_bg.resize((768, 1024))
    print("✨ 衣服背景剥离完成，获得纯净商品图！")

    # 3. 提取人体信息
    parsing_result, _ = app.state.parsing_model(p_img_pil)
    mask_img_pil = get_mask_location(parsing_result)
    
    pose_data = app.state.openpose_model(p_img_pil)
    if pose_data is None:
        pose_img_pil = Image.new("RGB", (768, 1024), (0, 0, 0))
    elif isinstance(pose_data, dict):
        pose_img_pil = pose_data.get('img', Image.new("RGB", (768, 1024), (0, 0, 0))).convert("RGB")
    else:
        pose_img_pil = pose_data.convert("RGB")
    pose_img_pil = pose_img_pil.resize((768, 1024))

    g_img_tensor = tensor_transform(g_img_pil).unsqueeze(0).to(DEVICE, torch.float16)
    pose_tensor = tensor_transform(pose_img_pil).unsqueeze(0).to(DEVICE, torch.float16)

    prompt = "photorealistic, highly detailed, a model is wearing this garment"
    negative_prompt = "monochrome, lowres, bad quality, blurry, distorted"

    (prompt_embeds, negative_prompt_embeds, pooled_prompt_embeds, negative_pooled_prompt_embeds) = app.state.pipe.encode_prompt(
        prompt=prompt, device=DEVICE, num_images_per_prompt=1, do_classifier_free_guidance=True, negative_prompt=negative_prompt
    )
    
    (prompt_embeds_c, _, _, _) = app.state.pipe.encode_prompt(
        prompt="a photo of a garment", device=DEVICE, num_images_per_prompt=1, do_classifier_free_guidance=False, negative_prompt=""
    )

    print("🚀 预处理完毕，送入 4090 算力渲染中...")
    
    with torch.no_grad():
        result = app.state.pipe(
            prompt_embeds=prompt_embeds,
            negative_prompt_embeds=negative_prompt_embeds,
            pooled_prompt_embeds=pooled_prompt_embeds,
            negative_pooled_prompt_embeds=negative_pooled_prompt_embeds,
            text_embeds_cloth=prompt_embeds_c,
            image=p_img_pil,
            mask_image=mask_img_pil,
            cloth=g_img_tensor,
            pose_img=pose_tensor,
            ip_adapter_image=g_img_pil, # 注意这里传进去的是纯白背景的 PIL 图！
            num_inference_steps=30,
            guidance_scale=2.0,
            height=1024,
            width=768
        )
        output_image = result[0][0]

    file_name = f"{uuid.uuid4().hex}.jpg"
    save_path = os.path.join(OUTPUT_DIR, file_name)
    output_image.save(save_path, format="JPEG", quality=95)
    
    print(f"📤 生成成功: {file_name}")
    
    return {
        "status": "success",
        "message": "AutoDL 节点生成成功",
        "result_image_path": f"/results/{file_name}"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6006)