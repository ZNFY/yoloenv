from flask import Blueprint, render_template, jsonify, request, send_from_directory
import os
from config import logger

# [重要] 请根据你的实际挂载路径修改
ANNOTATION_DATA_PATH = "/mnt/hardcase/classroom_dataset/images/train" 
LABELS_PATH = "/mnt/hardcase/classroom_dataset/labels/train" # 假设保存到训练集标签目录

# 创建一个Flask蓝图
annotator_bp = Blueprint('annotator', __name__)

@annotator_bp.route('/annotate')
def annotate_page():
    """渲染在线标注页面"""
    return render_template('annotator.html')

@annotator_bp.route('/api/images_to_annotate')
def get_images_to_annotate():
    """获取所有待标注的图片列表"""
    try:
        # 找出所有已经标注过的图片的基名 (不含扩展名)
        annotated_files = {os.path.splitext(f)[0] for f in os.listdir(LABELS_PATH) if f.endswith('.txt')}
        
        # 找出所有原始图片，并且过滤掉已经标注过的
        image_files = [
            f for f in os.listdir(ANNOTATION_DATA_PATH) 
            if f.lower().endswith(('.png', '.jpg', '.jpeg')) and os.path.splitext(f)[0] not in annotated_files
        ]
        return jsonify({"images": sorted(image_files)})
    except Exception as e:
        logger.error(f"获取待标注图片列表失败: {e}")
        return jsonify({"images": []}), 500

@annotator_bp.route('/images/<filename>')
def serve_image(filename):
    """为前端提供图片文件"""
    return send_from_directory(ANNOTATION_DATA_PATH, filename)

@annotator_bp.route('/api/save_annotation', methods=['POST'])
def save_annotation():
    """接收前端发送的标注数据并保存为.txt文件"""
    data = request.get_json()
    image_name = data.get('image_name')
    annotations = data.get('annotations')
    
    if not image_name or annotations is None:
        return jsonify({"error": "缺少数据"}), 400
        
    try:
        # 确保标签目录存在
        os.makedirs(LABELS_PATH, exist_ok=True)
        
        label_filename = os.path.splitext(image_name)[0] + '.txt'
        label_filepath = os.path.join(LABELS_PATH, label_filename)
        
        with open(label_filepath, 'w') as f:
            f.write(annotations)
            
        logger.info(f"成功保存在线标注文件: {label_filepath}")
        return jsonify({"message": "保存成功"})
    except Exception as e:
        logger.error(f"保存在线标注文件失败: {e}")
        return jsonify({"error": "保存失败"}), 500