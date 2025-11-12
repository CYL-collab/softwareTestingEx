# 软件测试实验指导书
## 0 提交说明
本实验最终提交物为单个实验报告，请参考 `.\实验报告.md` 中要求撰写并提交。提交要求仅包含一个 PDF 格式的文件。

提交截止时间： **2025-12-21（校历第 17 周周日） 23:59:59**
提交地址： https://gist.nju.edu.cn/course-testing/project.html

## LAB1: Minishell 功能测试
### 1.1 实验目的

利用 C++ 单元测试框架 googletest 的特性，对 Minishell 项目进行系统性的黑盒测试，实践参数化测试、等价类划分、边界值分析等测试方法。

### 1.2 Minishell 项目介绍

Minishell 是一个简化版的 Unix Shell 实现，支持以下功能：

**基础命令执行**
- 可以执行绝对路径、相对路径或通过环境变量 PATH 查找的可执行文件（如 `/bin/ls` 或 `ls`）
- 支持命令参数和选项
- 支持单引号 `'` 和双引号 `"` 的字符串解析（不支持多行命令）

**命令分隔与重定向**
- 使用 `;` 分隔多个命令
- 支持输出重定向 `>` 和追加重定向 `>>`
- 支持输入重定向 `<`
- 支持管道 `|`

**环境变量与特殊变量**
- 支持环境变量如 `$HOME`、`$PATH` 等
- 支持特殊变量 `$?`（上一条命令的返回值）

**信号处理**
- `Ctrl-C` 中断当前程序
- `Ctrl-\` 退出当前程序
- `Ctrl-D` 发送 EOF

**内置命令（Built-in）**
- `echo`：输出文本，支持 `-n` 选项
- `pwd`：显示当前工作目录
- `cd`：切换目录
- `env`：显示环境变量
- `export`：设置环境变量
- `unset`：删除环境变量
- `exit`：退出 shell

### 1.3 环境配置

本实验需要在 Linux 或 macOS 环境下进行（Windows 用户可使用 WSL）。推荐使用 [VSCode](https://code.visualstudio.com/) 作为代码编辑器，并安装以下插件：

- C/C++ Extension Pack
- Python Extension Pack

然后，为了正确编译并使用 gtest 测试 Minishell，你将需要：
- 支持 C++14 及以上的 C++ 编译器
- 构建工具 CMake 和 Make
- Minishell 项目的编译依赖

具体过程可参考 [GoogleTest官方文档](https://google.github.io/googletest/quickstart-cmake.html)。以下是各平台的推荐配置。

#### 编译 Minishell

首先需要编译 Minishell 项目。在项目根目录下进入 `source/minishell` 目录：

````` bash
cd source/minishell
make
`````

编译成功后，会在当前目录生成 `minishell` 可执行文件。你可以手动测试：

````` bash
./minishell
minishell$ echo "Hello World"
Hello World
minishell$ exit
`````

#### 配置测试环境

对于 **Linux** 平台，编译器使用 clang，通过包管理器安装。以 Debian/Ubuntu 为例：
````` shell
sudo apt install gcc g++ cmake make clang
`````

对于 **Mac** 平台，我们同样推荐使用包管理器 [Homebrew](https://brew.sh/) 配置环境。在 Mac 终端内输入
````` shell
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
`````
以安装 Homebrew。随后安装所需软件：
````` shell
brew install gcc g++ cmake make clang
`````

为验证构建工具已正确安装，在终端输入
````` shell
cmake --version
make --version
clang --version
`````
若正确显示版本信息，表示工具已经安装并准备好使用。

### 1.4 GoogleTest 测试框架介绍

在 GoogleTest 中，定义了多种宏来编写测试。针对本实验的 Minishell 测试，我们将重点使用以下功能：

#### TEST 宏
`````C++
TEST(TestSuiteName, TestName) {
  ... statements ...
}
`````
在测试套件 `TestSuiteName` 中定义一个名为 `TestName` 的测试。

#### TEST_F 宏（测试夹具）
`````C++
TEST_F(TestFixtureName, TestName) {
  ... statements ...
}
`````
定义一个使用测试夹具类 `TestFixtureName` 的测试。测试夹具用于：
- 在每个测试前进行初始化（如启动 minishell 进程）
- 在每个测试后进行清理（如关闭进程、删除临时文件）
- 复用测试代码，减少重复

#### TEST_P 宏（参数化测试）
`````C++
TEST_P(TestFixtureName, TestName) {
  ... statements ...
}
`````
定义一个值参数化测试，使用测试夹具类 `TestFixtureName`。参数化测试的优势：
- **减少重复代码**：相同的测试逻辑可以应用于不同的输入数据
- **提高测试覆盖率**：轻松测试大量输入组合
- **便于维护**：修改测试逻辑时只需改一处

参数化测试特别适合测试 Shell 命令，因为：
- 同一个命令可能有多种输入组合（参数、选项、边界值）
- 可以系统性地测试等价类和边界值
- 便于实施黑盒测试方法

#### INSTANTIATE_TEST_SUITE_P 宏
`````C++
INSTANTIATE_TEST_SUITE_P(InstantiationName,
                         TestSuiteName,
                         param_generator)
`````
实例化参数化测试套件，其中 `param_generator` 可以是：
- `Values(v1, v2, v3, ...)`: 显式指定参数值
- `ValuesIn(container)`: 从容器中读取参数
- `Range(begin, end, step)`: 生成范围内的参数
- `Combine(g1, g2, ...)`: 组合多个参数生成器（笛卡尔积）

#### 断言宏

GoogleTest 提供了丰富的断言宏用于验证测试结果：

**字符串比较断言**（Shell 测试中最常用）：
- `EXPECT_STREQ(str1, str2)`: 期望两个 C 字符串相等
- `EXPECT_STRNE(str1, str2)`: 期望两个 C 字符串不相等
- `EXPECT_STRCASEEQ(str1, str2)`: 忽略大小写比较
- `EXPECT_THAT(value, matcher)`: 使用匹配器进行复杂字符串匹配

**基本断言**：
- `EXPECT_TRUE(condition)`: 期望条件为真
- `EXPECT_FALSE(condition)`: 期望条件为假
- `EXPECT_EQ(val1, val2)`: 期望两个值相等
- `EXPECT_NE(val1, val2)`: 期望两个值不相等

**EXPECT vs ASSERT**：
- `EXPECT_*`: 失败时记录错误，继续执行后续测试
- `ASSERT_*`: 失败时立即终止当前测试用例

更多断言宏可参考 [GoogleTest 官方文档](https://google.github.io/googletest/reference/assertions.html)。

### 1.5 实验内容

本实验将对 Minishell 的各项功能进行系统性测试，综合运用等价类划分、边界值分析等黑盒测试方法，并使用参数化测试提高测试效率。

#### 1.5.1 基础测试框架搭建

首先，我们需要创建一个测试辅助类来与 Minishell 进程交互。创建 `unittest-cpp/minishell_test_base.h`：

`````C++
#ifndef MINISHELL_TEST_BASE_H
#define MINISHELL_TEST_BASE_H

