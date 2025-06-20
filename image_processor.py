# -*- coding: utf-8 -*-
"""
图像处理模块
使用OpenCV在图片上绘制检测到的文本区域边框
"""

import cv2
import os
from typing import List, Dict, Tuple
import config


class ImageProcessor:
    """图像处理类，用于在图片上绘制检测结果"""
    
    def __init__(self):
        """初始化图像处理器"""
        pass
    
    def load_image(self, image_path: str) -> cv2.Mat:
        """
        加载图片文件
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            OpenCV图像对象
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
        
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"无法读取图片文件: {image_path}")
        
        return image
    
    def draw_bounding_boxes(self, image: cv2.Mat, detections: List[Dict]) -> cv2.Mat:
        """
        在图片上绘制检测到的文本区域边框
        
        Args:
            image: OpenCV图像对象
            detections: 检测结果列表，每个元素包含box_2d和text_content
            
        Returns:
            绘制了边框的图像
        """
        # 创建图像副本，避免修改原图
        result_image = image.copy()
        
        for i, detection in enumerate(detections):
            try:
                # 提取边界框坐标
                box_2d = detection.get('box_2d', [])
                text_content = detection.get('text_content', '')
                
                if len(box_2d) != 4:
                    print(f"警告: 检测结果 {i} 的坐标格式不正确: {box_2d}")
                    continue
                
                x1, y1, x2, y2 = map(int, box_2d)
                
                # 确保坐标在图像范围内
                height, width = result_image.shape[:2]
                x1 = max(0, min(x1, width))
                y1 = max(0, min(y1, height))
                x2 = max(0, min(x2, width))
                y2 = max(0, min(y2, height))
                
                # 绘制红色边框
                cv2.rectangle(
                    result_image,
                    (x1, y1),
                    (x2, y2),
                    config.BBOX_COLOR,
                    config.BBOX_THICKNESS
                )
                
                # 在边框上方添加序号标签
                label = f"#{i+1}"
                label_size = cv2.getTextSize(
                    label,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    config.FONT_SCALE,
                    config.FONT_THICKNESS
                )[0]
                
                # 计算标签位置（边框左上角上方）
                label_x = x1
                label_y = max(y1 - 10, label_size[1] + 5)
                
                # 绘制标签背景
                cv2.rectangle(
                    result_image,
                    (label_x, label_y - label_size[1] - 5),
                    (label_x + label_size[0] + 5, label_y + 5),
                    config.BBOX_COLOR,
                    -1  # 填充
                )
                
                # 绘制标签文字
                cv2.putText(
                    result_image,
                    label,
                    (label_x + 2, label_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    config.FONT_SCALE,
                    (255, 255, 255),  # 白色文字
                    config.FONT_THICKNESS
                )
                
                print(f"绘制边框 #{i+1}: ({x1}, {y1}) -> ({x2}, {y2})")
                print(f"文本内容: {text_content[:50]}...")  # 只显示前50个字符
                
            except Exception as e:
                print(f"绘制检测结果 {i} 时发生错误: {e}")
                continue
        
        return result_image
    
    def save_image(self, image: cv2.Mat, output_path: str) -> bool:
        """
        保存处理后的图片
        
        Args:
            image: 要保存的图像
            output_path: 输出文件路径
            
        Returns:
            保存是否成功
        """
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            success = cv2.imwrite(output_path, image)
            if success:
                print(f"图片已保存到: {output_path}")
                return True
            else:
                print(f"保存图片失败: {output_path}")
                return False
                
        except Exception as e:
            print(f"保存图片时发生错误: {e}")
            return False
    
    def generate_output_path(self, input_path: str) -> str:
        """
        根据输入路径生成输出路径
        
        Args:
            input_path: 输入图片路径
            
        Returns:
            输出图片路径
        """
        dir_name = os.path.dirname(input_path)
        base_name = os.path.basename(input_path)
        name, ext = os.path.splitext(base_name)
        
        output_name = f"{name}{config.OUTPUT_SUFFIX}{ext}"
        return os.path.join(dir_name, output_name)
    
    def process_image(self, image_path: str, detections: List[Dict], output_path: str = None) -> str:
        """
        完整的图像处理流程：加载图片、绘制边框、保存结果
        
        Args:
            image_path: 输入图片路径
            detections: 检测结果列表
            output_path: 输出路径，如果不指定则自动生成
            
        Returns:
            输出图片路径
        """
        # 加载图片
        image = self.load_image(image_path)
        
        # 绘制边框
        result_image = self.draw_bounding_boxes(image, detections)
        
        # 生成输出路径
        if output_path is None:
            output_path = self.generate_output_path(image_path)
        
        # 保存结果
        self.save_image(result_image, output_path)
        
        return output_path
