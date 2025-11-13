import unittest
from parameterized import parameterized
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
import time

class ShoppingSystemTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """在所有测试开始之前只运行一次，设置全局的 WebDriver"""
        cls.driver = webdriver.Edge()  # 可以替换为其他驱动，如Firefox等
        cls.driver.maximize_window()
        cls.driver.implicitly_wait(5)  # 隐式等待，避免页面加载问题

    def setUp(self):
        """每个测试前执行，打开购物网站主页"""
        self.driver.get("https://www.saucedemo.com/")
    
    def login(self, username, password):
        """封装登录功能，供多个测试使用"""
        self.driver.find_element(By.ID, 'user-name').send_keys(username)
        self.driver.find_element(By.ID, 'password').send_keys(password)
        self.driver.find_element(By.ID, 'login-button').click()
        
    def reset_state(self):
        """重置测试状态，确保每个测试之间的独立性"""
        self.driver.get("https://www.saucedemo.com/inventory.html")
        self.driver.find_element(By.ID, 'react-burger-menu-btn').click()
        reset_link = self.driver.find_element(By.ID, 'reset_sidebar_link')
        reset_link.click()
        
    def add_to_cart(self, button_id):
        """封装添加商品到购物车功能，供多个测试使用"""
        add_to_cart_button = self.driver.find_element(By.ID, button_id)
        add_to_cart_button.click()

    # ---------------------- 登录功能测试 ----------------------
    def test_login_success(self):
        """测试输入正确的用户名和密码能否成功登录"""
        self.login("standard_user", "secret_sauce")
        time.sleep(2)  # 等待页面加载
        # 验证是否成功跳转到商品显示页面
        self.assertIn('https://www.saucedemo.com/inventory.html', self.driver.current_url)

    def test_login_wrong(self):
        """测试输入错误的用户名或密码时是否显示相应错误提示"""
        # TODO: 请补充完整测试代码
        
    def test_login_locked(self):
        """测试输入被锁定的用户时是否显示相应错误提示"""
        self.login("locked_out_user", "secret_sauce")
        # TODO: 请补充完整测试代码

    # ---------------------- 购物车功能测试 ----------------------
    @parameterized.expand([
        ("Sauce Labs Backpack", "add-to-cart-sauce-labs-backpack"),
        ("Sauce Labs Bike Light", "add-to-cart-sauce-labs-bike-light"),
        ("Sauce Labs Bolt T-Shirt", "add-to-cart-sauce-labs-bolt-t-shirt"),
        ("Sauce Labs Fleece Jacket", "add-to-cart-sauce-labs-fleece-jacket"),
        ("Sauce Labs Onesie", "add-to-cart-sauce-labs-onesie"),
        ("Test.allTheThings() T-Shirt (Red)", "add-to-cart-test.allthethings()-t-shirt-(red)")
    ])
    def test_add_to_cart(self, item_name, button_id):
        """测试添加商品到购物车功能"""
        # TODO: 请补充完整测试代码

    def test_remove_from_cart(self):
        """测试是否能够删除购物车中的商品"""
        self.login("standard_user", "secret_sauce")
        self.reset_state()
        self.add_to_cart("add-to-cart-sauce-labs-backpack")
        self.driver.get("https://www.saucedemo.com/cart.html")
        cart_item = self.driver.find_element(By.CLASS_NAME, 'cart_item')
        # 删除购物车中的商品
        remove_button = cart_item.find_element(By.ID, 'remove-sauce-labs-backpack')
        remove_button.click()
        # 验证购物车中商品是否被移除
        try:
            # 尝试查找元素 cart_item
            cart_item = self.driver.find_element(By.CLASS_NAME, 'cart_item')

            # 如果找到元素，等待其从 DOM 中消失
            WebDriverWait(self.driver, 10).until(EC.staleness_of(cart_item))
            print("Item successfully removed from the cart.")
        except NoSuchElementException:
            # 如果一开始元素就不存在，直接通过
            print("Item is not present in the cart, no need to remove.")
        except TimeoutException:
            # 如果等待超时，说明元素没有成功被移除，测试失败
            self.fail("The item was not removed from the cart.")

    # ---------------------- 结算和支付功能测试 ----------------------
    def test_checkout_and_payment(self):
        """测试填写收货信息和确认订单的结算功能"""
        # TODO: 请补充完整测试代码

    @classmethod
    def tearDownClass(cls):
        """测试结束后关闭浏览器"""
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()