#include <gtest/gtest.h>
#include <string>
#include <array>
#include <memory>
#include <stdexcept>

class MinishellTestBase : public ::testing::Test {
protected:
    std::string minishell_path = "../../source/minishell/minishell";
    
    // 执行命令并获取输出
    std::string executeCommand(const std::string& command) {
        std::string full_command = "echo \"" + command + "\" | " + minishell_path;
        return execShellCommand(full_command);
    }
    
    // 执行命令并获取退出码
    int executeCommandGetExitCode(const std::string& command) {
        std::string full_command = "echo \"" + command + "\" | " + minishell_path + "; echo $?";
        std::string output = execShellCommand(full_command);
        // 解析最后一行获取退出码
        size_t pos = output.find_last_of('\n');
        if (pos != std::string::npos && pos > 0) {
            pos = output.find_last_of('\n', pos - 1);
            if (pos != std::string::npos) {
                return std::stoi(output.substr(pos + 1));
            }
        }
        return -1;
    }
    
private:
    std::string execShellCommand(const std::string& cmd) {
        std::array<char, 128> buffer;
        std::string result;
        std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd.c_str(), "r"), pclose);
        if (!pipe) {
            throw std::runtime_error("popen() failed!");
        }
        while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
            result += buffer.data();
        }
        return result;
    }
};

#endif // MINISHELL_TEST_BASE_H
`````

创建 `unittest-cpp/CMakeLists.txt`：

````` cmake
cmake_minimum_required(VERSION 3.14)
project(minishell-tests)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)
FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/ff233bdd4cac0a0bf6e5cd45bda3406814cb2796.zip
)
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

enable_testing()

# 定义测试可执行文件
add_executable(minishell_builtin_test minishell_builtin_test.cc)
target_link_libraries(minishell_builtin_test GTest::gtest_main)

add_executable(minishell_redirect_test minishell_redirect_test.cc)
target_link_libraries(minishell_redirect_test GTest::gtest_main)

add_executable(minishell_pipe_test minishell_pipe_test.cc)
target_link_libraries(minishell_pipe_test GTest::gtest_main)

include(GoogleTest)
gtest_discover_tests(minishell_builtin_test)
gtest_discover_tests(minishell_redirect_test)
gtest_discover_tests(minishell_pipe_test)
`````

#### 1.5.2 内置命令测试（等价类划分）

**测试目标**：测试 `echo` 命令的各种使用情况

**等价类划分分析**：

根据 `echo` 命令的功能，可以划分以下等价类：

1. **输入类型等价类**：
   - 有效等价类：
     - EC1: 普通字符串（无特殊字符）
     - EC2: 包含空格的字符串
     - EC3: 空字符串
     - EC4: 包含环境变量的字符串
     - EC5: 包含特殊字符的字符串（需要引号）
   - 无效等价类：
     - EC6: 未定义的环境变量

2. **选项等价类**：
   - EC7: 无选项
   - EC8: `-n` 选项（不输出换行符）
   - EC9: 无效选项

3. **引号使用等价类**：
   - EC10: 单引号字符串
   - EC11: 双引号字符串
   - EC12: 混合引号

创建 `unittest-cpp/minishell_builtin_test.cc`：

`````C++
#include "minishell_test_base.h"
#include <gtest/gtest.h>

// ========== echo 命令测试 ==========

// 任务1: 完成基础 echo 测试
TEST_F(MinishellTestBase, EchoSimpleString) {
    std::string output = executeCommand("echo Hello");
    // TODO: 使用 EXPECT_THAT 或 EXPECT_STREQ 验证输出包含 "Hello"
    // 提示: 输出可能包含额外的 minishell 提示符，考虑使用部分匹配
}

TEST_F(MinishellTestBase, EchoEmptyString) {
    std::string output = executeCommand("echo");
    // TODO: 验证输出是否只包含换行符
}

TEST_F(MinishellTestBase, EchoWithSpaces) {
    // TODO: 测试包含多个空格的字符串
    // 提示: echo "Hello   World" 应该保留空格
}

// 参数化测试示例：测试不同的 echo 输入
struct EchoTestParam {
    std::string input;
    std::string expected_output;
    std::string description;
};

class EchoParameterizedTest : public MinishellTestBase,
                               public ::testing::WithParamInterface<EchoTestParam> {
};

TEST_P(EchoParameterizedTest, EchoVariousInputs) {
    EchoTestParam param = GetParam();
    std::string output = executeCommand("echo " + param.input);
    // TODO: 验证输出是否包含期望的字符串
}

// 任务2: 完成参数实例化
// 提示: 测试以下情况:
// - echo "Hello World"
// - echo 'Single Quotes'
// - echo $HOME (环境变量)
// - echo "$USER is home" (包含环境变量的字符串)
INSTANTIATE_TEST_SUITE_P(
    EchoTests,
    EchoParameterizedTest,
    ::testing::Values(
        // TODO: 在此添加测试参数
        EchoTestParam{"\"Hello World\"", "Hello World", "Double quoted string"},
        EchoTestParam{"'Single Quotes'", "Single Quotes", "Single quoted string"}
        // 继续添加更多测试用例...
    )
);

// ========== pwd 命令测试 ==========

TEST_F(MinishellTestBase, PwdOutputsCurrentDirectory) {
    // TODO: 执行 pwd 命令并验证输出是否为有效的目录路径
    // 提示: 可以与系统的 getcwd() 结果比较
}

// ========== env 命令测试 ==========

