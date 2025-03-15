# Сборка SQLite в виде динамической библиотеки

# Автор Баймухамедов Рафаэль Русланович

Этот проект позволяет собрать SQLite в виде динамической библиотеки (`.dll` для Windows и `.so` для Linux) с использованием CMake и Docker

## Сборка под Windows (DLL)

### (Требования) Установите зависимости

-   [CMake](https://cmake.org/download/)
-   [Visual Studio 17 2022](https://visualstudio.microsoft.com/) с компонентом "C++ Build Tools"

### Создайте файл CMakeLists.txt со следующих содержимым

```
cmake_minimum_required(VERSION 3.10)
project(sqlite-dll LANGUAGES C)

# Настройка для DLL
add_library(sqlite SHARED
    sqlite-src/sqlite-amalgamation-3260000/sqlite3.c
    sqlite-src/sqlite-amalgamation-3260000/sqlite3.h
)

set_target_properties(sqlite PROPERTIES
    WINDOWS_EXPORT_ALL_SYMBOLS TRUE
    OUTPUT_NAME "sqlite3" # Убираем "lib" из названия
    PREFIX "" # Убираем префикс "lib"
)

# Установка библиотеки
install(TARGETS sqlite
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)

```

### Перейдите в Windows PowerShell в папку проекта

Пропишите следующие строки в консоль

```
# Скачивание и распаковка архива
Invoke-WebRequest -Uri "https://www.sqlite.org/2018/sqlite-amalgamation-3260000.zip" -OutFile "sqlite-amalgamation-3260000.zip"

Expand-Archive -Path "sqlite-amalgamation-3260000.zip" -DestinationPath "sqlite-src"

# Создание директории сборки
mkdir build
cd build

# Определяем архитектуру системы
$architecture = if ([Environment]::Is64BitOperatingSystem) { "x64" } else { "Win32" }

# Простое определение версии Visual Studio
$vsVersions = @(
    "Visual Studio 17 2022", # Visual Studio 2022
    "Visual Studio 16 2019", # Visual Studio 2019
    "Visual Studio 15 2017"  # Visual Studio 2017
)
$vsVersion = $null
foreach ($version in $vsVersions) {
    $year = $version -replace "Visual Studio \d+ (\d+)", '$1'
    $path = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\$year\BuildTools\MSBuild\Current\Bin\MSBuild.exe"
    if (Test-Path $path) {
        $vsVersion = $version
        break
    }
}

if (-not $vsVersion) {
    Write-Error "Visual Studio не найдена. Установите Visual Studio (2017, 2019 или 2022) или укажите версию вручную в команде cmake."
    Write-Host "Пример для Visual Studio 2022: cmake .. -G 'Visual Studio 17 2022' -A $architecture"
    exit 1
}

# Выполняем команды CMake с найденной версией Visual Studio
cmake .. -G "$vsVersion" -A $architecture
cmake --build . --config Release
echo "Сборка успешно завершена"

```

Файл sqlite3.dll будет находиться в ./build/Release/

## Сборка под Linux (.so)

### (Требования) Установите зависимости

-   [CMake](https://cmake.org/download/)
-   [Docker](https://www.docker.com/get-started/)

### Создайте файл CMakeLists.txt со следующих содержимым

```
cmake_minimum_required(VERSION 3.10)
project(sqlite-dll LANGUAGES C)

# Настройка для DLL
add_library(sqlite SHARED
    sqlite-src/sqlite-amalgamation-3260000/sqlite3.c
    sqlite-src/sqlite-amalgamation-3260000/sqlite3.h
)

set_target_properties(sqlite PROPERTIES
    WINDOWS_EXPORT_ALL_SYMBOLS TRUE
    OUTPUT_NAME "sqlite3" # Убираем "lib" из названия
    PREFIX "" # Убираем префикс "lib"
)

# Установка библиотеки
install(TARGETS sqlite
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)

```

### Запустите Docker Desktop и создайте файл Dockerfile со следующим сожержимым

```
FROM debian:latest
RUN apt-get update && apt-get install -y \
    gcc \
    cmake \
    make \
    wget \
    unzip

WORKDIR /app

RUN wget https://www.sqlite.org/2018/sqlite-amalgamation-3260000.zip \
    && unzip sqlite-amalgamation-3260000.zip \
    && mkdir -p sqlite-src \
    && mv sqlite-amalgamation-3260000 sqlite-src/sqlite-amalgamation-3260000 \
    && rm sqlite-amalgamation-3260000.zip

COPY CMakeLists.txt /app/

RUN mkdir build
RUN mkdir output

WORKDIR /app/build
RUN cmake .. && make

CMD ["cp", "sqlite3.so", "/output/"]
```

### Перейдите в Terminal и пропишите следующие строки в консоль

```
docker build -t sqlite-builder .
docker run --rm -v "$PWD\output:/output" sqlite-builder

```

Файл sqlite3.so будет находится в ./output/

## Развёртывание виртуальной машины с операционной системой GNU/LINUX и дистрибутивом Centos 7 при помощи Vagrant (без сборки sqlite3)

### (Требования) Установите зависимости

-   [VirtualBox 7.1.6] (https://www.virtualbox.org/wiki/Downloads)
-   [Vagrant 2.4.3](https://developer.hashicorp.com/vagrant/install)

### Создать файл Vagrantfile с следующим содержимым

```
Vagrant.configure("2") do |config|
  config.vm.box = "centos/7"

  config.vm.provider "virtualbox" do |vb|
    vb.name = "centos7_vm"
    vb.memory = "4096"
    vb.cpus = 4
  end

  # Синхронизация локальной папки с Vagrant
  config.vm.synced_folder ".", "/vagrant"
end
```

### Команды в терминале (консоли) для работы с ВМ

vagrant up — создать и запустить виртуальную машину
vagrant halt — выключить виртуальную машину
vagrant suspend — приостановить ВМ (сохранить состояние)
vagrant resume — возобновить приостановленную ВМ
vagrant destroy — удалить виртуальную машину и все её файлы
vagrant ssh — подключиться к ВМ по SSH
vagrant status — показать статус ВМ

## Развёртывание виртуальной машины с операционной системой GNU/LINUX и дистрибутивом Centos 7 при помощи Vagrant и установкой на ВМ - Docker, но без процесса сборки sqlite

### (Требования) Установите зависимости

-   [VirtualBox 7.1.6] (https://www.virtualbox.org/wiki/Downloads)
-   [Vagrant 2.4.3](https://developer.hashicorp.com/vagrant/install)

### Создать файл Vagrantfile с следующим содержимым

```
Vagrant.configure("2") do |config|
  config.vm.box = "centos/7"

  config.vm.provider "virtualbox" do |vb|
    vb.name = "centos7_vm"
    vb.memory = "4096"
    vb.cpus = 4
  end

  # Синхронизация локальной папки с Vagrant
  config.vm.synced_folder ".", "/vagrant"

  # Устанавливаем Ansible
  config.vm.provision "shell", inline: <<-SHELL
    sudo sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*.repo
    sudo sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*.repo
    sudo yum install -y https://archives.fedoraproject.org/pub/archive/epel/7/x86_64/Packages/e/epel-release-7-14.noarch.rpm
    sudo yum install -y ansible
  SHELL

  # Используем Ansible для установки Docker
  config.vm.provision "ansible_local" do |ansible|
    ansible.playbook = "install_docker.yml"
    ansible.install = false
    ansible.compatibility_mode = "2.0"
  end
end

```

### Создать файл install_docker.yml с следующим содержимым

```
---
- hosts: all
  become: yes
  tasks:
      - name: Install necessary packages
        yum:
            name:
                - yum-utils
                - device-mapper-persistent-data
                - lvm2
            state: present

      - name: Download Docker CE repository file
        get_url:
            url: https://download.docker.com/linux/centos/docker-ce.repo
            dest: /etc/yum.repos.d/docker-ce.repo

      - name: Install Docker CE
        yum:
            name: docker-ce
            state: present

      - name: Start and enable Docker service
        service:
            name: docker
            state: started
            enabled: yes

      - name: Add vagrant user to docker group
        user:
            name: vagrant
            groups: docker
            append: yes

```

### Команды в терминале (консоли) для работы с ВМ

vagrant up — создать и запустить виртуальную машину
vagrant halt — выключить виртуальную машину
vagrant suspend — приостановить ВМ (сохранить состояние)
vagrant resume — возобновить приостановленную ВМ
vagrant destroy — удалить виртуальную машину и все её файлы
vagrant ssh — подключиться к ВМ по SSH
vagrant status — показать статус ВМ

## Развёртывание виртуальной машины c операционной системой GNU/Linux и дистрибутивом Centos 7 при помощи Vagrant и сборкой sqlite3

### (Требования) Установите зависимости

-   [VirtualBox 7.1.6] (https://www.virtualbox.org/wiki/Downloads)
-   [Vagrant 2.4.3](https://developer.hashicorp.com/vagrant/install)

### Создать файл Vagrantfile с следующим содержимым

```
Vagrant.configure("2") do |config|
  config.vm.box = "centos/7"

  config.vm.provider "virtualbox" do |vb|
    vb.name = "centos7_vm"
    vb.memory = "4096"
    vb.cpus = 4
  end

  # Синхронизация локальной папки с Vagrant
  config.vm.synced_folder ".", "/vagrant"

  # Устанавливаем Ansible и Docker
  config.vm.provision "shell", inline: <<-SHELL
    sudo sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*.repo
    sudo sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*.repo
    sudo yum install -y https://archives.fedoraproject.org/pub/archive/epel/7/x86_64/Packages/e/epel-release-7-14.noarch.rpm
    sudo yum install -y ansible
  SHELL

  # Используем Ansible для установки Docker
  config.vm.provision "ansible_local" do |ansible|
    ansible.playbook = "install_docker.yml"
    ansible.install = false
    ansible.compatibility_mode = "2.0"
  end

  # Запуск Docker контейнера для сборки проекта
  config.vm.provision "shell", inline: <<-SHELL
    cd /vagrant
    sudo docker build -t sqlite-builder .
    sudo docker run --rm -v /vagrant/output:/output sqlite-builder
    ls -l /vagrant/output
  SHELL
end

```

### Создать файл install_docker.yml с следующим содержимым

```
---
- hosts: all
  become: yes
  tasks:
      - name: Install necessary packages
        yum:
            name:
                - yum-utils
                - device-mapper-persistent-data
                - lvm2
            state: present

      - name: Download Docker CE repository file
        get_url:
            url: https://download.docker.com/linux/centos/docker-ce.repo
            dest: /etc/yum.repos.d/docker-ce.repo

      - name: Install Docker CE
        yum:
            name: docker-ce
            state: present

      - name: Start and enable Docker service
        service:
            name: docker
            state: started
            enabled: yes

      - name: Add vagrant user to docker group
        user:
            name: vagrant
            groups: docker
            append: yes

```

### Создайте файл CMakeLists.txt со следующих содержимым

```
cmake_minimum_required(VERSION 3.10)
project(sqlite-dll LANGUAGES C)

# Настройка для DLL
add_library(sqlite SHARED
    sqlite-src/sqlite-amalgamation-3260000/sqlite3.c
    sqlite-src/sqlite-amalgamation-3260000/sqlite3.h
)

set_target_properties(sqlite PROPERTIES
    WINDOWS_EXPORT_ALL_SYMBOLS TRUE
    OUTPUT_NAME "sqlite3" # Убираем "lib" из названия
    PREFIX "" # Убираем префикс "lib"
)

# Установка библиотеки
install(TARGETS sqlite
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)

```

### Запустите Docker Desktop и создайте файл Dockerfile со следующим сожержимым

```
FROM debian:latest
RUN apt-get update && apt-get install -y \
    gcc \
    cmake \
    make \
    wget \
    unzip

WORKDIR /app

RUN wget https://www.sqlite.org/2018/sqlite-amalgamation-3260000.zip \
    && unzip sqlite-amalgamation-3260000.zip \
    && mkdir -p sqlite-src \
    && mv sqlite-amalgamation-3260000 sqlite-src/sqlite-amalgamation-3260000 \
    && rm sqlite-amalgamation-3260000.zip

COPY CMakeLists.txt /app/

RUN mkdir build
RUN mkdir output

WORKDIR /app/build
RUN cmake .. && make

CMD ["cp", "sqlite3.so", "/output/"]
```

### Прописать в терминале в папке проекта

```
# Запустите развёртывание ВМ и сборку на ней
vagrant up

# Дождитесь развёртывания и сборки sqlite3

# Подключитесь к ВМ
vagrant ssh

cd /vagrant/output/

В текущей папке будет находиться sqlite3.so
```

### Команды в терминале (консоли) для работы с ВМ

vagrant up — создать и запустить виртуальную машину
vagrant halt — выключить виртуальную машину
vagrant suspend — приостановить ВМ (сохранить состояние)
vagrant resume — возобновить приостановленную ВМ
vagrant destroy — удалить виртуальную машину и все её файлы
vagrant ssh — подключиться к ВМ по SSH
vagrant status — показать статус ВМ

### Результат

В результате развёртывания виртуальной машины, на ней в папке /vagrant/output/ будет находиться файл sqlite3.so
