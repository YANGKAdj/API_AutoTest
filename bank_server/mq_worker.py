import json
import time
import os
import sys

# 把上层目录加入系统路径，以便可以单独作为进程启动 worker
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bank_server.redis_client import get_redis_client
from bank_server.database import get_conn

def start_worker():
    client = get_redis_client()
    print("🚀 [*] 启动异步消息队列 Worker，开始阻塞监听 'queue:notifications' 队列...")
    
    while True:
        try:
            # BRPOP: 阻塞弹出队列最右侧（右进左出逻辑或左进右出，对应 lpush 和 brpop）
            # timeout=0 表示如果没有消息则永远阻塞等待，不消耗 CPU
            result = client.brpop("queue:notifications", timeout=0)
            if not result:
                continue
                
            queue_name, msg_json = result
            msg = json.loads(msg_json)
            
            # 消费消息：落库到 MySQL
            conn = get_conn()
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO notifications (user_id, title, content) VALUES (%s, %s, %s)",
                    (msg["user_id"], msg["title"], msg["content"])
                )
                conn.commit()
                print(f"✅ [MQ 消费成功] 用户 {msg['user_id']} | 标题: {msg['title']}")
            except Exception as inner_e:
                print(f"❌ [DB 异常] 无法保存通知: {inner_e}")
                conn.rollback()
            finally:
                conn.close()
                
        except Exception as e:
            print(f"❌ [Worker 异常] {e}")
            time.sleep(2)

if __name__ == "__main__":
    start_worker()
