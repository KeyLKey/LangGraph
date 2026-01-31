"""
主程序入口
多智能体网络安全防护助手
"""
import asyncio
import os
from dotenv import load_dotenv
from src.advanced_workflow import AdvancedCybersecurityWorkflow
from src.conversation_manager import conversation_manager

# 加载环境变量
load_dotenv()

def main():
    """主函数"""
    print("=== 多智能体网络安全防护助手 ===\n")
    
    # 创建工作流实例
    cybersecurity_agent = AdvancedCybersecurityWorkflow()
    
    # 示例查询
    example_queries = [
        "什么是勒索软件？",
        "分析这份CTI报告，判断是不是勒索软件攻击，并告诉我该怎么防御",
        "如何修复CVE-2023-1234漏洞？",
        "帮我分析一下这个安全事件：黑客通过钓鱼邮件获取了员工凭证，然后横向移动到财务系统",
        "ATT&CK框架中的T1566代表什么技术？",
        "最近有哪些重要的网络安全威胁？",
        "帮我写一首诗"  # 这个应该被安全护栏拦截
    ]
    
    print("运行示例查询：\n")
    for i, query in enumerate(example_queries, 1):
        print(f"{i}. 查询: {query}")
        result = cybersecurity_agent.run(query)
        print(f"   响应: {result['final_response']}")
        print()
    
    # 交互式模式
    print("=" * 50)
    print("进入交互模式 (输入 'quit' 或 'exit' 退出):")
    
    while True:
        try:
            user_input = input("\n请输入您的网络安全相关问题: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("感谢使用多智能体网络安全防护助手！")
                break
            
            if not user_input:
                continue
            
            # 运行工作流
            result = cybersecurity_agent.run(user_input)
            print(f"助手回复: {result['final_response']}")
            
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"处理查询时出现错误: {str(e)}")


if __name__ == "__main__":
    main()