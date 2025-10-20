# .github/scripts/sync_images.py

import os
import sys
import subprocess
from pathlib import Path

def run_command(command: list[str]) -> bool:
    """执行一个 shell 命令并返回其是否成功。"""
    try:
        # 使用 subprocess.run 执行命令，并捕获输出
        # check=True 会在命令返回非零退出码时抛出 CalledProcessError
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        # 打印标准输出，便于在 Actions 日志中查看
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        # 如果命令失败，打印错误信息
        print(f"❌ 命令执行失败: {' '.join(command)}", file=sys.stderr)
        print(f"   错误码: {e.returncode}", file=sys.stderr)
        print(f"   标准输出: {e.stdout}", file=sys.stderr)
        print(f"   标准错误: {e.stderr}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print(f"❌ 命令未找到: {command[0]}。请确保 Docker 已安装并位于 PATH 中。", file=sys.stderr)
        return False


def main():
    """主处理函数"""
    # --- 1. 从环境变量获取配置 ---
    source_dir_str = os.getenv("SOURCE_DIR", "this is what i want")
    output_dir_str = os.getenv("OUTPUT_DIR", "got it")
    private_registry = os.getenv("PRIVATE_REGISTRY")
    private_registry_namespace = os.getenv("PRIVATE_REGISTRY_NAMESPACE")

    if not private_registry or not private_registry_namespace:
        print("❌ 错误: 环境变量 'PRIVATE_REGISTRY' 或 'PRIVATE_REGISTRY_NAMESPACE' 未设置。", file=sys.stderr)
        sys.exit(1)

    source_dir = Path(source_dir_str)
    output_dir = Path(output_dir_str)
    
    # --- 2. 准备工作 ---
    output_dir.mkdir(parents=True, exist_ok=True)
    if not source_dir.is_dir():
        print(f"源目录 '{source_dir}' 不存在，无需处理。")
        # 即使目录不存在，也需要设置输出，以防工作流失败
        set_github_output("has_processed_files", "false")
        sys.exit(0)

    has_processed_files = False

    # --- 3. 核心循环 ---
    # 使用 .iterdir() 遍历目录中的所有条目
    for task_file_path in source_dir.iterdir():
        # 确保处理的是文件
        if not task_file_path.is_file():
            continue

        # 读取文件内容作为源镜像名，并去除首尾空白
        source_image = task_file_path.read_text(encoding='utf-8').strip()
        
        if not source_image:
            print(f"🟡 警告: 任务文件 '{task_file_path.name}' 为空，已跳过。")
            continue

        print("=" * 60)
        print(f"🔵 开始处理任务: {source_image}")
        image_parts = source_image.split('/')
        image_name_with_tag = image_parts[-1]
        destination_image = f"{private_registry}/{private_registry_namespace}/{image_name_with_tag}"
        # --- 4. Docker 操作 ---
        # 链式操作，任何一步失败则跳过当前任务
        print(f"   - 下载中: {source_image}")
        if not run_command(["docker", "pull", source_image]):
            print("   ❌ 错误: 拉取失败，任务将保留以待重试。")
            continue

        print(f"   - 重打标签: {destination_image}")
        if not run_command(["docker", "tag", source_image, destination_image]):
            print("   ❌ 错误: 标记失败，任务将保留。")
            continue

        print(f"   - [调试信息] 准备推送的完整镜像名是: {destination_image}")

        print(f"   - 推送中: {destination_image}")
        if not run_command(["docker", "push", destination_image]):
            print("   ❌ 错误: 推送失败，任务将保留。")
            continue

        # --- 5. 成功后处理 ---
        # 根据源镜像名生成一个安全的文件名 (e.g., library/ubuntu:22.04 -> library-ubuntu-22.04.txt)
        safe_filename = source_image.replace("/", "-").replace(":", "-") + ".txt"
        output_file_path = output_dir / safe_filename
        
        # 将拉取指令写入输出文件
        output_file_path.write_text(f"docker pull {destination_image}\n", encoding='utf-8')
        print(f"   - ✅ 指令已生成: {output_file_path}")

        # 删除已成功处理的源文件
        task_file_path.unlink()
        print(f"   - ✅ 任务文件已删除: {task_file_path}")

        has_processed_files = True

    # --- 6. 设置 GitHub Actions 输出 ---
    set_github_output("has_processed_files", str(has_processed_files).lower())
    print("=" * 60)
    print(f"处理完成。是否处理了文件: {has_processed_files}")


def set_github_output(name: str, value: str):
    """将键值对写入 GITHUB_OUTPUT 文件，供后续步骤使用。"""
    github_output_file = os.getenv("GITHUB_OUTPUT")
    if github_output_file:
        with open(github_output_file, "a") as f:
            f.write(f"{name}={value}\n")

if __name__ == "__main__":
    main()