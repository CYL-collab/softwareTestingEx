#include "minishell_test_base.h"
#include <gtest/gtest.h>
#include <fstream>
#include <cstdio>

// ========================================
// 基础管道测试
// ========================================

TEST_F(MinishellTestBase, SimplePipe) {
    std::string output = executeCommand("echo 'hello world' | cat");
    EXPECT_TRUE(output.find("hello world") != std::string::npos);
}

TEST_F(MinishellTestBase, PipeWithWc) {
    // 任务2: 测试管道与 wc 命令
    std::string output = executeCommand("echo 'one two three' | wc -w");

    // TODO: 测试管道与 wc 命令,验证输出包含数字 3
}

TEST_F(MinishellTestBase, MultiplePipes) {
    // 任务2: 测试多重管道，比如 echo 'test line' | cat | cat

}

// ========================================
// 管道与重定向组合测试
// ========================================

class PipeRedirectTest : public MinishellTestBase {
protected:
    std::string temp_file = "/tmp/minishell_pipe_output.txt";
    
    void SetUp() override {
        std::remove(temp_file.c_str());
    }
    
    void TearDown() override {
        std::remove(temp_file.c_str());
    }
    
    std::string readFile(const std::string& filename) {
        std::ifstream file(filename);
        if (!file.is_open()) return "";
        return std::string((std::istreambuf_iterator<char>(file)),
                          std::istreambuf_iterator<char>());
    }
};

TEST_F(PipeRedirectTest, PipeWithAppendRedirect) {
    // TODO: 测试管道与追加重定向
    executeCommand("echo 'line 1' | cat > " + temp_file);
    executeCommand("echo 'line 2' | cat >> " + temp_file);
    
    std::string content = readFile(temp_file);
    // 验证文件包含两行
}

TEST_F(PipeRedirectTest, InputRedirectWithPipe) {
    // TODO: 测试输入重定向后接管道
    // 例如: cat < input.txt | grep pattern
    std::string input_file = "/tmp/minishell_pipe_input.txt";
    std::ofstream out(input_file);
    out << "test content for pipe\n";
    out.close();
    
    std::string output = executeCommand("cat < " + input_file + " | cat");
    // 验证输出
    
    std::remove(input_file.c_str());
}

// ========================================
// 管道参数化测试（决策表）
// ========================================

struct PipeTestParam {
    std::string command;
    std::string expected_behavior;  // 期望的行为描述
    bool should_succeed;            // 是否应该成功
    std::string description;        // 测试描述
};

class PipeParameterizedTest : public MinishellTestBase,
                               public ::testing::WithParamInterface<PipeTestParam> {
};

TEST_P(PipeParameterizedTest, PipeVariousCombinations) {
    PipeTestParam param = GetParam();
    
    if (param.should_succeed) {
        std::string output = executeCommand(param.command);
        // TODO: 验证成功的情况
        // 可以检查输出非空，或包含特定内容
    } else {
        // TODO: 验证失败的情况
        // 可以检查退出码非0，或包含错误信息
        int exit_code = executeCommandGetExitCode(param.command);
        // EXPECT_NE(exit_code, 0) << "Command should have failed: " << param.command;
    }
}

// 任务5: 实现决策表中的测试用例
// 决策表:
// | 条件 | C1: 命令1有效 | C2: 命令2有效 | C3: 有重定向 | 预期结果 |
// |------|--------------|--------------|-------------|----------|
// | R1   | Y            | Y            | N           | 成功     |
// | R2   | Y            | Y            | Y           | 成功     |
// | R3   | Y            | N            | N           | 失败     |
// | R4   | N            | Y            | N           | 失败     |

INSTANTIATE_TEST_SUITE_P(
    PipeDecisionTable,
    PipeParameterizedTest,
    ::testing::Values(
        // TODO: 根据决策表添加测试参数
        // R1: 两个有效命令，无重定向
        PipeTestParam{
            "echo 'test' | cat",
            "Both commands valid, no redirect",
            true,
            "R1: Valid|Valid|No-redirect"
        },
        // R2: 两个有效命令，有重定向
        PipeTestParam{
            "echo 'test' | cat > /tmp/test_pipe_r2.txt",
            "Both commands valid, with redirect",
            true,
            "R2: Valid|Valid|Redirect"
        }
        // TODO: 添加 R3, R4
        // R3: 第一个命令有效，第二个无效
        // 例如: "echo 'test' | invalidcommand123"
        
        // R4: 第一个命令无效，第二个有效
        // 例如: "invalidcommand123 | cat"
    )
);

// ========================================
// 边界值测试
// ========================================

TEST_F(MinishellTestBase, EmptyPipeLeft) {
    // 任务6: 测试管道左侧为空
    std::string output = executeCommand(" | cat");
    
    // TODO: 验证行为（可能是错误或空输出）
}

TEST_F(MinishellTestBase, EmptyPipeRight) {
    // 任务7: 测试管道右侧为空
    std::string output = executeCommand("echo 'test' | ");
    
    // TODO: 验证行为（应该产生错误）
}

TEST_F(MinishellTestBase, PipeWithOnlySpaces) {
    // TODO: 测试管道两侧只有空格
    std::string output = executeCommand("   |   ");
    // 应该产生错误
}

TEST_F(MinishellTestBase, PipeWithBuiltinCommands) {
    // TODO: 测试管道与内置命令的组合
    // 例如: echo "test" | pwd （pwd 不应该受影响）
}

// ========================================
// 错误处理测试
// ========================================

TEST_F(MinishellTestBase, PipeWithNonExecutableCommand) {
    // TODO: 测试管道下游有不可执行的命令
    std::string output = executeCommand("echo 'test' | /tmp/nonexistent_exe");
    // echo 输出会被丢弃
}

TEST_F(MinishellTestBase, PipeBreaksOnFirstFailure) {
    // TODO: 测试管道中有不可执行的命令，但下游存在有效命令
    std::string output = executeCommand("/tmp/nonexistent_exe | echo 'test'");
    // echo 正常打印到终端
}

// ========================================
// 主函数
// ========================================

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