TEST_F(MinishellTestBase, EnvShowsEnvironmentVariables) {
    std::string output = executeCommand("env");
    // TODO: 验证输出包含至少一个环境变量（如 PATH, HOME）
    // 提示: 使用 EXPECT_TRUE(output.find("PATH=") != std::string::npos)
}

// ========== cd 命令测试（边界值分析）==========

class CdCommandTest : public MinishellTestBase,
                      public ::testing::WithParamInterface<std::string> {
};

TEST_P(CdCommandTest, ChangeDirectory) {
    std::string target_dir = GetParam();
    // TODO: 执行 cd 命令，然后执行 pwd 验证目录是否改变
    // 提示: executeCommand("cd " + target_dir + " && pwd")
}

// 任务3: 完成 cd 命令的边界值测试
// 测试以下情况:
// - cd ~ (home目录)
// - cd / (根目录)
// - cd . (当前目录)
// - cd .. (父目录)
// - cd /nonexistent (不存在的目录)
INSTANTIATE_TEST_SUITE_P(
    CdBoundaryTests,
    CdCommandTest,
    ::testing::Values(
        // TODO: 添加边界值测试参数
        "~",
        "/"
        // 继续添加...
    )
);

// ========== export 和 unset 命令测试 ==========

TEST_F(MinishellTestBase, ExportAndUnsetVariable) {
    // 任务4: 完成以下测试
    // 1. 使用 export 设置一个新的环境变量
    // 2. 使用 echo 验证该变量已设置
    // 3. 使用 unset 删除该变量
    // 4. 再次 echo 验证该变量已删除
    
    // TODO: 实现测试逻辑
}

// ========== exit 命令测试 ==========

TEST_F(MinishellTestBase, ExitCommand) {
    // 任务5: 测试 exit 命令
    // 提示: 可以测试 "exit 0", "exit 42" 等，验证退出码
    int exit_code = executeCommandGetExitCode("exit 42");
    // TODO: 验证退出码是否为 42
}
`````

**实验要求**：
1. 完成所有标记为 `TODO` 的测试用例
2. 为 `echo` 命令至少添加 5 个参数化测试用例，覆盖不同的等价类
3. 为 `cd` 命令完成边界值测试，至少包含 5 个测试点
4. 完成 `export/unset` 和 `exit` 命令的测试
5. 编译并运行测试，确保所有测试通过

**编译运行**：
````` bash
cd unittest-cpp
cmake -S . -B build
cmake --build build
cd build && ctest --verbose
`````

#### 1.5.3 重定向功能测试（组合测试）

**测试目标**：测试输入/输出重定向功能（`>`, `>>`, `<`）

**测试策略**：使用 `Combine()` 测试不同命令和重定向方式的组合

创建 `unittest-cpp/minishell_redirect_test.cc`：

`````C++
#include "minishell_test_base.h"
#include <gtest/gtest.h>
#include <fstream>
#include <cstdio>

class RedirectTest : public MinishellTestBase {
protected:
    std::string temp_file = "/tmp/minishell_test_output.txt";
    std::string input_file = "/tmp/minishell_test_input.txt";
    
    void SetUp() override {
        // 清理可能存在的测试文件
        std::remove(temp_file.c_str());
        std::remove(input_file.c_str());
    }
    
    void TearDown() override {
        // 清理测试文件
        std::remove(temp_file.c_str());
        std::remove(input_file.c_str());
    }
    
    std::string readFile(const std::string& filename) {
        std::ifstream file(filename);
        std::string content((std::istreambuf_iterator<char>(file)),
                           std::istreambuf_iterator<char>());
        return content;
    }
    
    void writeFile(const std::string& filename, const std::string& content) {
        std::ofstream file(filename);
        file << content;
    }
};

// ========== 输出重定向测试 ==========

TEST_F(RedirectTest, SimpleOutputRedirect) {
    // 任务1: 测试基本输出重定向
    executeCommand("echo 'Hello World' > " + temp_file);
    std::string content = readFile(temp_file);
    // TODO: 验证文件内容是否为 "Hello World\n"
}

TEST_F(RedirectTest, OutputRedirectOverwrite) {
    // 任务2: 测试输出重定向是否会覆盖已存在的文件
    writeFile(temp_file, "Old content\n");
    executeCommand("echo 'New content' > " + temp_file);
    std::string content = readFile(temp_file);
    // TODO: 验证文件内容是否被覆盖为 "New content\n"
}

TEST_F(RedirectTest, AppendRedirect) {
    // 任务3: 测试追加重定向
    executeCommand("echo 'Line 1' > " + temp_file);
    executeCommand("echo 'Line 2' >> " + temp_file);
    std::string content = readFile(temp_file);
    // TODO: 验证文件包含两行内容
}

// ========== 输入重定向测试 ==========

TEST_F(RedirectTest, InputRedirect) {
    // 任务4: 测试输入重定向
    writeFile(input_file, "test input\n");
    std::string output = executeCommand("cat < " + input_file);
    // TODO: 验证输出是否为文件内容
}

// ========== 参数化测试：组合测试不同命令和重定向方式 ==========

struct RedirectCombineParam {
    std::string command;
    std::string redirect_op;
    std::string content;
};

class RedirectCombineTest : public RedirectTest,
                            public ::testing::WithParamInterface<RedirectCombineParam> {
};

TEST_P(RedirectCombineTest, CombinedRedirectTest) {
    RedirectCombineParam param = GetParam();
    
    // 构建完整命令
    std::string full_command = param.command + " " + param.redirect_op + " " + temp_file;
    executeCommand(full_command);
    
    std::string content = readFile(temp_file);
    // TODO: 根据参数验证输出
}

// 任务5: 使用 Combine 创建组合测试
// 组合不同的命令 (echo, ls, pwd) 和重定向操作符 (>, >>)
INSTANTIATE_TEST_SUITE_P(
    RedirectCombinations,
    RedirectCombineTest,
    ::testing::Values(
        // TODO: 添加不同的组合参数
        RedirectCombineParam{"echo 'test'", ">", "test"},
        RedirectCombineParam{"echo 'append'", ">>", "append"}
        // 继续添加更多组合...
    )
);
`````

**实验要求**：
1. 完成所有 `TODO` 标记的测试
2. 使用 `Combine()` 或 `Values()` 创建至少 6 个组合测试用例
3. 测试边界情况：空文件、不存在的文件、多次重定向等

#### 1.5.4 管道功能测试（决策表测试）

**测试目标**：测试管道 `|` 功能以及管道与其他功能的组合

**决策表分析**：

管道功能涉及多个条件的组合：

| 条件 | C1: 命令1有效 | C2: 命令2有效 | C3: 有重定向 | 预期结果 |
|------|--------------|--------------|-------------|----------|
| R1   | Y            | Y            | N           | 成功     |
| R2   | Y            | Y            | Y           | 成功     |
| R3   | Y            | N            | N           | 失败     |
| R4   | N            | Y            | N           | 失败     |

创建 `unittest-cpp/minishell_pipe_test.cc`：

`````C++
#include "minishell_test_base.h"
#include <gtest/gtest.h>

