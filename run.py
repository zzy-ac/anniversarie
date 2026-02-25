from datetime import datetime
import re
import logging
import argparse
import sys

# ----------------------------
# 日志配置
# ----------------------------
def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('anniversaries_log.txt', mode='a', encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = setup_logging()

# ----------------------------
# 数据文件
# ----------------------------
DATA_FILE = 'anniversaries_data.txt'

# ----------------------------
# 读取保存的纪念日
# ----------------------------
def load_anniversariess():
    anniversariess = {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '|' in line:
                    name, date_str = line.split('|', 1)
                    anniversariess[name.strip()] = date_str.strip()
    except FileNotFoundError:
        pass
    return anniversariess

# ----------------------------
# 保存纪念日
# ----------------------------
def save_anniversariess(anniversariess):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            for name, date_str in anniversariess.items():
                f.write(f"{name}|{date_str}\n")
        logger.info(f"已保存 {len(anniversariess)} 个纪念日")
    except Exception as e:
        logger.error(f"保存失败: {e}")

# ----------------------------
# 解析日期
# ----------------------------
def parse_date_input(date_str):
    date_str = date_str.strip()
    match = re.match(r'(\d{4})[年\-/.] *(\d{1,2})[月\-/.] *(\d{1,2})', date_str)
    if not match:
        raise ValueError("格式错误！支持：xxx年yy月zz日 | xxxx-yy-zz | xxxx/yy/zz | xxxx.yy.zz")
    year, month, day = map(int, match.groups())
    return datetime(year, month, day).date()

# ----------------------------
# 核心功能函数（复用）
# ----------------------------
def add_anniversaries(name, date_input):
    try:
        target_date = parse_date_input(date_input)
        date_str = target_date.strftime('%Y-%m-%d')
        anniversariess = load_anniversariess()
        anniversariess[name] = date_str
        save_anniversariess(anniversariess)
        print(f"已成功添加：{name} ({date_str})")
    except ValueError as e:
        print(f"日期格式错误：{e}")

def query_anniversaries(name):
    if name is None:
        print("未指定纪念日。")
        return
    anniversariess = load_anniversariess()
    if name not in anniversariess:
        print(f"未找到纪念日：{name}")
        return

    date_str = anniversariess[name]
    target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    today = datetime.now().date()

    if today >= target_date:
        days_past = (today - target_date).days
        print(f"\n【{name}】已过去 {days_past} 天")
    else:
        print(f"\n【{name}】尚未开始")

    next_year = today.year + (1 if target_date.replace(year=today.year) < today else 0)
    next_target = target_date.replace(year=next_year)
    days_left = (next_target - today).days
    print(f"下一个 {target_date.strftime('%m月%d日')} 还剩 {days_left} 天")

def delete_anniversaries(name):
    anniversariess = load_anniversariess()
    if name not in anniversariess:
        print(f"未找到纪念日：{name}")
        return
    del anniversariess[name]
    save_anniversariess(anniversariess)
    print(f"已删除：{name}")

# ----------------------------
# 交互式选择流程（复用）
# ----------------------------
def select_and_query():
    anniversariess = load_anniversariess()
    if not anniversariess:
        print("暂无已保存的纪念日。")
        return

    print("\n已保存的纪念日：")
    names = list(anniversariess.keys())
    for i, n in enumerate(names, 1):
        print(f"  {i}. {n}")

    try:
        idx = input("\n请选择要查询的纪念日序号 (1, 2, ...): ").strip()
        if not idx:
            print("输入不能为空。")
            return
        idx = int(idx)
        if 1 <= idx <= len(names):
            name = names[idx - 1]
            query_anniversaries(name)
        else:
            print("无效序号。")
    except (ValueError, IndexError):
        print("输入无效。")

def select_and_query_delete():
    anniversariess = load_anniversariess()
    if not anniversariess:
        print("暂无纪念日可删除。")
        return

    print("\n已保存的纪念日：")
    names = list(anniversariess.keys())
    for i, n in enumerate(names, 1):
        print(f"  {i}. {n}")

    try:
        idx = input("\n请输入要删除的纪念日序号: ").strip()
        if not idx:
            print("输入不能为空。")
            return
        idx = int(idx)
        if 1 <= idx <= len(names):
            name = names[idx - 1]
            delete_anniversaries(name)
        else:
            print("无效序号。")
    except (ValueError, IndexError):
        print("输入无效。")

# ----------------------------
# 命令行模式
# ----------------------------
def command_mode(args):
    # ----------------------------
    # 新建纪念日
    # ----------------------------
    if args.add:
        name, date_input = args.add
        name = name.strip()
        if not name:
            print("错误：纪念日名称不能为空。")
            sys.exit(1)
        add_anniversaries(name, date_input)
        return

    # ----------------------------
    # 查询纪念日（进入交互选择）
    # ----------------------------
    if args.query:
        select_and_query()
        return

    # ----------------------------
    # 删除纪念日（强制进入序号选择）
    # ----------------------------
    if args.delete:
        select_and_query_delete()
        return

# ----------------------------
# 交互式主菜单（保持不变）
# ----------------------------
def interactive_mode():
    print("=== 纪念日管理工具 ===")
    print("支持格式：xxxx年yy月zz日 | xxxx-yy-zz | xxxx/yy/zz | xxxx.yy.zz")

    while True:
        print("\n请选择操作：")
        print("1. 新建纪念日")
        print("2. 查询纪念日")
        print("3. 删除纪念日")
        print("4. 退出")
        choice = input("请输入选项 (1/2/3/4, 回车默认1): ").strip().lower()

        if not choice or choice in ('1', 'y', 'yes'):
            name = input("纪念日名称: ").strip()
            if not name:
                print("名称不能为空。")
                continue
            date_input = input(f"【{name}】的日期: ").strip()
            add_anniversaries(name, date_input)
            return

        elif choice in ('2', 'query'):
            select_and_query()
            return

        elif choice in ('3', 'delete'):
            select_and_query_delete()
            return

        elif choice in ('4', 'exit', 'quit'):
            print("感谢使用纪念日管理工具，再见！")
            return

        else:
            print("无效选项，请输入 1、2、3 或 4。")

# ----------------------------
# 主函数
# ----------------------------
def main():
    parser = argparse.ArgumentParser(
        description="纪念日管理工具（运行一次后退出）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  python anniversaries.py --add "结婚纪念日" "2024-12-25"
  python anniversaries.py --query          # 进入交互式选择（列出序号）
  python anniversaries.py --delete         # 进入交互式选择（列出序号）
  python anniversaries.py  # 交互式模式（不带参数）
        """
    )
    parser.add_argument('-a', '--add', nargs=2, metavar=('名称', '日期'), help="新建纪念日")
    parser.add_argument('-q', '--query', action='store_true', help="查询纪念日（进入交互式选择）")
    parser.add_argument('-d', '--delete', action='store_true', help="删除纪念日（进入交互式选择）")

    args = parser.parse_args()

    if any(vars(args).values()):
        command_mode(args)
    else:
        interactive_mode()

    print("\n纪念日管理完成，程序退出。")

# ----------------------------
# 入口点
# ----------------------------
if __name__ == "__main__":
    main()
