py = import('python').find_installation()

py.install_sources(
    'python_environments/__init__.py',
    'python_environments/_init.py',
    'python_environments/generate.py',
    subdir: 'python_environments',
)

build_containers_command = [py, '-m', 'containers.build']
if get_option('push_containers')
    build_containers_command += ['--push']
endif
build_containers_command += ['--build-path', meson.source_root() / get_option('containers_build_path')]

generate_data_deps = []
if get_option('build_containers')
    build_containers_target = custom_target(
        'build-containers',
        output: 'dummy',
        command: build_containers_command,
        env: {
            'PYTHONPATH': meson.source_root(),
        },
        console: true,
    )
    generate_data_deps += [build_containers_target]
endif

data_files = run_command(py, 'generate-data.py', '--list-files', check: true).stdout().strip().split(' ')
custom_target(
    'data',
    input: 'generate-data.py',
    output: data_files,
    command: [py, '@INPUT@', '--outdir', '@OUTDIR@'],
    install_dir: py.get_install_dir() / 'python_environments' / 'data',
    install: true,
    depends: generate_data_deps,
)
