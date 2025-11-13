#include "minishell_test_base.h"
#include <gtest/gtest.h>
#include <fstream>
#include <cstdio>
#include <string>

// ========================================
// 重定向测试类
// ========================================

class RedirectTest : public MinishellTestBase {
protected:
    std::string temp_file = "/tmp/minishell_test_output.txt";
    std::string input_file = "/tmp/minishell_test_input.txt";
    std::string append_file = "/tmp/minishell_test_append.txt";
    
    void SetUp() override {
        // 清理可能存在的测试文件
        std::remove(temp_file.c_str());
        std::remove(input_file.c_str());
        std::remove(append_file.c_str());
    }
    
    void TearDown() override {
        // 清理测试文件
        std::remove(temp_file.c_str());
        std::remove(input_file.c_str());
        std::remove(append_file.c_str());
    }
    
    // 读取文件内容
    std::string readFile(const std::string& filename) {
        std::ifstream file(filename);
        if (!file.is_open()) {
            return "";
        }
        std::string content((std::istreambuf_iterator<char>(file)),
                           std::istreambuf_iterator<char>());
        return content;
    }
    
    // 写入文件内容
    void writeFile(const std::string& filename, const std::string& content) {
        std::ofstream file(filename);
        file << content;
    }
    
    // 检查文件是否存在
    bool fileExists(const std::string& filename) {
        std::ifstream file(filename);
        return file.good();
    }
};

// ========================================
// 使用 Combine() 创建组合测试
// ========================================

// 参数结构，用于 Combine() 测试
class CombineRedirectTest : public RedirectTest,
                            public ::testing::WithParamInterface<std::tuple<std::string, std::string>> {
};

TEST_P(CombineRedirectTest, CombineRedirectTest) {
    std::string command = std::get<0>(GetParam());
    std::string redirect_op = std::get<1>(GetParam());
    
    // 如果是追加操作，先写入一些初始内容
    if (redirect_op == ">>") {
        executeCommand("echo 'initial' > " + temp_file);
    }
    
    // 构建完整命令
    std::string full_command = command + " " + redirect_op + " " + temp_file;
    executeCommand(full_command);
    
    // 读取文件内容
    std::string content = readFile(temp_file);
    
    // 验证文件被创建
    EXPECT_TRUE(fileExists(temp_file));

    // TODO: 根据不同的命令和重定向操作，验证文件内容是否符合预期
    if (command.find("echo") != std::string::npos) {
        EXPECT_NE(content.find("test"), std::string::npos);
    } 

}

// 任务: 使用 Combine() 创建笛卡尔积组合测试
// Combine() 可以组合多个参数生成器，生成所有可能的组合
// 例如: 3个命令 × 2个操作符 = 6个测试用例
INSTANTIATE_TEST_SUITE_P(
    CombineRedirectCombinations,
    CombineRedirectTest,
    ::testing::Combine(
        // TODO: 补充不同的命令（pwd，env等）
        ::testing::Values(
            "echo 'test1'"
        ),
        // 第二维: 不同的重定向操作符（2个）
        // 3个命令 × 2个操作符 = 6个组合测试用例
        ::testing::Values(">", ">>")
    )
);

// ========================================
// 主函数
// ========================================

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
