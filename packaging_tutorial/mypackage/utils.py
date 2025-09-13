import yaml
import importlib.resources
import pathlib
import sys

REQUIRED_KEYS = ["key"]  # ユーザが必ず定義しなければならないキー

def _load_config():
    # ユーザーカスタム (ホームディレクトリ)
    user_conf = pathlib.Path.home() / ".mypackage" / "conf.yaml"
    if user_conf.exists():
        with open(user_conf, "r", encoding="utf-8") as f:
            user_config = yaml.safe_load(f)
    else:
        print(f"ERROR: 必須設定ファイルが見つかりません: {user_conf}")
        sys.exit(1)

    # デフォルト設定（パッケージ同梱）
    with importlib.resources.open_text("mypackage", "conf.yaml", encoding="utf-8") as f:
        default_config = yaml.safe_load(f)

    # デフォルトにユーザ設定をマージ（ユーザが優先）
    merged = {**default_config, **user_config}

    # 必須キーのチェック
    missing = [k for k in REQUIRED_KEYS if k not in user_config]
    if missing:
        print(f"ERROR: 必須キーが conf.yaml にありません: {missing}")
        sys.exit(1)

    return merged

# 設定をロード
config = _load_config()

def hello(name: str = None) -> str:
    if name is None:
        name = config.get("default_name", "User")
    greeting = config.get("greeting", "Hello")
    key = config["key"]  # ユーザ必須
    return f"{greeting}, {name}! (key={key})"

