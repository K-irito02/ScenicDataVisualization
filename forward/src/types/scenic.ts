// 景区数据类型定义
export interface ScenicSpot {
  id: number;
  name: string;
  level: string;
  price: number;
  location: {
    province: string;
    city: string;
    address: string;
    latitude: number;
    longitude: number;
  };
  description: string;
  mainImage: string;
  tags: string[];
  score: number;
  commentCount: number;
  collected: boolean;
  trafficMethods: string[];
  comments?: Comment[];
  // 可选的身份标识属性
  museumLevel?: string;  // 博物馆等级
  geologicalParkLevel?: string; // 地质公园级别
  waterScenicSpot?: boolean; // 国家级水利风景区
  forestParkLevel?: string; // 森林公园等级
  wetlandLevel?: string; // 湿地级别
  culturalRelicLevel?: string; // 文物保护单位级别
  natureReserveLevel?: string; // 自然保护区等级
}

/**
 * 景区分布统计数据类型
 */
export interface DistributionStatistics {
  // 各省景区分布数据
  provinceData: {
    name: string;
    value: number;
    a5Count: number;
    a4Count: number;
    a3Count: number;
  }[];
  // 景区等级分布数据
  levelDistribution: {
    name: string;
    value: number;
  }[];
}

/**
 * 景区属性分析数据类型
 */
export interface AttributeAnalysis {
  // 景区等级与价格分布数据
  levelPriceData: {
    level: string;
    priceRange: string;
    count: number;
  }[];
  // 景区属性热力图数据
  attributeHeatData: {
    name: string;
    value: [number, number, number]; // x坐标, y坐标, 热力值
  }[];
}

/**
 * 价格分析数据类型
 */
export interface PriceAnalysis {
  // 不同等级景区价格分布箱形图数据
  levelPriceDistribution: {
    level: string;
    min: number;
    q1: number;
    median: number;
    q3: number;
    max: number;
    outliers: number[];
  }[];
}

/**
 * 交通分析数据类型
 */
export interface TrafficAnalysis {
  // 各种交通方式使用数量统计
  methodsCount: {
    [key: string]: number;
  };
  // 不同交通方式组合下的情感分析
  sentimentByTrafficCount: {
    methodsCount: number;
    positive: number;
    neutral: number;
    negative: number;
    mainMethod: string;
  }[];
}

/**
 * 评论分析数据类型
 */
export interface CommentAnalysis {
  // 评论关键词云数据
  keywordCloud: {
    word: string;
    weight: number;
  }[];
  // 评论词组频率云数据
  frequencyCloud: {
    word: string;
    weight: number;
  }[];
}

/**
 * 身份分析数据类型
 */
export interface IdentityAnalysisData {
  // 景区身份集合数据
  sets: {
    name: string;
    value: number;
  }[];
  // 身份关系网络数据
  relations: {
    source: string;
    target: string;
    value: number;
  }[];
}

/**
 * 评论类型
 */
export interface Comment {
  id: number;
  user: string;
  avatar: string;
  content: string;
  score: number;
  date: string;
}

/**
 * 搜索结果类型
 */
export interface SearchResult {
  totalCount: number;
  list: ScenicSpot[];
}

/**
 * 搜索参数类型
 */
export interface SearchParams {
  keyword?: string;
  province?: string;
  city?: string;
  level?: string[];
  priceMin?: number;
  priceMax?: number;
  tags?: string[];
  page?: number;
  pageSize?: number;
} 