// ========== 基础管道测试 ==========

TEST_F(MinishellTestBase, SimplePipe) {
    // 任务1: 测试基本管道功能
    std::string output = executeCommand("echo 'hello' | cat");
    // TODO: 验证输出
}

TEST_F(MinishellTestBase, MultiplePipes) {
    // 任务2: 测试多重管道
    std::string output = executeCommand("echo 'test' | cat | cat");
    // TODO: 验证输出
}

TEST_F(MinishellTestBase, PipeWithGrep) {
    // 任务3: 测试管道与 grep 组合
    std::string output = executeCommand("echo -e 'line1\\nline2\\nline3' | grep 'line2'");
    // TODO: 验证只输出 line2
}

// ========== 管道与重定向组合测试 ==========

TEST_F(MinishellTestBase, PipeWithRedirect) {
    // 任务4: 测试管道与重定向组合
    // 提示: echo "test" | cat > /tmp/test_output.txt
    // TODO: 实现测试
}

// ========== 参数化测试：不同的管道组合 ==========

struct PipeTestParam {
    std::string command;
    std::string expected_behavior;
    bool should_succeed;
};

class PipeParameterizedTest : public MinishellTestBase,
                               public ::testing::WithParamInterface<PipeTestParam> {
};

TEST_P(PipeParameterizedTest, PipeVariousCombinations) {
    PipeTestParam param = GetParam();
    
    if (param.should_succeed) {
        std::string output = executeCommand(param.command);
        // TODO: 验证成功的情况
    } else {
        // TODO: 验证失败的情况（检查退出码或错误信息）
    }
}

// 任务5: 实现决策表中的测试用例
INSTANTIATE_TEST_SUITE_P(
    PipeDecisionTable,
    PipeParameterizedTest,
    ::testing::Values(
        // TODO: 根据决策表添加测试参数
        // R1: 两个有效命令，无重定向
        PipeTestParam{"echo 'test' | cat", "success", true},
        // R2: 两个有效命令，有重定向
        PipeTestParam{"echo 'test' | cat > /tmp/out.txt", "success", true}
        // 继续添加 R3, R4...
    )
);

// ========== 边界值测试 ==========

TEST_F(MinishellTestBase, EmptyPipe) {
    // 任务6: 测试空管道
    std::string output = executeCommand(" | cat");
    // TODO: 验证行为
}

TEST_F(MinishellTestBase, PipeWithEmptyCommand) {
    // 任务7: 测试管道前后有空命令
    std::string output = executeCommand("echo 'test' | ");
    // TODO: 验证行为
}
`````

**实验要求**：
1. 完成所有 `TODO` 标记的测试
2. 根据决策表实现至少 4 个测试规则
3. 测试至少 3 个边界情况
4. 测试管道与重定向的组合（至少 2 种组合）

**编译运行**：
````` bash
cd unittest-cpp
cmake -S . -B build
cmake --build build
cd build && ctest --verbose
`````

### 1.6 思考题

请依据实验内容简要回答下列思考题：

1. 在 Shell 测试中，为什么 `EXPECT_*` 断言比 `ASSERT_*` 断言更常用？什么情况下应该使用 `ASSERT_*`？
2. 在参数化测试中，如何选择代表性的测试参数以达到较高的测试覆盖率同时避免测试用例过多？
3. 对于 `cd` 命令的测试，除了边界值分析外，还可以使用哪些黑盒测试方法？请举例说明。
4. 如果要测试 Minishell 的引号处理功能（单引号、双引号、嵌套引号），应该如何设计等价类？
5. 使用 `Combine()` 进行组合测试时，如何避免组合爆炸问题？## 2 Java 单元测试
### 2.1 实验目的

使用 Java 单元测试框架 JUnit 的特性，实践部分黑盒和白盒测试方法。

### 2.2 环境配置

安装 ≥ Java 8 的 Java Development Kit,本实验推荐版本为 OpenJDK 21。

Windows平台可：
- 通过[该链接](https://learn.microsoft.com/zh-cn/java/openjdk/download)由 msi 安装包安装。
- 通过包管理器安装。
  - WinGet ：``winget install Microsoft.OpenJDK.21``
  - Scoop: ``scoop bucket add java``添加库后，``scoop install openjdk``

Linux 和 Mac 端可直接通过包管理器安装：
- Debian/Ubuntu：``sudo apt install openjdk-21-jdk``
- Mac: ``brew install openjdk@21``

作为 Java 上最流行的单元测试框架， JUnit 可以方便地通过 Maven 和 Gradle 等构建工具集成到软件项目之中。在本实验中，我们使用 Maven 进行构建。Maven 依赖于 Java SDK 运行，因此 OpenJDK 和 Maven 的安装顺序不可颠倒。

Windows平台可：
- 通过 [Maven 官网](https://maven.apache.org/download.cgi) 下载压缩包。解压到任意位置，并将``Maven文件夹路径/bin``目录添加到系统环境变量 ``PATH`` 中。Windows的环境变量可通过“控制面板”>“系统和安全”>“系统”>“高级系统设置”，“系统属性”窗口中，点击“环境变量”，在其中找到“系统变量”区域下的“PATH”变量，选择它，然后点击“编辑”即可。
- 通过包管理器安装。
  - Scoop: ``scoop install maven``

Linux和Mac端可直接通过包管理器安装：
- Debian/Ubuntu：``sudo apt install maven``
- Mac: ``brew install maven``

在 ``unittest-java`` 文件夹中，项目文件结构如下：
`````
unittest-java/
|-- pom.xml
`-- src/
    |-- main/
    |   `-- java/
        `-- resources/
    `-- test/
        `-- java/
        `-- resources/    
