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
    // 任务1: 测试管道与 wc 命令
    std::string output = executeCommand("echo 'one two three' | wc -w");

    // TODO: 测试管道与 wc 命令,验证输出包含数字 3
}

TEST_F(MinishellTestBase, MultiplePipes) {
    // 任务2: 测试多重管道，比如 echo 'test line' | cat | cat

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
        // 可以检查是否包含错误信息
        
    }
}

// 任务3: 实现决策表中的测试用例
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
        
        
        // R4: 第一个命令无效，第二个有效
        
    )
);

// ========================================
// 主函数
// ========================================

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
