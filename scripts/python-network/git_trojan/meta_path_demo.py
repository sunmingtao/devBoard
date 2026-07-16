import sys
from importlib.abc import MetaPathFinder, Loader
from importlib.machinery import ModuleSpec

# 1. 定义一个符合 3.12 规范的加载器（必须继承 Loader）
class Python312Loader(Loader):
    def __init__(self, code_string):
        self.code_string = code_string

    def exec_module(self, module):
        # 继承 Loader 后，Python 会自动创建空白模块并传给这里
        # 我们只需要负责把代码执行进模块的字典（命名空间）中
        exec(self.code_string, module.__dict__)

# 2. 定义一个查找器（必须继承 MetaPathFinder）
class Python312Finder(MetaPathFinder):
    def __init__(self, module_name, code_string):
        self.module_name = module_name
        self.code_string = code_string

    def find_spec(self, fullname, path=None, target=None):
        if fullname == self.module_name:
            # 创建并返回一个 ModuleSpec，指定模块名和对应的 Loader 实例
            return ModuleSpec(fullname, Python312Loader(self.code_string))
        return None

# --- 🎯 运行测试 ---
virtual_code = """
def greet(name):
    return f"Hello, {name}! 3.12 Import pipeline fully customized."
"""

# 注册查找到 sys.meta_path
sys.meta_path.append(Python312Finder("my_dynamic_module", virtual_code))

# 导入并运行
import my_dynamic_module
print(my_dynamic_module.greet("Jacky"))