`````

其中 ``src/main/java`` 存放项目的主要 Java 源代码,``src/test/java`` 存放项目的测试代码，``pom.xml`` 定义了项目的依赖、插件和其他构建相关的设置。

### 2.3 JUnit 用法介绍

JUnit 的核心注解和断言语法使得它非常易于使用。以下是 JUnit 中常用的基本语法：

#### 注解（Annotations）

JUnit 通过注解来标记测试方法和测试生命周期，常用注解包括：

- @Test：标记一个方法为测试方法。
- @Before：每个测试方法执行前执行，用于准备工作（JUnit 4）。
- @BeforeEach：每个测试方法执行前执行，用于初始化资源（JUnit 5）。
- @After：每个测试方法执行后执行，用于清理工作（JUnit 4）。
- @AfterEach：每个测试方法执行后执行，用于清理资源（JUnit 5）。
- @BeforeClass：在所有测试方法之前只执行一次，用于全局初始化（JUnit 4）。
- @BeforeAll：在所有测试方法之前只执行一次（JUnit 5）。
- @AfterClass：在所有测试方法之后只执行一次，用于全局清理（JUnit 4）。
- @AfterAll：在所有测试方法之后只执行一次（JUnit 5）。
- @Ignore：忽略该测试方法，不执行。

#### 断言（Assertions）

断言用于验证测试执行的预期结果，JUnit 提供的断言方法包括：

- assertEquals(expected, actual)：断言两个值相等。
- assertNotEquals(unexpected, actual)：断言两个值不相等。
- assertTrue(condition)：断言条件为 true。
- assertFalse(condition)：断言条件为 false。
- assertNull(object)：断言对象为 null。
- assertNotNull(object)：断言对象不为 null。
- assertArrayEquals(expectedArray, actualArray)：断言数组相等。
- assertThrows()：断言抛出指定的异常。

### 2.4 实验内容

接下来我们将使用 JUnit 实现几种经典的黑盒和白盒测试方法。

#### 2.4.1 等价类划分

等价类划分是将所有可能的输入数据（包括输出）按照规则划分为若干个“等价类”，每个等价类内的数据从程序的角度来看是相同的。对每个等价类至少选取一个代表性数据作为测试案例。这些类通常被分为两大类：

- 有效等价类：合法的、预期能被系统正确处理的输入数据。
- 无效等价类：不合法的、预期会被系统拒绝或特殊处理的输入数据。

本部分的测试对象是 ``Date`` 类中的 ``next()`` 方法，它会提供当前日期的下一天。对于该问题，可以通过查看 ``Date.java`` 的源码，观察程序如何处理不同种类日期，以划分等价类。``DateTests.java`` 已提供了一个普通月份中间日的测试用例，请完成剩余等价类的测试用例，并在实验报告中列出具体的划分策略。

完成用例后，在 ``./unittest-java`` 目录下使用 ``mvn test`` 运行测试。

#### 2.4.2 边界值分析

根据软件测试实践经验来看，错误往往发生在输入或输出范围的边界而非中间值上。因此，边界值分析方法侧重于选取等价类的边界值。

以密码验证功能为例，该功能通常包含一系列规则，比如密码的最小长度、最大长度、必须包含的字符种类等。现有一个密码验证类 ``PasswordValidator``，要求对输入的密码进行验证。密码规则如下：

- 密码长度：至少8个字符，最多20个字符。
- 必须包含至少一个数字。
- 必须包含至少一个大写字母。
- 必须包含至少一个特殊字符（特殊字符范围为!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~）。

现提供了一个 ``PasswordValidator`` 的实现。请注意，这个实现是有缺陷的。请在 ``PasswordValidatorTests`` 用边界值分析的方法对密码验证功能进行测试，找到该缺陷，并修复它。

完成用例后，在 ``./unittest-java`` 目录下使用 ``mvn test`` 运行测试。

#### 2.4.3 覆盖率度量

在白盒测试中，覆盖率分析对于优化测试策略，提升代码质量的意义重大。本节将应用覆盖率分析工具 OpenClover，生成行、分支、条件、方法等多种覆盖率度量，并以可视化覆盖率报告的形式。

为在项目中引入 OpenClover，你需要修改 ``pom.xml``，引入 OpenClover 插件。完成后，在 ``./unittest-java`` 目录下使用 ``mvn clover:instrument test clover:clover``  进行Clover 的代码插桩，运行测试，并生成覆盖率报告，默认报告路径在 ``.\target\site\clover\index.html`` 中。

请分析可视化 HTML 报告中各个覆盖率数据的含义，以及它们对于指导软件测试的意义。

## 2.5 思考题

请依据实验内容简要回答下列思考题：

1. 除了 `2.4.1` 中设计等价类测试用例时，如何确保测试用例的代表性？
2. 为什么边界值容易出错？边界值分析和等价类划分如何结合使用？

## 3 Web 测试
### 3.1 实验目的

基于 Web 自动化工具 Selenium, 对 Web 服务进行功能性测试。

### 3.2 环境配置

Selenium是一个广泛用于Web应用的自动化测试工具，基于WebDriver协议构建，支持多种编程语言，包括但不限于 Java、C#、Python、Ruby、JavaScript 等。在此我们推荐[在 Python 安装 Selenium 库](https://www.selenium.dev/zh-cn/documentation/webdriver/getting_started/install_library/). 同时本部分还需要用到 Python 的单元测试库 ``unittest`` 及其参数化库``parameterized``。为此，你需要在本机上安装 Python：

在 Window 上，使用 WinGet：
`````bash
winget install Python.Python.3.12
`````

Mac 上:

`````zsh
brew install python
`````

很多 Linux 发行版通常预装了 Python，可以通过运行 python 或 python --version 来检查。

接下来，使用 pip 为 Python 安装所需的库：

`````bash
pip install selenium parameterized allure-pytest
`````

Selenium 需要使用 WebDriver 提供的接口，以驱动浏览器的自动化运行。在新版本的 Selenium 中，这一过程被自动管理，无需手动干预。

为确认安装，请运行 ``./web-test/helloweb.py``，确认浏览器正常弹出并完成自动化操作。运行前请修改 driver 至本机使用的浏览器。

### 3.3 Selenium 用法

如 ``./web-test/helloweb.py`` 所示的，使用 Selenium 编写的测试脚本通常包括：
- 启动浏览器会话：以Chrome为例，``driver = webdriver.Chrome(options=options)``
- 浏览器导航: 包括打开网站、后退、前进、刷新页面等操作
  - 打开网站: ``driver.get("https://www.example.com")``
  - 后退: ``driver.back()``
  - 前进: ``driver.forward()``
  - 刷新: ``driver.refresh()``
  亦支持通过获取当前浏览器相关信息,包括窗口句柄、浏览器尺寸 / 位置、cookie等。例如，可使用 ``driver.current_url`` 获取当前网址URL，使用 ``driver.title`` 获取当前网页标题。
- 等待策略: 为保证代码与浏览器的当前状态同步,可使用隐式或显式的方法在操作间设置等待。注意不要混合使用隐式和显式等待，以避免不可预测的等待时间。
  - 隐式等待：全局设置，适用于整个会话的每个元素位置调用。``driver.implicitly_wait(2)``
  - 显式等待：直接添加到代码中，用于轮询应用程序以获取特定条件.
    `````python
      wait = WebDriverWait(driver, timeout=2)
      wait.until(lambda d : revealed.is_displayed())
    `````
- 元素操作: 大多数会话内操作都与元素有关。为此，Selenium可进行
  - [查找元素](https://www.selenium.dev/zh-cn/documentation/webdriver/elements/finders/): 使用 driver.find_element 可使用多种测试快速定位页面上的元素。在 find_element 中传入 By 类的定位器策略即可。
    `````python
    from selenium.webdriver.common.by import By

    # 使用 By.ID 定位
    element = driver.find_element(By.ID, "element_id")

    # 使用 By.NAME 定位
    element = driver.find_element(By.NAME, "element_name")

    # 使用 By.XPATH 定位
    element = driver.find_element(By.XPATH, "//div[@id='element_id']")

    # 使用 By.LINK_TEXT 定位
    element = driver.find_element(By.LINK_TEXT, "链接文本")

    # 使用 By.PARTIAL_LINK_TEXT 定位
    element = driver.find_element(By.PARTIAL_LINK_TEXT, "部分链接文本")

    # 使用 By.TAG_NAME 定位
    element = driver.find_element(By.TAG_NAME, "tag_name")

    # 使用 By.CLASS_NAME 定位
    element = driver.find_element(By.CLASS_NAME, "class_name")

    # 使用 By.CSS_SELECTOR 定位
    element = driver.find_element(By.CSS_SELECTOR, "css_selector")
    `````
    
    在浏览器中，可使用开发者工具快速定位网页元素。以 Edge 为例，按下 F12 打开开发者工具，在 Elements 选项卡中点击左上角的选择元素工具，即可快速选中元素并查看其属性。
  - [操作元素](https://www.selenium.dev/zh-cn/documentation/webdriver/elements/interactions/): 包括五种基本指令：点击（``element.click()``）、发送键位（``element.send_keys("foo")``）、清除(``element.clear()``)，提交表单（不推荐使用），和选择列表元素（``Select(select_element)``）。

  - [获取元素信息](https://www.selenium.dev/zh-cn/documentation/webdriver/elements/information/): 查询元素的属性。
- 结束会话：``driver.quit()``

### 3.4 实验内容

#### 3.4.1 基于 unittest 编写测试用例

本实验将对一个[虚拟的线上购物系统](https://www.saucedemo.com/)进行功能性测试，确保购物流程正常运行。我们的测试内容包括：
- 登录功能
  - 输入正确的用户名和密码，验证是否成功登录，并跳转到商品显示界面。
  - 输入错误的用户名或密码，或被封号的用户，验证是否显示错误提示信息。
- 购物车功能
  - 测试从产品列表页添加商品到购物车的功能是否正常。
  - 验证是否能够更新购物车中的商品数量。
  - 测试是否能够删除购物车中的商品。
- 结算和支付功能
  - 测试是否能完成填写收货信息、确认订单的步骤。

示例代码 ``./testing-web/test_SwagLabs.py`` 使用 Python 的 unittest 框架和 Selenium 来进行在线购物系统的自动化功能测试。请根据下列要求补全其实现：
1. 本文件已在 ``test_login_success`` 实现对正确用户名和密码的测试，请参考此，利用类里已有的 ``login`` 方法实现：
   1. ``test_login_wrong``：错误的用户名和密码下，是否登录失败并显示相应错误提示；
   2. ``test_login_wrong``：使用被封禁的用户名 ``locked_out_user``，是否登录失败并显示相应错误提示。
2. 请参考其他测试用例的实现，完成 ``test_add_to_cart`` 用例，测试从产品列表页添加商品到购物车的功能是否正常，直至所有测试用例均通过。
3. 修改 ``test_add_to_cart`` 用例，将用户名改为 ``error_user``，再次运行同一测试，观察报错并说明哪些组件的功能不正常。

使用本机的 Python 环境，在`` ./testing-web ``目录下运行 ``python test_SwagLabs.py``,或使用即可自动运行所有 ``test_`` 开头的测试用例。

#### 3.4.2 基于 Allure 生成测试报告

直接使用 ``unittest`` 生成的测试结果并不直观，使用第三方工具如 Allure 可生成更友好的报告界面，便于快速理解测试结果。请基于 Allure，查看 ``test_add_to_cart`` 用例在 ``error_user`` 下的运行情况。具体使用步骤如下：

1. 参照官方文档安装 [Allure](https://allurereport.org/docs/install/).安装完成后，在命令行运行 ``allure --version`` 应显示对应版本号。
2. 在 ``./testing-web`` 目录下执行 ``pytest --alluredir=allure-results``，执行测试并生成 Allure 报告所需的数据 ``allure-results``
3. 使用 Allure 命令行工具生成和查看报告 ``allure serve allure-results``

请说明哪些测试用例报错了？体现了什么功能性缺陷？

## 3.5 思考题

请依据实验内容简要回答下列思考题：

- 如果在该在线购物网站中加入了优惠券系统（限定使用时间内满x元减y元），将会需要哪些额外的功能性测试？请列出具体测试用例。

## 4 移动应用测试

### 4.1 实验目的
基于 Web 自动化工具 Appium, 对一个真实安卓应用进行功能性和非功能性测试。

### 4.2 环境配置

作为最好的开源移动应用测试自动化框架之一，Appium 同样基于 Selenium WebDriver 开发，支持使用相同的 API 为不同平台编写 UI 测试，并提供对不同编程语言的支持。在此我们以Python为例。

首先安装 Node.js，不同平台的安装方式可参考[文档](https://nodejs.org/zh-cn/download)。

通过 Node.js 的包管理工具 npm 安装 Appium Server

```bash
npm install -g appium
```

安装Driver。对于安卓系统，需要[安装对应驱动](https://appium.io/docs/zh/2.5/quickstart/uiauto2-driver/)：

```bash
appium driver install uiautomator2
```

uiautomator2 驱动的运行需要 Android SDK 和 Java JDK 的支持，为此，我们需要配置 Android SDK: 
- 安装[Android Studio](https://developer.android.com/studio)，在 Android Studio 欢迎页点击 More Actions → SDK Manager，在 SDK Platforms 选项卡中，选择你需要的 Android 版本；切换到 SDK Tools 选项卡，勾选 Android SDK Platform-Tools 和 Android Emulator。点击 OK，等待 Android Studio 下载并安装所选的工具。
- 设置 ``ANDROID_HOME`` 环境变量，指向安装 Android SDK 的目录。

测试需要一台真实/虚拟安卓设备：
- 真实设备: 打开设置 -> 开发人员选项 -> USB 调试，使用 USB 线连接设备，在弹出授权界面中点击允许。
- Android Virtual Device. 在 Android Studio 欢迎页点击 More Actions → Virtual Device Manager，在其中新建一台虚拟设备，版本与之前安装的 SDK 对应即可。
若连接成功,在命令行输入 ``adb devices`` 时，将显示已连接的设备。

在Python安装客户端：

```bash
pip install Appium-Python-Client
```

运行时，先在命令行启动Server端：

```bash
appium
```

再在`` ./testing-android ``目录下运行 ``python hello_android.py`，观察到设备打开设置并点击电池选项，说明 Appium 运行正常。

