// 默认图片路径
export const DEFAULT_IMAGE = '/img/default-scenic.jpg';

/**
 * 处理图片URL，提供默认图片处理
 * @param imageUrl 原始图片URL
 * @param fallbackImage 备用图片URL
 */
export function processImageUrl(
  imageUrl: string, 
  fallbackImage = DEFAULT_IMAGE
): string {
  try {
    // 如果URL为空，使用默认图片
    if (!imageUrl || imageUrl === 'null' || imageUrl === 'undefined') {
      console.log('[图片处理] 图片URL为空或无效，使用默认图片');
      return fallbackImage;
    }
    
    // 如果URL是相对路径且不以/开头，添加斜杠
    if (!imageUrl.startsWith('/') && !imageUrl.startsWith('http')) {
      imageUrl = '/' + imageUrl;
    }
    
    // 如果是相对路径或已经是http开头的URL，直接返回
    return imageUrl;
  } catch (error) {
    console.error('[图片处理] 处理图片URL出错:', error);
    return fallbackImage;
  }
}