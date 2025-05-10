#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import pymongo
from pymongo import MongoClient, UpdateOne
from openai import OpenAI
import time
from tqdm import tqdm
import os
import logging
from datetime import datetime
import random
import pickle
import hashlib
import requests
import threading

# 配置日志，只记录错误日志
logging.basicConfig(
    level=logging.ERROR,  # 仅记录ERROR级别及以上的日志
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scenic_data_processing_error.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 可从环境变量获取敏感信息，如未设置则使用默认值
DEEPSEEK_API_KEYS = os.environ.get("DEEPSEEK_API_KEYS", 
                                  "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx,"
                                  "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx,"
                                  "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx,"
                                  "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx").split(",")
MONGO_CONNECTION_STRING = os.environ.get("MONGO_CONNECTION_STRING", "mongodb://localhost:27017/")
DB_NAME = os.environ.get("MONGO_DB_NAME", "scenic_area")
COLLECTION_NAME = os.environ.get("MONGO_COLLECTION", "china_attractions")

# 处理效率设置
MAX_WORKERS = int(os.environ.get("MAX_WORKERS", "16"))  # 增加并发数以匹配Ryzen 5 5600H的12线程
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "80"))    # 增大批处理大小以充分利用16GB内存
RETRY_ATTEMPTS = int(os.environ.get("RETRY_ATTEMPTS", "3"))  # API调用失败时的重试次数
RETRY_DELAY = float(os.environ.get("RETRY_DELAY", "2"))     # 重试间隔(秒)
RATE_LIMIT_DELAY = float(os.environ.get("RATE_LIMIT_DELAY", "0.1"))  # 降低随机延迟（不受限制）
API_TIMEOUT = int(os.environ.get("API_TIMEOUT", "120"))  # 增加API超时时间，但不超过DeepSeek的30分钟限制

