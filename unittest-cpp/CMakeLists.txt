cmake_minimum_required(VERSION 3.14)
project(minishell-tests)

# Prefer NEW behavior for policy CMP0135 so extracted files get a fresh timestamp
# (avoids rebuild/robustness issues when FetchContent downloads archives)
if(POLICY CMP0135)
  cmake_policy(SET CMP0135 NEW)
endif()

# GoogleTest requires at least C++14
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)
FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/ff233bdd4cac0a0bf6e5cd45bda3406814cb2796.zip
  # Ensure extracted files get the current extraction timestamp to avoid
  # stale-file timestamp problems on some filesystems
  DOWNLOAD_EXTRACT_TIMESTAMP TRUE
)
# For Windows: Prevent overriding the parent project's compiler/linker settings
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

enable_testing()

# 定义 Minishell 测试可执行文件
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
