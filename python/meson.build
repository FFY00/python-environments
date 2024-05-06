py = import('python').find_installation()

py.install_sources(
    'python_environments/__init__.py',
    'python_environments/_init.py',
    'python_environments/generate.py',
    subdir: 'python_environments',
)

run_command(py, '-m', 'containers.build', check: false)

data_files = run_command(py, 'generate-data.py', '--list-files', check: true).stdout().strip().split(' ')
custom_target(
    'data',
    input: 'generate-data.py',
    output: data_files,
    command: [py, '@INPUT@', '--outdir', '@OUTDIR@'],
    install_dir: py.get_install_dir() / 'python_environments' / 'data',
    install: true,
)