### 4.3 Appium 基本用法

Appium 的用法与 Selenium 一脉相承。不同的是，移动测试环境的多样性和复杂性使得 Appium WebDriver 的初始化必须显式定义所需的 capabilities，例如：
`````python
from appium import webdriver

desired_caps = {
    "platformName": "Android", # 或 "iOS"
    "deviceName": "Your_Device_Name",
    "appPackage": "com.example.app",
    "appActivity": ".MainActivity",
}

driver = webdriver.Remote("http://localhost:4723", desired_caps)

`````

测试脚本中则与 Selenium 基本一致，通过一系列操作完成自动化测试，包括:
- 元素定位与交互：Appium 使用 find_element 方法结合 By 类来定位元素，但由于平台区别，支持的定位方式存在一定不同。具体来说，安卓系统下的 Appium 可通过以下方式进行元素定位：
  - ID (resource-id):使用元素的 resource-id 属性进行定位。语法：find_element(By.ID, 'resource_id')
  - Accessibility ID (content-desc):使用元素的 content-desc 属性进行定位，通常是用于辅助功能。语法：find_element(By.ACCESSIBILITY_ID, 'accessibility_id')
  - XPath:使用 XPath 表达式进行定位，可以非常灵活地定位元素。语法：find_element(By.XPATH, 'xpath_expression')
  - Class Name (class):使用元素的 class 属性进行定位。语法：find_element(By.CLASS_NAME, 'class_name')
  - Android UIAutomator:使用 Android UIAutomator 框架提供的定位策略。语法：find_element(By.ANDROID_UIAUTOMATOR, 'android UiSelector().text("Some Text")')
  - Android View Tag:使用元素的 tag 属性进行定位，不常用。语法：find_element(By.ANDROID_VIEW_TAG, 'tag')
  - Android Data Matcher:使用 Android DataMatcher 来匹配数据，不常用。语法：find_element(By.ANDROID_DATA_MATCHER, 'new UiSelector().description("Some Description")')
  - Android View Matcher:使用 Android ViewMatcher 来匹配视图，不常用。语法：find_element(By.ANDROID_VIEW_MATCHER, 'new UiSelector().description("Some Description")')
  - Android Widget:使用 Android Widget 来定位元素，不常用。语法：find_element(By.ANDROID_WIDGET, 'new UiSelector().description("Some Description")')
  - CSS Selector:使用 CSS 选择器进行定位，但通常在移动测试中使用较少。语法：find_element(By.CSS_SELECTOR, 'css_selector')
  一般来说，常用较为稳定且直接的 ID、Accessibility ID 和 XPath 进行定位。操作则包括:
  - 点击：通过 element.click() 可以对元素执行点击操作。
  - 输入文本：通过 element.sendKeys("text") 向输入框中输入文本。
  - 清除文本：通过 element.clear() 清除输入框中的内容。
  - 获取文本：通过 element.getText() 获取某个元素的显示文本。
