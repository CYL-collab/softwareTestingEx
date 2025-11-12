#ifndef MINISHELL_TEST_BASE_H
#define MINISHELL_TEST_BASE_H

#include <gtest/gtest.h>
#include <string>
#include <array>
#include <memory>
#include <stdexcept>
#include <cstdio>

class MinishellTestBase : public ::testing::Test {
protected:
    // Minishell 可执行文件路径（相对于测试可执行文件）
    std::string minishell_path = "../../source/minishell/minishell";
    
    /**
     * 执行命令并获取输出
     * @param command 要执行的命令
     * @return 命令的输出
     */
    std::string executeCommand(const std::string& command) {
        // 构建完整命令：通过 echo 将命令传入 minishell
        std::string full_command = "echo \"" + escapeQuotes(command) + "\" | " + minishell_path + " 2>&1";
        return execShellCommand(full_command);
    }
    
    /**
     * 执行命令并获取退出码
     * @param command 要执行的命令
     * @return 命令的退出码
     */
    int executeCommandGetExitCode(const std::string& command) {
        std::string full_command = "echo \"" + escapeQuotes(command) + "\" | " + 
                                  minishell_path + "; echo $?";
        std::string output = execShellCommand(full_command);
        
        // 解析最后一行获取退出码
        size_t last_newline = output.find_last_not_of("\n\r");
        if (last_newline == std::string::npos) {
            return -1;
        }
        
        output = output.substr(0, last_newline + 1);
        size_t prev_newline = output.find_last_of('\n');
        
        if (prev_newline != std::string::npos) {
            std::string exit_code_str = output.substr(prev_newline + 1);
            try {
                return std::stoi(exit_code_str);
            } catch (...) {
                return -1;
            }
        }
        
        return -1;
    }
    
    /**
     * 执行多个命令（用分号分隔）
     * @param commands 命令数组
     * @return 所有命令的组合输出
     */
    std::string executeCommands(const std::vector<std::string>& commands) {
        std::string combined;
        for (size_t i = 0; i < commands.size(); ++i) {
            if (i > 0) combined += "; ";
            combined += commands[i];
        }
        return executeCommand(combined);
    }
    
private:
    /**
     * 转义字符串中的引号
     */
    std::string escapeQuotes(const std::string& str) {
        std::string result;
        for (char c : str) {
            if (c == '"') {
                result += "\\\"";
            } else if (c == '\\') {
                result += "\\\\";
            } else {
                result += c;
            }
        }
        return result;
    }
    
    /**
     * 执行 shell 命令并获取输出
     */
    std::string execShellCommand(const std::string& cmd) {
        std::array<char, 256> buffer;
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
