"""
HumanEval Benchmark 测试 - LLM 代码生成能力评估

此脚本使用 HumanEval 数据集的子集测试 LLM 的代码生成能力。

实验任务:
1. 完成 generate_code 函数，调用 LLM 生成代码
3. 完成 calculate_pass_at_k 函数，计算评估指标

使用方法:
    python test_humaneval.py
"""

from openai import OpenAI
import os
from dotenv import load_dotenv
from datasets import load_dataset
import json
import time
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Any, Callable

# 加载环境变量
load_dotenv()

# 初始化客户端
client = OpenAI(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url=os.getenv("SILICONFLOW_BASE_URL")
)


def load_humaneval_subset(num_problems=10):
    """
    任务1: 加载 HumanEval 数据集的子集
    
    参数:
        num_problems: 要加载的问题数量
    
    返回:
        List[Dict]: 问题列表
    
    提示:
        - 使用 datasets 库的 load_dataset 函数
        - dataset = load_dataset("openai_humaneval", split="test")
        - 返回前 num_problems 个问题
    """
    # TODO: 实现此函数
    print(f"📥 加载 HumanEval 数据集的前 {num_problems} 个问题...")
    
    try:
        # TODO: 加载数据集
        dataset = load_dataset("openai_humaneval", split="test")
        
        # TODO: 提取前 num_problems 个问题
        problems = []
        for i in range(min(num_problems, len(dataset))):
            problems.append({
                "task_id": dataset[i]["task_id"],
                "prompt": dataset[i]["prompt"],
                "entry_point": dataset[i]["entry_point"],
                "test": dataset[i]["test"],
                "canonical_solution": dataset[i]["canonical_solution"]
            })
        
        print(f"✅ 成功加载 {len(problems)} 个问题")
        return problems
    
    except Exception as e:
        print(f"❌ 加载数据集失败: {e}")
        print("提示: 首次运行需要下载数据集，请确保网络连接正常")
        return []


def generate_code(client, prompt, temperature=0.2, max_tokens=512, num_samples=1):
    """
    任务2: 调用 LLM 生成代码
    
    参数:
        client: OpenAI 客户端
        prompt: 代码提示（包含函数签名和文档字符串）
        temperature: 温度参数
        max_tokens: 最大生成 token 数
        num_samples: 生成样本数量
    
    返回:
        List[str]: 生成的代码列表
    """
    # TODO: 实现此函数


def execute_code_with_test(code, test_code, entry_point):
    """
    任务3: 执行生成的代码并运行测试
    
    参数:
        code: 生成的代码
        test_code: 测试代码
        entry_point: 函数入口点名称
    
    返回:
        Tuple[bool, str]: (是否通过, 错误信息)
    
    提示:
        - 使用 exec() 在独立的命名空间中执行代码
        - 测试代码通过调用 check() 函数验证
        - 捕获所有可能的异常
        - 进阶: 可以使用 multiprocessing 实现超时机制
    """
    
    if code is None:
        return False, "Code generation failed"
    
    try:
        # 需要包含 __builtins__ 以便访问内置函数和类型注解
        namespace = {
            "__builtins__": __builtins__,
            "List": List,
            "Dict": Dict,
            "Tuple": Tuple,
            "Any": Any,
            "Callable": Callable
        }
        
        exec(code, namespace)
        
        if entry_point not in namespace:
            return False, f"Function '{entry_point}' not defined"
        
        exec(test_code, namespace)
        
        namespace["check"](namespace[entry_point])
        
        return True, None
    
    except AssertionError as e:
        return False, f"Assertion failed: {str(e)}"
    except SyntaxError as e:
        return False, f"Syntax error: {str(e)}"
    except Exception as e:
        return False, f"Runtime error: {type(e).__name__}: {str(e)}"


def calculate_pass_at_k(results, k=1):
    """
    任务4: 计算 pass@k 指标
    
    参数:
        results: List[Dict] 包含每个问题的测试结果
        k: k 值
    
    返回:
        float: pass@k 分数
    """
    # TODO: 实现此函数


def main():
    """主函数"""
    print("🚀 开始 HumanEval 代码生成能力测试")
    print()
    
    # 配置
    NUM_PROBLEMS = 10  # 测试问题数量
    TEMPERATURE = 0.2   # 温度参数
    NUM_SAMPLES = 1     # 每个问题生成的样本数
    
    # 加载数据集
    problems = load_humaneval_subset(NUM_PROBLEMS)
    
    if not problems:
        print("❌ 无法加载数据集，测试终止")
        return
    
    print()
    
    # 测试每个问题
    results = []
    
    for i, problem in enumerate(problems):
        print(f"\n{'='*60}")
        print(f"📝 测试问题 {i+1}/{len(problems)}: {problem['task_id']}")
        print(f"{'='*60}")
        
        # 显示问题
        print("问题描述:")
        print(problem["prompt"][:200] + "..." if len(problem["prompt"]) > 200 else problem["prompt"])
        print()
        
        # 生成代码
        codes = generate_code(
            client,
            problem["prompt"],
            temperature=TEMPERATURE,
            num_samples=NUM_SAMPLES
        )
        
        # 测试生成的代码
        passed = False
        error_msg = None
        
        for j, code in enumerate(codes):
            if code is None:
                continue
            
            print(f"\n测试样本 {j+1}/{len(codes)}...")
            success, error = execute_code_with_test(
                code,
                problem["test"],
                problem["entry_point"]
            )
            
            if success:
                print("✅ 测试通过!")
                passed = True
                break
            else:
                print(f"❌ 测试失败: {error}")
                error_msg = error
        
        # 记录结果
        results.append({
            "task_id": problem["task_id"],
            "passed": passed,
            "error": error_msg,
            "samples_tested": len([c for c in codes if c is not None])
        })  
        
        # TODO: 计算 pass@k 并显示
    
    print("\n✅ 测试完成!")


if __name__ == "__main__":
    main()
