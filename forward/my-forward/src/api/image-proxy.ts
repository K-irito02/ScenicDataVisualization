import axios from 'axios';

// 默认图片
export const DEFAULT_IMAGE = '/images/default-scenic.jpg';

// 检测不可用图片域名列表
const PROBLEMATIC_DOMAINS = [
  'mafengwo.net',
  'note.mafengwo.net',
  'b1-q.mafengwo.net',
  'n1-q.mafengwo.net',
  'p1-q.mafengwo.net',
  'images.mafengwo.net'
];

/**
 * 检查图片URL是否需要代理
 * @param url 原始图片URL
 */
export function needsProxy(url: string): boolean {
  if (!url) return false;
  
  try {
    // 如果不是http开头的URL，不需要代理
    if (!url.startsWith('http')) return false;
    
    // 检查是否包含已知的问题域名
    return PROBLEMATIC_DOMAINS.some(domain => url.includes(domain));
  } catch (error) {
    console.error('[ImageProxy] 检查URL是否需要代理出错:', error);
    return false;
  }
}

/**
 * 处理图片URL，避免跨域和403错误
 * @param imageUrl 原始图片URL
 * @param fallbackImage 备用图片URL
 */
export function processImageUrl(imageUrl: string, fallbackImage = DEFAULT_IMAGE): string {
  try {
    if (!imageUrl) return fallbackImage;
    
    // 检查是否是有问题的图片域名
    if (needsProxy(imageUrl)) {
      console.log('[ImageProxy] 检测到问题域名的图片，使用代理服务');
      // 使用后端代理
      return `/api/proxy/image?url=${encodeURIComponent(imageUrl)}`;
    }
    
    // 其他第三方图片，直接返回原始URL
    if (imageUrl.startsWith('http')) {
      return imageUrl;
    }
    
    // 本地图片路径
    return imageUrl;
  } catch (error) {
    console.error('[ImageProxy] 处理图片URL出错:', error);
    return fallbackImage;
  }
}

/**
 * 使用后端代理获取图片
 * 注意：需要后端实现对应的代理接口
 * @param imageUrl 原始图片URL
 */
export async function fetchProxiedImage(imageUrl: string): Promise<string> {
  try {
    if (!imageUrl) return DEFAULT_IMAGE;
    
    // 本地或已经代理的图片不需要处理
    if (!imageUrl.startsWith('http') || 
        imageUrl.startsWith('/api/proxy/')) {
      return imageUrl;
    }
    
    // 请求后端代理
    const response = await axios.get(`/api/proxy/image`, {
      params: { url: imageUrl },
      responseType: 'blob'
    });
    
    // 创建blob URL
    const blob = new Blob([response.data], { type: response.headers['content-type'] });
    return URL.createObjectURL(blob);
  } catch (error) {
    console.error('[ImageProxy] 代理获取图片失败:', error);
    return DEFAULT_IMAGE;
  }
} 