#!/usr/bin/env python3
import os
import zipfile
from datetime import datetime
from pathlib import Path

# Pasta raiz do projeto Django (onde está manage.py)
PROJECT_ROOT = '.'

# Pasta onde o ZIP será gerado
OUTPUT_DIR = Path('tmp')
OUTPUT_DIR.mkdir(exist_ok=True)

# Apps e arquivos importantes que queremos incluir
INCLUDE_ITEMS = [
    'manage.py', 'config', 'chatbots', 'clientes', 'pedidos', 'tarefas',
    'integracoes', 'metricas', 'README.md', '.env.example',
    'start_services.sh', 'zip_project.py'
]

EXCLUDE_PATTERNS = [
    '__pycache__', '.pyc', '.pyo', '.git', 'attached_assets', 'uv.lock',
    'chatbot_whatsapp_', '.pytest_cache', '*.log', '*.pid', 'staticfiles',
    'media'
]


def should_exclude(path: Path):
    path_str = str(path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str:
            return True
    return False


def clean_temp_files():
    """Remove arquivos temporários dentro do projeto"""
    temp_patterns = ['__pycache__', '.pyc', '.pyo', '.pytest_cache']
    for pattern in temp_patterns:
        os.system(
            f'find {PROJECT_ROOT} -type d -name "{pattern}" -exec rm -rf {{}} + 2>/dev/null || true'
        )
        os.system(
            f'find {PROJECT_ROOT} -type f -name "*{pattern}" -delete 2>/dev/null || true'
        )
    os.system('rm -f /tmp/*.log /tmp/*.pid 2>/dev/null || true')


def create_zip():
    """Cria o arquivo ZIP com apenas os arquivos essenciais do projeto Django"""
    print("=== Empacotando projeto Django Chatbot WhatsApp ===\n")
    clean_temp_files()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = OUTPUT_DIR / f"chatbot_whatsapp_{timestamp}.zip"
    total_files = 0

    with zipfile.ZipFile(str(zip_filename), 'w', zipfile.ZIP_DEFLATED) as zipf:
        for item in INCLUDE_ITEMS:
            item_path = Path(PROJECT_ROOT) / item
            if not item_path.exists():
                continue

            if item_path.is_file():
                arcname = item
                info = zipfile.ZipInfo(arcname)
                info.date_time = datetime.now().timetuple()[:6]
                with open(item_path, 'rb') as f:
                    zipf.writestr(info,
                                  f.read(),
                                  compress_type=zipfile.ZIP_DEFLATED)
                total_files += 1

            elif item_path.is_dir():
                for root, dirs, files in os.walk(item_path):
                    dirs[:] = [
                        d for d in dirs if not should_exclude(Path(root) / d)
                    ]
                    for file in files:
                        filepath = Path(root) / file
                        if should_exclude(filepath):
                            continue
                        arcname = os.path.relpath(filepath, PROJECT_ROOT)
                        info = zipfile.ZipInfo(arcname)
                        info.date_time = datetime.now().timetuple()[:6]
                        with open(filepath, 'rb') as f:
                            zipf.writestr(info,
                                          f.read(),
                                          compress_type=zipfile.ZIP_DEFLATED)
                        total_files += 1
                        if total_files % 10 == 0:
                            print(f"  Adicionados {total_files} arquivos...",
                                  end='\r')

    file_size = os.path.getsize(zip_filename)
    size_mb = file_size / (1024 * 1024)
    print(f"\n\n✓ Projeto empacotado com sucesso!")
    print(f"Arquivo: {zip_filename.resolve()}")
    print(f"Tamanho: {size_mb:.2f} MB")
    print(f"Total de arquivos: {total_files}")


if __name__ == '__main__':
    create_zip()
