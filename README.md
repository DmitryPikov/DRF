1. Войдите в терминал удаленной виртуальной машины:
    ```
    ssh user@ip_adress
    ```
   где user - пользователь системы, ip_adress - IP адресс вашего сервера.
2. Откройте терминал и выполните команду для обновления списка пакетов:
    ```
    sudo apt update
    ```
3. Затем выполните команду для обновления всех установленных пакетов до их последних версий:
    ```
    sudo apt upgrade
    ```
4. Сначала проверьте состояние файрвола с помощью команды:
    ```
    sudo ufw status
    ```
5. Если файрвол отключен, активируйте его:
    ```
    sudo ufw enable
    ```
6. Теперь откройте необходимые порты:
   - Порт 80 для HTTP:
   ```
   sudo ufw allow 80/tcp
   ```
   - Порт 443 для HTTPS:
   ```
   sudo ufw allow 443/tcp
   ```
   - Порт 22 для SSH:
   ```
   sudo ufw allow 22/tcp
   ```
   - Проверьте настройки файрвола:
   ```
   sudo ufw status
   ```
   - В результате выполнения команды вы должны увидеть, что порт 22 находится в состоянии ALLOW наряду с портами 80 и 443. Это означает, что ваш сервер будет доступен для SSH-подключений, а также для веб-трафика.
7. Установка Docker на удаленный сервер:
- ```
    sudo apt update
  ```
- ```
    sudo apt install ca-certificates curl
  ```
- ```
    sudo install -m 0755 -d /etc/apt/keyrings
  ```
- ```
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  ```
- ```
    sudo chmod a+r /etc/apt/keyrings/docker.asc
  ```
- ```
  sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
  Types: deb
  URIs: https://download.docker.com/linux/ubuntu
  Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
  Components: stable
  Signed-By: /etc/apt/keyrings/docker.asc
  EOF
  ```
- ```
    sudo apt update
  ```
- ```
    sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  ```