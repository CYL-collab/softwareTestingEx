# 软件测试实验指导书
## 0 提交说明
本实验最终提交物为单个实验报告，请参考 `.\实验报告.md` 中要求撰写并提交。提交要求仅包含一个 PDF 格式的文件。

提交截止时间： **2024-12-22（校历第 16 周周日） 23:59:59**
提交地址： https://send2me.cn/y7bw80pA/Rd-n_iZhow4Uqg

## 1 C++ 单元测试
### 1.1 实验目的

利用 C++ 单元测试框架 googletest 的特性，提高单元测试编写和执行效率。

### 1.2 环境配置

本实验的所有操作均可以在 vim，或记事本内完成。当然，由于现代代码编辑器提供了代码补全，调试支持，插件等一系列强大功能，我们在此推荐使用 [VSCode](https://code.visualstudio.com/) 以支持你在本实验的代码编写。为此，推荐在 VSCode 主侧栏的扩展商店中安装如下插件：

- C/C++ Extension Pack
- Extension Pack for Java
- Python Extension Pack

然后，为了正确编译并使用 gtest 测试 C++ 代码，你将需要：
- 支持 C++14 及以上的 C++ 编译器
- 构建工具 CMake 和 Make

具体过程可参考 [GoogleTest官方文档](https://google.github.io/googletest/quickstart-cmake.html)。以下是各平台的推荐配置。

对于 **Windows** 平台：
- 推荐编译器为微软开发的 MSVC，通过下载 [Visual Studio 生成工具](https://aka.ms/vs/17/release/vs_BuildTools.exe)，并在其中勾选使用C++的桌面开发，安装。
- 构建工具可在 [CMake](https://cmake.org/download/) 和 [Make](https://gnuwin32.sourceforge.net/packages/make.htm) 官网安装。
  更推荐的方法是使用包管理器（比如[WinGet](https://github.com/microsoft/winget-cli), [Scoop](https://scoop.sh/) 和 [Chocolatey](https://chocolatey.org/install) ）一键安装。以 Scoop 为例，在 Powershell 中安装 Scoop：
    ````` powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
    `````
    然后通过Scoop安装所需构建工具：
    ````` powershell
    scoop install cmake make
    `````

对于 **Linux** 平台，编译器使用 gcc/clang 均可。通过包管理器安装。以 Debian/Ubuntu 为例：
````` shell
sudo apt install gcc g++ cmake make
`````

对于 **Mac** 平台，我们同样推荐使用包管理器 [Homebrew](https://brew.sh/) 配置环境。在 Mac 终端内输入
````` shell
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
`````
以安装 Homebrew。随后安装所需软件：
````` shell
brew install gcc g++ cmake make
`````

为验证构建工具已正确安装，在终端输入
````` shell
cmake --version
make --version
`````
若正确显示版本信息，表示工具已经安装并准备好使用。

此时即可在项目中配置 gtest。新建一个 ``my_project`` 文件夹并进入:
````` shell
mkdir my_project && cd my_project
`````
在其中新建一个 ``hello_test.cc``，内容为：
`````C++
#include <gtest/gtest.h>

TEST(HelloTest, BasicAssertions) {
  // Expect two strings not to be equal.
  EXPECT_STRNE("hello", "world");
  // Expect equality.
  EXPECT_EQ(7 * 6, 42);
}
`````

另新建一个 ``CMakeLists.txt`` ，使用 [FetchContent](https://cmake.org/cmake/help/latest/module/FetchContent.html) 声明对 GoogleTest 的依赖，并声明要构建的 C++ 测试二进制文件:
````` shell
cmake_minimum_required(VERSION 3.14)
project(unittest-cpp)

# GoogleTest requires at least C++14
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)
FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/ff233bdd4cac0a0bf6e5cd45bda3406814cb2796.zip
)
# For Windows: Prevent overriding the parent project's compiler/linker settings
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

enable_testing()

# Define test executable name and source file
set(TEST_EXECUTABLE_NAME hello_test)
set(TEST_SOURCE_FILE hello_test.cc)

add_executable(${TEST_EXECUTABLE_NAME} ${TEST_SOURCE_FILE})
target_link_libraries(${TEST_EXECUTABLE_NAME} GTest::gtest_main)

include(GoogleTest)
gtest_discover_tests(${TEST_EXECUTABLE_NAME})
`````

构建并运行测试：
````` bash
my_project$ cmake -S . -B build
-- The C compiler identification is GNU 10.2.1
-- The CXX compiler identification is GNU 10.2.1
...
-- Build files have been written to: .../my_project/build

my_project$ cmake --build build
Scanning dependencies of target gtest
...
[100%] Built target gmock_main

my_project$ cd build && ctest
Test project .../my_project/build
    Start 1: HelloTest.BasicAssertions
1/1 Test #1: HelloTest.BasicAssertions ........   Passed    0.00 sec

100% tests passed, 0 tests failed out of 1

Total Test time (real) =   0.01 sec
`````

### 1.3 GoogleTest语法介绍

在GoogleTest中，定义了多种宏来编写测试。其中常用的包括：
#### TEST
`````C++
TEST(TestSuiteName, TestName) {
  ... statements ...
}
`````
在测试套件``TestSuiteName``中定义一个名为``TestName``的测试。
#### TEST_F 
`````C++
TEST_F(TestFixtureName, TestName) {
  ... statements ...
}
`````
定义一个名为``TestName``的测试，使用测试夹具类 ``TestFixtureName``。在测试的时候，我们经常遇到一个对象需要初始化，测试完可能还需要清理的情况，使用测试夹具可以批量完成此类操作。

使用 TEST_F 能够复用夹具中定义的代码，使得测试更加模块化，并减少了重复代码。
#### TEST_P
`````C++
TEST_P(TestFixtureName, TestName) {
  ... statements ...
}
`````
定义一个名为``TestName``的值参数化测试，使用测试夹具类 ``TestFixtureName``。测试套件名称为 ``TestFixtureName``。 

使用 TEST_P 能够实现值参数化测试，即在一个测试下对不同参数值进行测试。这可以有效减少重复代码，提高测试覆盖率。

#### INSTANTIATE_TEST_SUITE_P
`````C++
INSTANTIATE_TEST_SUITE_P(InstantiationName,TestSuiteName,param_generator)
INSTANTIATE_TEST_SUITE_P(InstantiationName,TestSuiteName,param_generator,name_generator)
`````
实例化TEST_P定义的值参数化测试套件 ``TestSuiteName``。

#### TYPED_TEST_SUITE
`````C++
TYPED_TEST_SUITE(TestFixtureName,Types) TYPED_TEST_SUITE(TestFixtureName,Types,NameGenerator)
`````
定义一个基于测试夹具 ``TestFixtureName`` 的类型参数化测试套件。使用参数 ``Types`` 表示要运行测试的数据类型列表。

#### TYPED_TEST
`````C++
TYPED_TEST(TestSuiteName, TestName) {
  ... statements ...
}
`````
在类型参数化测试套件中定义一个具体的测试用例。在测试体内部，可以使用特殊名称 ``TypeParam`` 来引用类型参数，使用 ``TestFixture`` 来引用测试夹具类。

更多测试用宏的资料可参考[官方文档](https://google.github.io/googletest/reference/testing.html)。 

断言(Assertion)是单元测试中不可缺少的重要部分。在GoogleTest中，定义了多种断言宏：

- 基本断言：如 EXPECT_TRUE、EXPECT_FALSE、ASSERT_TRUE 和 ASSERT_FALSE，用于检查测试中的条件。
- 二元比较断言：比较两个值，包括 EXPECT_EQ、EXPECT_NE 等及其 ASSERT_ 对应形式。
- 字符串比较断言：专门用于比较 C 字符串，包括 EXPECT_STREQ 和 EXPECT_STRCASEEQ 等。
- 浮点数比较断言：如 EXPECT_FLOAT_EQ 和 EXPECT_NEAR，处理浮点数的精度问题。
- 异常断言：检查预期的异常，如 EXPECT_THROW 和 EXPECT_NO_THROW。
- 谓词断言：允许复杂逻辑检查，包括 EXPECT_PRED1、EXPECT_PRED2 等。

每一类断言又分为两种：
- **EXPECT断言**：在条件不满足时记录断言失败，但不终止当前测试用例。
- **ASSERT断言**：在条件不满足时终止当前测试用例，不再执行后续的代码。

更多断言宏相关资料可参考[官方文档](https://google.github.io/googletest/reference/assertions.html)。 

## 1.4 实验内容

本部分将通过数个例子，利用 googletest 功能进行单元测试实践。

### 1.4.1 创建第一个单元测试

在本节中，我们对一个计算器类进行测试，它提供了四个基本的数学运算方法：加法、减法、乘法和除法。实验预先提供了计算器类的实现 ``Calculator.h``，并在 ``calculator_test.cc`` 设置了测试夹具,提供了测试用例示例:
`````C++
TEST_F(CalculatorTest, AddsTwoNumbers) {
    EXPECT_EQ(5, calc.add(2, 3));
}
`````

本部分的任务如下：
1. 在指定位置仿照示例完成 SubtractsTwoNumbers, MultipliesTwoNumbers, DividesTwoNumbers 的测试用例。（提示：由于 DividesTwoNumbers 涉及浮点运算，直接比较浮点数可能会因为极小的精度误差而导致测试失败，可考虑使用 [EXPECT_NEAR(val1,val2,abs_error)](https://google.github.io/googletest/reference/assertions.html#floating-point) 而不是 EXPECT_EQ 断言）。
2. 请在指定位置构建DivisionByZeroThrows测试用例，验证除以0是能否触发异常。在其中使用 EXPECT_THROW(statement,exception_type) 断言。由 ``Calculator.h`` 可知，除以0触发的异常类型为 ``std::invalid_argument``。

完成后，修改 ``CMakeLists.txt``，把 ``TEST_SOURCE_FILE`` 变量修改成 ``calculator_test.cc``，然后在 ``./unittest-cpp`` 目录下编译并运行测试：
`````bash
cmake --build build
cd build && ctest
`````
测试结果显示
`````bash
Test project /your/path
      Start  1: CalculatorTest.AddsTwoNumbers
 x/xx Test  #1: CalculatorTest.AddsTwoNumbers ............   Passed    0.05 sec
      Start  2: CalculatorTest.SubtractsTwoNumbers
 ...

100% tests passed, x tests failed out of x

Total Test time (real) =   0.xx sec
`````

### 1.4.2 值参数化测试

如 1.3 中所述，值参数化测试可以组织一组不同的测试数据，对其调用相同的测试方法进行测试。GoogleTest的官方文档详细阐述了如何使用 [值参数化测试](https://google.github.io/googletest/advanced.html#value-parameterized-tests)：
1. 定义测试夹具类。以 FooTest 为例：
    `````C++
    class FooTest :
        public testing::TestWithParam<absl::string_view> {
            // 部署测试夹具
    };
    `````
2. 使用 TEST_P 定义所需的测试用例。
   `````C++
   TEST_P(FooTest, DoesBlah) {
      // 使用 GetParam() 方法获取参数
      EXPECT_TRUE(foo.Blah(GetParam()));
      ...
    }

    TEST_P(FooTest, HasBlahBlah) {
      ...
    }
   `````
3. 使用 INSTANTIATE_TEST_SUITE_P 使用所需参数集来实例化测试套件。
   `````C++
   INSTANTIATE_TEST_SUITE_P(Default,
                              FooTest,
                              testing::Values("meeny", "miny", "moe"));
   `````

本部分的任务是，在指定位置完成 ``CanAddNumbers`` 用例的编写：
- 定义一个新的测试夹具 ``CalculatorParamTest`` ，使用 ``TestWithParam<int>`` 作为基类代替 ``Test``。
- 使用 TEST_P 定义 ``CanAddNumbers`` 用例，使用 ``GetParam()`` 调用一个参数，再加上一个常数，以测试 ``add`` 方法，并使用 EXPECT_EQ 作为断言。
- 使用 INSTANTIATE_TEST_SUITE_P(InstantiationName,TestSuiteName,param_generator) 实例化该测试套件，使用五个参数[1,2,3,4,5]。

在 ``./unittest-cpp`` 目录下编译并运行测试，观察结果。

### 1.4.3 在值参数化测试中考虑组合

在复杂软件系统中，经常会出现这样的现象:软件被安装在一个新的位置或者被不同用户使用后，出现了一组原本不存在的新错误。这是由于，这些变化导致了一组不同的输入，其中一些输入组合触发了故障。gtest 在参数化测试中引入了 ``Combine()`` 方法，将 n 个输入通过笛卡尔积的方式组合成 n 元组进行测试。

本部分的任务是，在指定位置完成 ``AddCombination`` 用例的编写。可参考官方文档 [参数化测试](https://google.github.io/googletest/advanced.html#value-parameterized-tests)：

- 定义一个新的测试夹具 ``CalculatorCombinedTest`` ，使用 ``TestWithParam`` 作为基类。注意此处的参数应当是两个 int 组成的 tuple。
- 使用 TEST_P 定义 ``AddCombination`` 用例，使用 ``GetParam()`` 调用两个参数，以测试 ``add`` 方法，并使用 EXPECT_EQ 作为断言。
- 使用 INSTANTIATE_TEST_SUITE_P(InstantiationName,TestSuiteName,param_generator) 实例化该测试套件，使用 Combine 组合两个 Values 参数集，参数任选。 

在 ``./unittest-cpp`` 目录下编译并运行测试，观察结果。

### 1.4.4 类型参数化测试

[类型参数化测试](https://google.github.io/googletest/advanced.html#type-parameterized-tests) 可以在同一段测试代码中，使用不同数据类型进行测试,不必为每个数据类型单独编写测试逻辑。我们现在的计算器实现 ``Calculator.h`` 只能接受 ``int`` 作为输入，因此，你需要：
- (已完成)扩展计算器实现使其支持 ``double`` 和 ``float``。为此，在 ``UniversalCalculator.h`` 中进行[模板声明](https://learn.microsoft.com/en-us/cpp/cpp/templates-cpp) ``template <typename T>`` 并将四个基本的数学运算方法均改写为模板函数（e.g., ``T add(T a, T b)``）。
- 创建一个新的测试文件 ``universalCalculator_test.cc``，并在其中：
  - 定义一个类型参数化的测试套件 ``CalculatorTest``:
    `````C++
    template <typename T>
    class CalculatorTest : public ::testing::Test {};
    `````
  - 定义类型列表 ``MyTypes``，其中包含了我们要测试的类型（包括 ``int``, ``float``, ``double``）。
    `````C++
    using MyTypes = ::testing::Types<int, float, double>;
    `````
  - 使用 ``TYPED_TEST_SUITE(CalculatorTest, MyTypes)`` 绑定测试类和类型列表。
  - 使用``TYPED_TEST(CalculatorTest, AddTest)`` 编写测试逻辑。注意使用 ``TypeParam`` 引用类型参数(``UniversalCalculator<TypeParam> calc``)，以实例化计算器类并定义两个常数为输入参数。使用 EXPECT_EQ 测试一组用例即可。

在 ``./unittest-cpp`` 目录下编译并运行测试，观察结果。

## 1.5 思考题

请依据实验内容简要回答下列思考题：

1. 除了 `1.4.1` 中使用的EXCEPT 断言，还有什么场景更适合使用 ASSERT 断言？
2. 在 `1.4.3` 所述的值参数化测试中，如果输入参数的全排列面临组合爆炸问题，你有什么策略减少测试用例数量？
3. 在 `1.4.4` 所述类型参数化测试中，如何处理类型之间行为的差异？

## 2 Java 单元测试
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