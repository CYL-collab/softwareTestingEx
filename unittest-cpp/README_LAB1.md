# Minishell 单元测试实验

本目录包含 Minishell 项目的 GoogleTest 单元测试代码。

## 文件结构

```
unittest-cpp/
├── CMakeLists.txt              # CMake 构建配置
├── minishell_test_base.h       # 测试基类（提供辅助函数）
├── minishell_builtin_test.cc   # 内置命令测试（等价类划分）
├── minishell_redirect_test.cc  # 重定向功能测试（组合测试）
└── minishell_pipe_test.cc      # 管道功能测试（决策表测试）
```

## 前置条件

1. **编译 Minishell**：
   ```bash
   cd ../source/minishell
   make
   ```
   
   确保生成了 `minishell` 可执行文件。

2. **安装依赖**：
   - C++ 编译器（clang）
   - CMake (>= 3.14)
   - Make
   - GoogleTest（通过 CMake 自动下载）

## 构建和运行测试

### 1. 配置 CMake

```bash
cd unittest-cpp
cmake -S . -B build
```

### 2. 编译测试

```bash
cmake --build build
```

### 3. 运行所有测试

```bash
cd build
ctest --verbose
```

### 4. 运行特定测试

```bash
# 只运行内置命令测试
./minishell_builtin_test

# 只运行重定向测试
./minishell_redirect_test

# 只运行管道测试
./minishell_pipe_test
```

### 5. 运行特定测试用例

使用 GoogleTest 的过滤器：

```bash
# 运行所有 Echo 相关的测试
./minishell_builtin_test --gtest_filter=*Echo*

# 运行参数化测试
./minishell_builtin_test --gtest_filter=EchoParameterizedTest*

# 运行特定测试
./minishell_builtin_test --gtest_filter=MinishellTestBase.EchoSimpleString
```

## 实验任务

### 任务 1: 内置命令测试（minishell_builtin_test.cc）

实现并完成以下测试：
- [ ] 完成基础 echo 测试（3个 TODO）
- [ ] 为 echo 添加至少 5 个参数化测试用例
- [ ] 完成 pwd 命令测试
- [ ] 完成 env 命令测试
- [ ] 为 cd 命令添加至少 5 个边界值测试
- [ ] 完成 export/unset 命令测试
- [ ] 完成 exit 命令测试

**测试方法**：等价类划分、边界值分析

### 任务 2: 重定向功能测试（minishell_redirect_test.cc）

实现并完成以下测试：
- [ ] 完成输出重定向测试（`>`, `>>`）
- [ ] 完成输入重定向测试（`<`）
- [ ] 完成组合重定向测试
- [ ] 添加至少 6 个参数化组合测试
- [ ] 测试边界情况（空输出、不存在的文件等）

**测试方法**：组合测试、边界值分析

### 任务 3: 管道功能测试（minishell_pipe_test.cc）

实现并完成以下测试：
- [ ] 完成基础管道测试
- [ ] 完成管道与重定向组合测试
- [ ] 根据决策表实现至少 4 个测试规则
- [ ] 测试至少 3 个边界情况
- [ ] 测试错误处理

**测试方法**：决策表测试、边界值分析

## 常见问题

### Q1: 测试失败，提示找不到 minishell

**A**: 确保：
1. 已经编译了 minishell：`cd ../source/minishell && make`
2. 测试基类中的路径正确：检查 `minishell_test_base.h` 中的 `minishell_path`

### Q2: 如何调试失败的测试？

**A**: 
1. 使用 `--gtest_filter` 只运行失败的测试
2. 查看测试输出中的详细错误信息
3. 手动运行相同的命令验证 minishell 行为：
   ```bash
   echo "echo Hello" | ../../source/minishell/minishell
   ```

### Q3: 测试输出中包含额外的提示符信息怎么办？

**A**: 使用部分匹配而不是精确匹配：
```cpp
// 使用 find() 检查输出是否包含期望的字符串
EXPECT_TRUE(output.find("expected") != std::string::npos);
```

### Q4: 如何查看测试覆盖率？

**A**: 可以使用 gcov/lcov 工具：
```bash
# 在 CMakeLists.txt 中添加编译选项
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -coverage")

# 运行测试
cd build && ctest

# 生成覆盖率报告
lcov --capture --directory . --output-file coverage.info
genhtml coverage.info --output-directory coverage_report
```

## 参考资料

- [GoogleTest 官方文档](https://google.github.io/googletest/)
- [GoogleTest 参数化测试](https://google.github.io/googletest/advanced.html#value-parameterized-tests)
- [GoogleTest 断言参考](https://google.github.io/googletest/reference/assertions.html)

## 提交要求

完成所有 TODO 标记的测试后：
1. 确保所有测试都能编译通过
2. 运行 `ctest --verbose` 并截图测试结果
3. 在实验报告中说明：
   - 等价类划分的具体策略
   - 边界值选择的理由
   - 组合测试参数的选择依据
   - 遇到的问题和解决方案

## 评分标准

- 完成所有 TODO 标记的测试：40%
- 测试用例的质量和覆盖率：30%
- 黑盒测试方法的应用：20%
- 实验报告的完整性：10%
