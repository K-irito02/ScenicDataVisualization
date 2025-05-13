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
    // 如果URL为空或无效值，使用默认图片
    if (!imageUrl || 
        imageUrl === 'null' || 
        imageUrl === 'undefined' || 
        imageUrl === 'none' || 
        imageUrl.toLowerCase() === 'null' || 
        imageUrl.toLowerCase() === 'none') {
      console.log('[图片处理] 图片URL为空或无效，使用默认图片');
      return fallbackImage;
    }

    // 如果URL已经是默认图片路径，直接返回
    if (imageUrl === '/img/default-scenic.jpg') {
      return fallbackImage;
    }
    
    // 去除example.com域名
    if (imageUrl.includes('example.com')) {
      imageUrl = imageUrl.replace(/https?:\/\/example\.com/g, '');
      console.log('[图片处理] 移除示例域名:', imageUrl);
    }
    
    // 修复双斜杠问题
    imageUrl = imageUrl.replace(/\/\//g, '/');
    
    // 如果URL是相对路径且不以/开头，添加斜杠
    if (!imageUrl.startsWith('/') && !imageUrl.startsWith('http')) {
      imageUrl = '/' + imageUrl;
      console.log('[图片处理] 添加前导斜杠:', imageUrl);
    }
    
    // 处理media路径，确保直接访问/media而不是通过/images/media
    if (imageUrl.includes('/images/media/')) {
      imageUrl = imageUrl.replace('/images/media/', '/media/');
      console.log('[图片处理] 修正媒体文件路径:', imageUrl);
    }
    
    // 优先处理本地媒体文件路径
    if (imageUrl.includes('/media/scenic_images/')) {
      console.log('[图片处理] 使用本地图片路径:', imageUrl);
      return imageUrl;
    }
    
    // 如果URL包含"static/images/default-scenic.jpg"，替换为新的默认图片路径
    if (imageUrl.includes('static/images/default-scenic.jpg') || 
        imageUrl.includes('/static/images/default-scenic.jpg')) {
      console.log('[图片处理] 将旧的默认图片路径替换为新路径');
      return fallbackImage;
    }
    
    // 如果仍然是马蜂窝的外部链接，记录警告
    if (imageUrl.includes('mafengwo.net')) {
      console.warn('[图片处理] 检测到外部马蜂窝图片链接，应该已下载到本地:', imageUrl);
    }
    
    // 如果是相对路径或已经是http开头的URL，直接返回
    return imageUrl;
  } catch (error) {
    console.error('[图片处理] 处理图片URL出错:', error);
    return fallbackImage;
  }
}