# 结果缓存目录
CACHE_DIR = os.environ.get("CACHE_DIR", "ai_results_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# 中断恢复文件
RESUME_FILE = os.environ.get("RESUME_FILE", "resume_state.pkl")

# API客户端池化管理
_api_clients = {}  # 按API-Key存储客户端实例
_api_client_lock = threading.Lock()
_current_key_index = 0  # 当前使用的API-Key索引
_api_key_counters = {}  # 每个API-Key的使用计数
_api_key_errors = {}  # 每个API-Key的错误计数

# 数据处理进度跟踪（每个API-Key线程）
_thread_progress = {}  # 记录每个线程的处理进度
_thread_progress_lock = threading.Lock()  # 线程安全锁

def get_next_api_key():
    """使用轮转策略获取下一个可用的API-Key"""
    global _current_key_index
    
    with _api_client_lock:
        # 获取可用的API密钥数量
        key_count = len(DEEPSEEK_API_KEYS)
        if key_count == 0:
            logger.error("没有可用的API密钥")
            return None
            
        # 选择下一个API密钥（简单轮询）
        _current_key_index = (_current_key_index + 1) % key_count
        selected_key = DEEPSEEK_API_KEYS[_current_key_index]
        
        # 更新使用计数
        if selected_key not in _api_key_counters:
            _api_key_counters[selected_key] = 0
        _api_key_counters[selected_key] += 1
        
        return selected_key

def get_api_client(api_key=None):
    """获取共享的API客户端实例，实现连接池化管理"""
    global _api_clients
    
    # 如果未指定API密钥，则使用轮转策略获取
    if api_key is None:
        api_key = get_next_api_key()
        if api_key is None:
            return None
    
    # 使用线程锁确保线程安全
    with _api_client_lock:
        # 检查该密钥是否已有客户端实例
        if api_key not in _api_clients:
            _api_clients[api_key] = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
            logger.info(f"已为API密钥 {api_key[:8]}... 初始化客户端连接")
    
    return _api_clients[api_key]

def record_api_error(api_key):
    """记录API密钥的错误，用于后续智能选择"""
    with _api_client_lock:
        if api_key not in _api_key_errors:
            _api_key_errors[api_key] = 0
        _api_key_errors[api_key] += 1
        
        # 如果错误过多，考虑临时禁用该密钥
        if _api_key_errors[api_key] > 10:
            logger.warning(f"API密钥 {api_key[:8]}... 错误过多，考虑检查其状态")

def connect_to_mongodb():
    """连接到MongoDB数据库"""
    try:
        client = MongoClient(MONGO_CONNECTION_STRING)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        return collection, client  # 返回client用于关闭连接
    except Exception as e:
        logger.error(f"MongoDB连接错误: {e}")
        return None, None

def add_deep_prefix(data):
    """为所有键添加deep_前缀"""
    return {f"deep_{k}": v for k, v in data.items()}

def load_resume_state():
    """加载中断恢复状态"""
    if os.path.exists(RESUME_FILE):
        try:
            with open(RESUME_FILE, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            logger.error(f"加载恢复状态失败: {e}")
    return None

def process_attractions_with_key(api_key, collection, start_id, end_id, batch_size):
    """使用指定API密钥处理景点数据的专用线程函数"""
    thread_name = f"APIThread-{api_key[:6]}"
    thread_id = threading.current_thread().ident
    processed_count = 0
    updates = []
    
    print(f"[{thread_name}] 启动处理线程，API密钥: {api_key[:8]}...")
    
    # 添加重试计数器
    retry_count = 0
    max_retries = 3
    
    while True:
        try:
            # 修改：使用批处理方式而不是保持游标长时间打开
            query = {}
            if start_id:
                query["_id"] = {"$gte": start_id}
            if end_id:
                if "_id" in query:
                    query["_id"]["$lt"] = end_id
                else:
                    query["_id"] = {"$lt": end_id}
            
            print(f"[{thread_name}] 查询条件: {query}")
            
            # 设置游标超时时间（毫秒）
            cursor = collection.find(query).sort("_id", pymongo.ASCENDING)
            cursor.max_time_ms(30 * 60 * 1000)  # 30分钟
            
            # 批量处理，每次获取一批数据而不是保持游标打开
            last_id = start_id
            while True:
                # 每次查询一批新数据，而不是保持同一个游标
                batch_query = query.copy()
                if last_id and last_id != start_id:
                    batch_query["_id"] = {"$gt": last_id}
                    if end_id:
                        batch_query["_id"]["$lt"] = end_id
                
                # 限制每次获取的数量
                batch = list(collection.find(batch_query).sort("_id", pymongo.ASCENDING).limit(batch_size))
                
                if not batch:
                    break
                    
                # 处理当前批次
                batch_results = []
                for attraction in batch:
                    result = process_attraction_with_key(attraction, api_key)
                    if result:
                        batch_results.append(result)
                
                # 更新最后处理的ID
                last_id = batch[-1]["_id"]
                
                # 更新处理进度
                processed_count += len(batch)
                with _thread_progress_lock:
                    _thread_progress[thread_id] = {
                        "api_key": api_key,
                        "processed": processed_count,
                        "last_id": last_id
                    }
                    
                # 收集更新
                for result in batch_results:
                    updates.append(UpdateOne(
                        {"_id": result["_id"]},
                        {"$set": result["deep_data"]}
                    ))
                    
                # 定期写入数据库
                if len(updates) >= 20:
                    try:
                        result = collection.bulk_write(updates)
                        print(f"[{thread_name}] 中间更新: 已写入 {len(updates)} 个记录")
                        updates = []
                    except Exception as e:
                        logger.error(f"[{thread_name}] 批量更新错误: {e}")
                
                # 批次间短暂休息，避免资源竞争
                time.sleep(random.uniform(0.5, 1.5))
            
            # 完成所有处理后，写入剩余更新
            if updates:
                try:
                    result = collection.bulk_write(updates)
                    print(f"[{thread_name}] 最终更新: 已写入 {len(updates)} 个记录")
                except Exception as e:
                    logger.error(f"[{thread_name}] 最终批量更新错误: {e}")
            
            print(f"[{thread_name}] 处理完成! 共处理 {processed_count} 个景点")
            
            # 每批次处理完成后保存进度
            save_thread_progress(api_key, last_id, processed_count)
            
            return processed_count
            
        except pymongo.errors.CursorNotFound as e:
            retry_count += 1
            if retry_count > max_retries:
                logger.error(f"[{thread_name}] 游标错误，已达到最大重试次数: {e}")
                break
                
            logger.warning(f"[{thread_name}] 游标错误，尝试重新查询 (尝试 {retry_count}/{max_retries}): {e}")
            time.sleep(2)  # 短暂休息后重试
            continue
            
        except Exception as e:
            logger.error(f"[{thread_name}] 处理异常: {e}")
            break

def process_attraction_with_key(attraction, api_key):
    """使用指定API密钥处理单个景点"""
    name = attraction.get("name")
    city = attraction.get("city")
    
    if not name or not city:
        logger.error(f"景点数据不完整: {attraction.get('_id')}")
        return None
    
    # 随机延迟，避免同时发起大量请求
    time.sleep(random.uniform(0, RATE_LIMIT_DELAY))
    
    # 调用AI获取信息，使用指定的API密钥
    try:
        start_time = time.time()
        ai_data = query_ai_with_key(city, name, api_key)
        elapsed = time.time() - start_time
        if elapsed > 10:  # 记录慢请求
            logger.info(f"长时请求: {city}-{name} 耗时 {elapsed:.1f}秒")
    except Exception as e:
        logger.error(f"处理异常: {e}")
        return None
    
    if not ai_data:
        logger.error(f"无法获取AI数据: {city} - {name}")
        return None
    
    return {
        "_id": attraction.get("_id"),
        "deep_data": ai_data
    }

def query_ai_with_key(city, name, api_key):
    """使用指定API密钥调用DeepSeek AI获取景区信息"""
    # 输入验证
    if not city or not name:
        logger.error(f"无效的输入参数: city={city}, name={name}")
        return None
    
    # 清理输入数据
    city = city.strip()
    name = name.strip()
    
    if len(city) == 0 or len(name) == 0:
        logger.error(f"输入参数为空: city={city}, name={name}")
        return None
    
    # 生成安全的缓存文件名
    cache_key = f"{city}_{name}".encode('utf-8')
    filename = hashlib.md5(cache_key).hexdigest() + ".json"
    cache_file = os.path.join(CACHE_DIR, filename)
    
    # 检查缓存
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                # 验证缓存数据完整性
                required_fields = ["scenic_level", "coordinates", "ticket_price", "opening_hours"]
                if all(f"deep_{field}" in cache_data for field in required_fields):
                    return cache_data
                logger.warning(f"缓存数据不完整: {city}-{name}，重新获取")
        except Exception as e:
            logger.error(f"读取缓存失败: {e}")
    
    # 使用与query_ai_for_scenic_info相同的提示
    prompt = f"""
    请根据以下信息，提供这个景点的详细数据，以JSON格式返回结果。
    - 景点所在省份: {city}
    - 景点名称: {name}
    
    请提供以下信息（如果没有信息，返回null）：
    1. 景区级别 (scenic_level): 如5A、4A、3A等
    2. 景区别名 (alternate_name): 景区的其他名称
    3. 景区经纬度 (coordinates): [经度, 纬度]格式
    4. 景区门票 (ticket_price): 详细票价信息
    5. 景区开放时间 (opening_hours): 开放时间详情
    6. 森林公园等级 (forest_park_level): 国家级、省级等
    7. 地质公园级别 (geological_park_level): 国家级、省级等
    8. 自然保护区等级 (nature_reserve_level): 国家级、省级等
    9. 国家级水利风景区 (water_conservancy_scenic_area): 是/否
    10. 博物馆等级 (museum_level): 国家级、省级等
    11. 湿地级别 (wetland_level): 国际级、国家级等
    12. 遗产项目编号 (heritage_project_number): 编号
    13. 文物保护单位 (cultural_relic_protection_unit): 国家级、省级等
    
    请直接返回JSON格式，无需任何额外说明。JSON应包含上述所有字段，格式如下:
    {{
      "scenic_level": "5A",
      "alternate_name": "xxx",
      "coordinates": [经度, 纬度],
      "ticket_price": "xxx",
      "opening_hours": "xxx",
      "forest_park_level": "xxx",
      "geological_park_level": "xxx",
      "nature_reserve_level": "xxx",
      "water_conservancy_scenic_area": "xxx",
      "museum_level": "xxx",
      "wetland_level": "xxx",
      "heritage_project_number": "xxx",
      "cultural_relic_protection_unit": "xxx"
    }}
    """
    
    # 检查避免空提示
    if not prompt or len(prompt.strip()) == 0:
        logger.error("生成的提示为空")
        return None
    
    ai_response = None
    client = get_api_client(api_key)
    
    for attempt in range(RETRY_ATTEMPTS + 1):
        try:
            # 使用指数退避策略进行重试
            retry_delay = RETRY_DELAY * (2 ** attempt) if attempt > 0 else RETRY_DELAY
            
            # 根据尝试次数决定是否使用流式请求
            use_stream = (attempt > 0)  # 第一次正常请求，重试时使用流式请求
            
            if use_stream:
                # 流式请求
                full_response = ""
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "你是一个旅游数据专家，精通中国各地景点信息。请只输出JSON格式数据，不要有任何额外文字。"},
                        {"role": "user", "content": prompt}
                    ],
                    stream=True,
                    timeout=API_TIMEOUT
                )
                
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                
                ai_response = full_response
            else:
                # 非流式请求
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "你是一个旅游数据专家，精通中国各地景点信息。请只输出JSON格式数据，不要有任何额外文字。"},
                        {"role": "user", "content": prompt}
                    ],
                    stream=False,
                    timeout=API_TIMEOUT
                )
                
                ai_response = response.choices[0].message.content
            
            # 处理AI响应(与原代码相同)
            if not ai_response:
                logger.error(f"API密钥 {api_key[:8]}... 返回空回复 (第{attempt+1}次尝试)")
                record_api_error(api_key)
                if attempt < RETRY_ATTEMPTS:
                    time.sleep(retry_delay)
                continue
            
            # 尝试提取JSON数据
            json_str = ""
            
            if "```json" in ai_response:
                json_str = ai_response.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_response:
                json_str = ai_response.split("```")[1].strip()
            else:
                json_str = ai_response.strip()
            
            try:
                data = json.loads(json_str)
                
                # 验证数据符合预期格式
                required_fields = ["scenic_level", "coordinates", "ticket_price", "opening_hours"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    missing_fields_str = ", ".join(missing_fields)
                    logger.warning(f"AI回复缺少必要字段: {missing_fields_str}，API密钥: {api_key[:8]}")
                    
                    if attempt < RETRY_ATTEMPTS:
                        time.sleep(retry_delay)
                        continue
                
                # 添加deep_前缀并保存缓存
                result = add_deep_prefix(data)
                
                # 保存到缓存
                try:
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    logger.error(f"保存缓存失败: {e}")
                
                # 更新API密钥使用计数
                with _api_client_lock:
                    if api_key not in _api_key_counters:
                        _api_key_counters[api_key] = 0
                    _api_key_counters[api_key] += 1
                
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析错误: {e}, API密钥: {api_key[:8]}")
                record_api_error(api_key)
                
                if attempt < RETRY_ATTEMPTS:
                    time.sleep(retry_delay)
                continue
        
        except Exception as e:
            logger.error(f"API调用错误: {e}, API密钥: {api_key[:8]}")
            record_api_error(api_key)
            
            if attempt < RETRY_ATTEMPTS:
                time.sleep(retry_delay)
            continue
    
    # 如果所有尝试都失败
    logger.error(f"无法获取有效回复: {city} - {name}, API密钥: {api_key[:8]}")
    return None

def monitor_progress(total_count):
    """监控各线程处理进度的线程函数"""
    last_total = 0
    start_time = time.time()
    
    while True:
        time.sleep(10)  # 每10秒更新一次
        
        with _thread_progress_lock:
            if not _thread_progress:
                continue
                
            # 计算总处理数量
            current_total = sum(prog["processed"] for prog in _thread_progress.values())
            
            # 计算处理速度
            elapsed = time.time() - start_time
            if elapsed > 0:
                speed = current_total / elapsed
            else:
                speed = 0
                
            # 计算预计剩余时间
            remaining = (total_count - current_total) / speed if speed > 0 else 0
            
            # 计算增量
            increment = current_total - last_total
            last_total = current_total
            
            # 显示总体进度
            print(f"\n--- 处理进度 ({datetime.now().strftime('%H:%M:%S')}) ---")
            print(f"总进度: {current_total}/{total_count} ({current_total/total_count:.1%})")
            print(f"处理速度: {speed:.1f} 景点/秒 (最近增量: {increment} 景点)")
            print(f"预计剩余时间: {remaining/60:.1f} 分钟")
            
            # 显示各线程进度
            print("\n各API密钥处理情况:")
            for thread_id, info in _thread_progress.items():
                api_key = info["api_key"]
                processed = info["processed"]
                print(f"- API密钥 {api_key[:8]}...: 已处理 {processed} 个景点")
                
            print("\n" + "-" * 50)
            
            # 检查是否所有线程都已完成
            active_threads = threading.active_count() - 2  # 减去主线程和监控线程
            if active_threads <= 0:
                print("所有处理线程已完成，监控结束")
                break

def save_thread_progress(api_key, last_id, processed_count):
    """保存线程处理进度"""
    thread_id = threading.current_thread().ident
    with _thread_progress_lock:
        _thread_progress[thread_id] = {
            "api_key": api_key,
            "processed": processed_count,
            "last_id": last_id
        }

def main():
    """使用独立线程处理景点数据，每个API KEY对应一个线程"""
    start_time = time.time()
    
    # 连接到MongoDB
    collection, mongo_client = connect_to_mongodb()
    if collection is None:
        logger.error("无法连接到MongoDB，程序退出")
        return
    
    # 显示API密钥信息
    api_key_count = len(DEEPSEEK_API_KEYS)
    print(f"当前配置了 {api_key_count} 个API密钥")
    if api_key_count == 0:
        logger.error("没有配置API密钥，程序退出")
        return
    
    try:
        # 获取所有景点数据
        total_count = collection.count_documents({})
        print(f"共找到 {total_count} 个景点数据")
        
        # 检查是否有中断恢复状态
        resume_state = load_resume_state()
        start_id = None
        
        if resume_state:
            response = input(f"发现上次处理中断，已处理 {resume_state['processed_count']}/{total_count} 个景点，是否继续? (y/n): ")
            if response.lower() == 'y':
                start_id = resume_state.get('last_id')
                print(f"从断点继续处理: 最后处理ID {start_id}")
        
        # 根据文档总数而不是ID范围来划分数据
        base_docs_per_thread = total_count // api_key_count
        extra_docs = total_count % api_key_count  # 余数
        
        print(f"数据划分: 每个线程约处理 {base_docs_per_thread} 个景点")
        
        # 如果有断点，查找断点ID的位置
        skip_count = 0
        if start_id:
            # 计算从开始到断点ID的文档数量
            skip_count = collection.count_documents({"_id": {"$lte": start_id}})
            print(f"从断点继续处理: 已完成 {skip_count} 个景点，将继续处理剩余 {total_count - skip_count} 个景点")
        
        # 创建线程池，每个API密钥一个线程
        threads = []
        
        # 追踪当前已划分的文档数量
        current_skip = skip_count
        
        for i, api_key in enumerate(DEEPSEEK_API_KEYS):
            # 为每个线程分配文档数量，最后一个线程可能会多分配一些文档
            thread_docs = base_docs_per_thread + (1 if i < extra_docs else 0)
            
            # 避免处理已经处理过的文档
            thread_docs = min(thread_docs, total_count - current_skip)
            
            if thread_docs <= 0:
                print(f"API密钥 {api_key[:8]}... 不需要处理数据，跳过")
                continue
            
            # 获取线程数据范围的第一个ID和最后一个ID
            thread_start_doc = collection.find().sort("_id", pymongo.ASCENDING).skip(current_skip).limit(1)
            try:
                thread_start_id = next(thread_start_doc)["_id"]
            except StopIteration:
                print(f"API密钥 {api_key[:8]}... 没有找到起始文档，跳过")
                continue
            
            # 只有当有数据需要处理时才获取结束ID
            thread_end_id = None
            if thread_start_id and thread_docs < total_count - current_skip:
                thread_end_doc = collection.find().sort("_id", pymongo.ASCENDING).skip(current_skip + thread_docs).limit(1)
                try:
                    thread_end_id = next(thread_end_doc)["_id"]
                except StopIteration:
                    # 如果没有下一个文档，表示这是最后一批
                    thread_end_id = None
            
            current_skip += thread_docs
            
            print(f"API密钥 {api_key[:8]}... 将处理从第 {current_skip - thread_docs + 1} 到第 {current_skip} 个景点 (共 {thread_docs} 个)")
            
            # 计算合适的批处理大小
            thread_batch_size = min(50, max(10, BATCH_SIZE // api_key_count))
            
            # 创建并启动线程
            thread = threading.Thread(
                target=process_attractions_with_key,
                args=(api_key, collection, thread_start_id, thread_end_id, thread_batch_size),
                name=f"APIThread-{api_key[:6]}"
            )
            threads.append(thread)
            thread.start()
        
        # 启动进度监控线程
        monitor_thread = threading.Thread(
            target=monitor_progress,
            args=(total_count,),
            name="ProgressMonitor"
        )
        monitor_thread.daemon = True  # 设为守护线程，主线程结束时自动结束
        monitor_thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 显示处理统计
        print("\n--- 处理统计 ---")
        total_processed = sum(prog["processed"] for prog in _thread_progress.values()) if _thread_progress else 0
        print(f"总计处理: {total_processed}/{total_count} 个景点 ({total_processed/total_count:.1%})")
        
        # 显示每个API密钥的统计
        print("\n--- API密钥使用统计 ---")
        for api_key, count in _api_key_counters.items():
            error_count = _api_key_errors.get(api_key, 0)
            print(f"API密钥 {api_key[:8]}...: 使用 {count} 次, 错误 {error_count} 次")
            
        # 完成处理
        elapsed_time = time.time() - start_time
        print(f"\n全部处理完成! 总耗时: {elapsed_time:.2f} 秒, 速率: {total_processed/elapsed_time:.2f} 景点/秒")
        
    except Exception as e:
        logger.error(f"处理过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭MongoDB连接
        if mongo_client:
            mongo_client.close()


if __name__ == "__main__":
    # 运行主程序
    print("\n===== 景区数据AI处理程序 =====")
    print("\n配置信息:")
    print(f"- MongoDB: {MONGO_CONNECTION_STRING}")
    print(f"- 数据库: {DB_NAME}.{COLLECTION_NAME}")
    print(f"- API密钥数量: {len(DEEPSEEK_API_KEYS)}")
    print(f"- 并发数: {MAX_WORKERS}")
    print(f"- 批处理大小: {BATCH_SIZE}")
    
    if len(DEEPSEEK_API_KEYS) == 1:
        print("\n提示: 您当前只配置了一个API密钥，可以通过设置环境变量DEEPSEEK_API_KEYS添加多个密钥来提高处理效率")
        print("      多个密钥请用逗号分隔，例如: export DEEPSEEK_API_KEYS=\"key1,key2,key3\"")
    
    choice = input("\n选择操作: 1=处理全部景点, q=退出: ")
    if choice == '1':
        confirm = input("确定要处理所有景点数据吗? 这可能需要较长时间 (y/n): ")
        if confirm.lower() == 'y':
            main()
    else:
        print("退出程序")
