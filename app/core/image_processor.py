import io
from PIL import Image
from app.core.logging import get_logger

logger = get_logger(__name__)

TARGET_SIZE = (750, 750)
MAX_FILE_SIZE = 1024 * 1024


def process_tongue_image(image_bytes: bytes) -> bytes:
    """
    处理舌面图片：调整分辨率为750x750，压缩至1MB以下
    
    Args:
        image_bytes: 原始图片的字节数据
        
    Returns:
        处理后的图片字节数据
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        
        image_resized = image.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
        
        output = io.BytesIO()
        quality = 95
        
        while quality >= 20:
            output.seek(0)
            output.truncate()
            image_resized.save(output, format='JPEG', quality=quality, optimize=True)
            
            if output.tell() <= MAX_FILE_SIZE:
                logger.info(f"Image processed successfully: size={output.tell()} bytes, quality={quality}")
                return output.getvalue()
            
            quality -= 5
        
        output.seek(0)
        output.truncate()
        image_resized.save(output, format='JPEG', quality=20, optimize=True)
        logger.warning(f"Image compressed to minimum quality: size={output.tell()} bytes")
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"Failed to process image: {e}", exc_info=True)
        raise ValueError(f"图片处理失败: {str(e)}")


def validate_image_size(image_bytes: bytes) -> bool:
    """
    验证图片大小是否在限制范围内
    
    Args:
        image_bytes: 图片字节数据
        
    Returns:
        是否符合大小要求
    """
    return len(image_bytes) <= MAX_FILE_SIZE