- 手势操作：安卓设备支持多种手势操作，包括
  - 长按：通过 tap() 实现长按操作。
  - 滑动：使用 swipe() 实现从屏幕一端滑动到另一端的操作。
  - 拖拽：使用 drag_and_drop() 实现元素的拖拽操作。
  - 捏合（缩放）：通过 flick() 可以实现缩放操作（双指捏合或扩展）。
- 应用管理，包括应用安装、卸载、关闭、打开等。
- 设备信息获取。

完整的 API 信息可参考 [Appium-Python-Client](https://github.com/appium/python-client) 和 [Appium-UIautomator2-Driver](https://github.com/appium/appium-uiautomator2-driver) 文档。

Appium 也提供了快速查看 GUI 层级，包括其中各元素属性的工具 Appium Inspector。安装方式可参考 [Installation](https://appium.github.io/appium-inspector/latest/quickstart/installation/)。安装完成后，在应用首页配置 Appium Server 的地址(默认为 127.0.0.1/4723),在启动测试后即可通过 Attach to Session 选项连接到当前运行的会话，查看界面 GUI 结构，获取元素的 xpath 等属性。

### 4.4 实验内容

本实验测试对象为 TODO List 应用 [1List](https://f-droid.org/en/packages/com.lolo.io.onelist/). 

#### 4.4.1 功能性测试

对本应用的功能性测试应包括：
1. UI 元素交互测试
   1. 切换列表：验证点击不同列表时，列表内容是否正确切换。
   2. 添加列表：点击右上角的 + 按钮添加新列表，检查列表创建是否成功，并验证列表名输入框和保存按钮的正常工作。
   3. 编辑/删除列表：长按列表以检查是否能正确触发编辑或删除选项。
   4. 添加项目：在当前选中的列表内添加项目，确保项目被正确添加并在 UI 中显示。
   5. 删除项目：向左滑动项目进行删除操作，确保项目被删除并从 UI 中移除。
   6. 编辑项目：向右滑动项目并进行编辑，确保项目内容能够正确修改。
   7. 快速添加评论：输入待办事项时，点击评论按钮，验证能否快速添加评论并保存。
   8. 标记为完成：点击项目，检查其是否能正确标记为完成，并验证是否会改变显示样式（如打勾或灰色显示）。
2. 列表管理
   1. 导入列表：测试导入功能，确保能通过选择存储文件夹正确导入外部列表数据。
   2. 项目排序：测试拖拽操作能否按期望顺序移动列表或项目。
3. 设置测试
   1. 点击设置按钮（⚙️），检查是否能够正确进入设置页面。
   2. 验证设置页面中的各项功能是否生效，例如更改主题，备份等功能。

在 ``./testing-android/test_onelist_func.py`` 中已完成了切换、添加列表，添加/删除项目等测试用例，请完成：
1. 编辑/删除列表测试用例 ``edit_delete_list``。请先新建一个列表，再编辑其名称，之后删除它，用 assert 验证两个操作是否完成。
2. 编辑项目测试用例 ``test_edit_item``。请模仿辅助方法 ``add_item``, ``delete_item`` 的实现，首先完成 ``edit_item``，再在 ``test_edit_item`` 中调用该方法完成测试。
3. 完成查看版本信息测试用例 ``test_release_note``。请完成点击设置图标 → "show last release note" 选项的自动化脚本，测试查看当前版本的 release 信息功能是否正常。

完成测试用例后，使用本机的 Python 环境在`` ./testing-androoid ``目录下运行 ``python test_onelist_func.py``,或使用即可自动运行所有 ``test_`` 开头的测试用例。

#### 4.4.2 非功能性测试

安卓应用的非功能需求（Non-functional requirements, NFRs）是指影响用户体验、性能、系统稳定性、安全性等方面的要求。这类需求不会直接体现为功能，但对应用的整体质量有重要影响。对于本应用来说，应考虑的 NFRs 包括但不限于：
- 在不同平台、硬件、安卓版本下的**兼容性**；
- 在正常使用过程中**性能**正常，不出现长时间无响应或崩溃；
- 保证数据存储的**安全性**，确保未授权的第三方应用无法访问敏感数据；
- 用户引导是否足够详细、有效，UI设计是否符合用户操作习惯。

本节中，我们考虑对该应用进行性能测试。通过向应用中添加大量待办事项的方式，测试应用在大量数据下的性能表现。

关于获取性能指标的方式，Appium-UIautomator2-Driver 封装了 get_performance_data 方法，方便测试人员快速获取简单的性能指标，包括 CPU, 内存，网络等。本实验中，``./testing-android/test_onelist_perf.py `` 已经完成了添加待办事项和内存数据收集操作。
**任务：**请使用收集到的 csv 数据，利用 Python 的 [Matplotlib](https://matplotlib.org/) 库绘制各内存指标随时间变化的图像。找到有显著趋势特征的指标并列出。

上述指标往往不能满足复杂的性能测试需求，因此，安卓性能测试人员通常会使用 [Perfetto](https://perfetto.dev/)，[PerfDog](https://perfdog.qq.com/) 等专业性能测试和分析工具。Perfetto 是 Google 开发的一个开源的系统级性能分析工具。Android 系统提供了对 Perfetto 的原生支持，并提供了多种配置 trace 的方式，详情参考 [Quickstart: Record traces on Android](https://perfetto.dev/docs/quickstart/android-tracing)。

``./testing-android`` 目录中提供了 ``record_android_trace`` 脚本，可在 ``cd`` 进入通过``./testing-android`` 目录执行该脚本执行 trace.本次 trace 使用外置配置于 ``config.pbtx`` 的方式。config 文件可以在 [Perfetto UI](https://ui.perfetto.dev/#!/record) 中生成，本实验中已提供。在执行 ``test_onelist_perf.py `` 中请以如下方式启动 Perfetto：
- Windows：``python ./record_android_trace -o trace_file.perfetto-trace -c config.pbtx``
- Linux/Mac：
  `````bash
  chmod u+x record_android_trace
  ./record_android_trace -o trace_file.perfetto-trace -c config.pbtx
  `````

根据 config 的配置，数据收集将持续 30 秒，数据收集内容包括。``record_android_trace`` 将在收集完成后自动存储 trace 文件并打开 Perfetto UI 供测试人员分析性能数据。Perfetto UI 中应关注的信息包括：
- Time range selector: 顶部的时间轴用于选择和缩放你想查看的时间范围。你可以点击并拖动，放大或缩小特定时间段的视图。
- CPU Usage: 时间轴下方展示了所有 CPU 核心的使用情况，你可以看到哪些进程和线程正在占用 CPU 资源。
- 进程信息：显示每个进程各自信息。在此我们主要关心测试的应用 com.lolo.io.onelist，负责界面显示的 SurfaceFlinger。各线程中包括：
  - 帧渲染信息：Expected Timeline 显示了系统对帧渲染的预期时间，Actual Timeline 表示应用实际渲染每一帧的时间。关注红/橙色条，即帧渲染超过预期时间的时间段。
  - 线程活动: 展示应用内的各个线程，标注线程状态。主要关注主线程（Main Thread） 和 渲染线程（Render Thread），观察它们在关键渲染时刻是否有被其他线程阻塞。
  - 内存使用：查看内存分配和垃圾回收（HeapTaskDaemon 线程活动）.

请观察一段 com.lolo.io.onelist 主线程中的某一次交互后，帧渲染尤其卡顿的时间段。观察这段时间的各线程运行、CPU 调度、内存状况，观察是否存在资源争夺、内存不足或过多的后台任务的现象，并分析这段时间帧率下降的原因可能是什么？

## 1.5 思考题

请依据实验内容简要回答下列思考题：

- 在 `4.4.1` 的标记项目完成测试用例 ``test_mark_item_done`` 中， Appium 本身无法通过 UIAutomator2 获取文本的颜色、删除线等样式信息，此时该如何完成此测试用例？