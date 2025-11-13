#!/usr/bin/env python3
"""
提取并打包测试文件脚本
该脚本会收集所有的测试文件并打包成ZIP格式
"""

import os
import sys
import argparse
import zipfile
from pathlib import Path
from typing import List

def get_test_files() -> List[str]:
    """获取测试文件列表"""
    return [
        # C++ 测试文件
        "unittest-cpp/minishell_builtin_test.cc",
        "unittest-cpp/minishell_pipe_test.cc",
        "unittest-cpp/minishell_redirect_test.cc",
        
        # Python 测试文件
        "testing-ai/test_humaneval.py",
        "testing-ai/test_jailbreak.py",
        "testing-web/test_SwagLabs.py"
    ]

def pack_tests(base_dir: Path, output_path: Path) -> bool:
    """
    打包测试文件
    
    Args:
        base_dir: 项目根目录
        output_path: 输出ZIP文件的路径
        
    Returns:
        是否成功
    """
    test_files = get_test_files()
    
    # 如果输出文件已存在，删除它
    if output_path.exists():
        output_path.unlink()
        print(f"✓ 删除已存在的文件: {output_path}")
    
    # 创建ZIP文件
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path_str in test_files:
                file_path = base_dir / file_path_str
                
                if file_path.exists():
                    # 添加文件到ZIP，保持相对路径
                    arcname = file_path_str.replace(os.sep, '/')
                    zipf.write(file_path, arcname=arcname)
                    print(f"✓ 已添加: {file_path_str}")
                else:
                    print(f"✗ 文件不存在: {file_path_str}", file=sys.stderr)
                    return False
        
        # 获取ZIP文件信息
        file_size = output_path.stat().st_size
        file_size_kb = file_size / 1024
        
        print(f"\n✓ 打包成功!")
        print(f"\nZIP文件信息:")
        print(f"  文件名: {output_path.name}")
        print(f"  大小: {file_size_kb:.2f} KB")
        print(f"  路径: {output_path.absolute()}")
        
        return True
        
    except Exception as e:
        print(f"✗ 打包失败: {e}", file=sys.stderr)
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='提取并打包测试文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
例子:
  python pack_tests.py
  python pack_tests.py -o my_tests.zip
  python pack_tests.py --output ../test_files.zip
        '''
    )
    
    parser.add_argument(
        '-o', '--output',
        default='test_files.zip',
        help='输出ZIP文件的路径 (默认: test_files.zip)'
    )
    
    parser.add_argument(
        '-d', '--directory',
        default='.',
        help='项目根目录 (默认: 当前目录)'
    )
    
    args = parser.parse_args()
    
    # 获取路径
    base_dir = Path(args.directory).resolve()
    output_path = Path(args.output).resolve()
    
    if not base_dir.exists():
        print(f"✗ 错误: 目录不存在: {base_dir}", file=sys.stderr)
        sys.exit(1)
    
    print(f"项目目录: {base_dir}")
    print(f"输出文件: {output_path}")
    print()
    
    # 执行打包
    success = pack_tests(base_dir, output_path)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
