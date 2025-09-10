import torch
from ultralytics import YOLO
from config import logger
import yaml
import os

def run_training(config_path='classroom.yaml'):
    """
    执行YOLOv8模型的微调训练。
    """
    try:
        # 1. 检查是否有可用的GPU
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"Using device: {device} for training.")

        # 2. 检查并加载数据集配置文件
        if not os.path.exists(config_path):
            logger.error(f"Dataset config file not found at: {config_path}")
            return None, "Dataset config file not found."
        
        with open(config_path, 'r') as f:
            data_config = yaml.safe_load(f)
            logger.info(f"Loaded dataset configuration: {data_config}")

        # 3. 加载预训练模型作为起点
        # 注意：我们总是从官方的 'yolov8s.pt' 开始，而不是从上一个 best.pt 继续
        # 这确保了每次都是基于一个干净的基线进行微调。
        logger.info("Loading base pre-trained YOLOv8s model...")
        model = YOLO('yolov8s.pt')

        # 4. 开始训练
        logger.info("Starting model fine-tuning...")
        results = model.train(
            data=config_path,
            epochs=50,  # 初始轮次可以少一些，便于快速验证
            imgsz=640,
            device=device,
            project='runs/train', # 将所有训练结果保存在 runs/train 文件夹下
            name='classroom_finetune', # 本次实验的名称
            workers=2
        )

        best_model_path = os.path.join(results.save_dir, 'weights/best.pt')
        logger.info(f"Training complete! New model saved at: {best_model_path}")
        
        return best_model_path, "Training completed successfully."

    except Exception as e:
        logger.error(f"An error occurred during training: {str(e)}")
        return None, f"An error occurred: {str(e)}"

if __name__ == '__main__':
    # 这个部分允许你直接通过 `python train.py` 来独立运行训练
    run_training()